"""
API Routes for file upload and processing
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import logging
from typing import Dict, Any

from config import UPLOAD_DIR, ALLOWED_EXTENSIONS, TALLY_COMPANY
from models.schemas import UploadResponse, ProcessRequest, ProcessResponse, ColumnMapping
from services import ExcelParser, AIMapper, DataValidator, TallyXMLGenerator, TallyClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["upload"])

# Initialize services
excel_parser = ExcelParser()
ai_mapper = AIMapper()
tally_client = TallyClient()
xml_generator = TallyXMLGenerator(company_name=TALLY_COMPANY)


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload Excel file and get column analysis with AI-suggested mappings
    """
    try:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"File uploaded: {file.filename}")
        
        # Parse Excel file
        columns, sample_data, row_count = excel_parser.parse_file(file_path)
        
        # Get AI-suggested mappings
        ai_mappings = ai_mapper.suggest_mappings(columns)
        
        # Convert to response format
        suggested_mappings = [
            ColumnMapping(
                excel_column=col,
                tally_field=mapping["tally_field"],
                confidence=mapping["confidence"]
            )
            for col, mapping in ai_mappings.items()
        ]
        
        return UploadResponse(
            filename=file.filename,
            columns=columns,
            sample_data=sample_data,
            suggested_mappings=suggested_mappings,
            row_count=row_count
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/process", response_model=ProcessResponse)
async def process_file(request: ProcessRequest):
    """
    Process Excel file and send vouchers to Tally
    """
    try:
        file_path = UPLOAD_DIR / request.filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Create Tally client with the selected company
        company_tally_client = TallyClient(company_name=request.company_name)
        company_xml_generator = TallyXMLGenerator(company_name=request.company_name)
        
        # Read all data
        df = excel_parser.read_all_data(file_path)
        
        success_count = 0
        failed_count = 0
        errors = []
        ledgers_created = []
        
        # Ensure standard ledgers exist
        if request.create_missing_ledgers:
            ledger_to_check = None
            parent_group = None
            
            if request.voucher_type.lower() == "sales":
                ledger_to_check = "Sales"
                parent_group = "Sales Accounts"
            elif request.voucher_type.lower() == "contra":
                # For Contra, usually involves Bank/Cash
                # We'll assume the 'party_name' is a Bank ledger if we need to create it
                ledger_to_check = None # No standard ledger like 'Sales' to check
                
                # We can check specific contra ledger if provided
                # But 'process_file' loop handles the 'party_name' ledger creation below
                pass

            if ledger_to_check and not company_tally_client.ledger_exists(ledger_to_check):
                logger.info(f"Creating missing standard ledger: {ledger_to_check}")
                # Use standard logic for ledger creation
                ledger_xml = company_xml_generator.generate_ledger_xml(ledger_to_check, parent_group)
                success, msg = company_tally_client.send_xml(ledger_xml)
                if success:
                    logger.info(f"Successfully created standard ledger: {ledger_to_check}")
                else:
                    logger.warning(f"Failed to create standard ledger {ledger_to_check}: {msg}")
            
            # Create GST ledgers if they don't exist
            gst_ledgers = [
                ("Cgst", "Duties & Taxes"),
                ("Sgst", "Duties & Taxes"),
                ("Igst", "Duties & Taxes"),
            ]
            
            for ledger_name, parent in gst_ledgers:
                if not company_tally_client.ledger_exists(ledger_name):
                    logger.info(f"Creating GST ledger: {ledger_name}")
                    ledger_xml = company_xml_generator.generate_ledger_xml(ledger_name, parent)
                    success, msg = company_tally_client.send_xml(ledger_xml)
                    if success:
                        logger.info(f"Successfully created GST ledger: {ledger_name}")
                    else:
                        logger.warning(f"Failed to create GST ledger {ledger_name}: {msg}")

        # Process each row
        for idx, row in df.iterrows():
            row_dict = row.to_dict()
            
            # Validate row
            is_valid, validated_data, error_msg = DataValidator.validate_voucher_entry(
                row_dict,
                request.mappings,
                request.voucher_type
            )
            
            if not is_valid:
                failed_count += 1
                analysis = _analyze_error(error_msg)
                errors.append({
                    "row_number": idx + 2,  # +2 for header and 0-indexing
                    "data": {k: str(v) for k, v in row_dict.items()},
                    "error": error_msg,
                    "reason": analysis["reason"],
                    "solution": analysis["solution"]
                })
                continue
            
            # Check if party ledger exists
            party_name = validated_data.get('party_name')
            if party_name and request.create_missing_ledgers:
                if not company_tally_client.ledger_exists(party_name):
                    # Determine parent group based on voucher type
                    parent = "Sundry Debtors" # Default
                    v_type = request.voucher_type.lower()
                    
                    if v_type == "sales":
                        parent = "Sundry Debtors"
                    elif v_type == "purchase":
                        parent = "Sundry Creditors"
                    elif v_type == "contra":
                        parent = "Bank Accounts" # Assume new ledger in Contra is a Bank
                    elif v_type == "payment":
                        parent = "Sundry Creditors"
                    elif v_type == "receipt":
                        parent = "Sundry Debtors"
                    
                    # Create ledger
                    ledger_xml = company_xml_generator.generate_ledger_xml(party_name, parent)
                    success, msg = company_tally_client.send_xml(ledger_xml)
                    
                    if success:
                        ledgers_created.append(party_name)
                        logger.info(f"Created ledger: {party_name}")
                    else:
                        logger.warning(f"Failed to create ledger {party_name}: {msg}")
            
            # Generate voucher XML based on type
            voucher_xml = _generate_voucher_xml(
                request.voucher_type,
                validated_data,
                company_xml_generator
            )
            
            # Send to Tally
            success, msg = company_tally_client.send_xml(voucher_xml)
            
            if success:
                success_count += 1
            else:
                failed_count += 1
                analysis = _analyze_error(msg)
                errors.append({
                    "row_number": idx + 2,
                    "data": {k: str(v) for k, v in row_dict.items()},
                    "error": f"Tally error: {msg}",
                    "reason": analysis["reason"],
                    "solution": analysis["solution"]
                })
        
        message = f"Processed {success_count + failed_count} entries. {success_count} successful, {failed_count} failed."
        
        return ProcessResponse(
            success_count=success_count,
            failed_count=failed_count,
            errors=errors,
            ledgers_created=ledgers_created,
            message=message
        )
        
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


def _generate_voucher_xml(voucher_type: str, data: Dict[str, Any], generator: TallyXMLGenerator) -> str:
    """
    Generate appropriate XML based on voucher type
    """
    voucher_type = voucher_type.lower()
    
    if voucher_type == "sales":
        return generator.generate_sales_voucher_xml(
            date=data['date'],
            party_name=data['party_name'],
            amount=data['amount'],
            sales_ledger=data.get('sales_ledger', 'Sales'),
            invoice_no=data.get('invoice_no'),
            narration=data.get('narration'),
            taxable_value=data.get('taxable_value'),
            igst=data.get('igst'),
            cgst=data.get('cgst'),
            sgst=data.get('sgst'),
            gst_number=data.get('gst_number')
        )
    
    elif voucher_type == "purchase":
        return generator.generate_purchase_voucher_xml(
            date=data['date'],
            party_name=data['party_name'],
            amount=data['amount'],
            purchase_ledger=data.get('purchase_ledger', 'Purchase'),
            invoice_no=data.get('invoice_no'),
            narration=data.get('narration')
        )
    
    elif voucher_type == "payment":
        return generator.generate_payment_voucher_xml(
            date=data['date'],
            party_name=data['party_name'],
            amount=data['amount'],
            payment_mode=data.get('payment_mode', 'Cash'),
            invoice_no=data.get('invoice_no'),
            narration=data.get('narration')
        )
    
    elif voucher_type == "receipt":
        return generator.generate_receipt_voucher_xml(
            date=data['date'],
            party_name=data['party_name'],
            amount=data['amount'],
            receipt_mode=data.get('receipt_mode', 'Cash'),
            invoice_no=data.get('invoice_no'),
            narration=data.get('narration')
        )
    
    elif voucher_type == "journal":
        return generator.generate_journal_voucher_xml(
            date=data['date'],
            debit_ledger=data.get('debit_ledger', data['party_name']),
            credit_ledger=data.get('credit_ledger', 'Cash'),
            amount=data['amount'],
            invoice_no=data.get('invoice_no'),
            narration=data.get('narration')
        )
    
    elif voucher_type == "contra":
        return generator.generate_contra_voucher_xml(
            date=data['date'],
            debit_ledger=data['party_name'],  # Target (e.g. Bank)
            credit_ledger=data.get('contra_ledger', 'Cash'), # Source
            amount=data['amount'],
            invoice_no=data.get('invoice_no'),
            narration=data.get('narration')
        )
    
    else:
        raise ValueError(f"Unsupported voucher type: {voucher_type}")


def _analyze_error(error_msg: str) -> Dict[str, str]:
    """
    Analyze error message and provide reason/solution
    """
    error = error_msg.lower()
    
    if "date" in error and "does not exist" in error:
        return {
            "reason": "The date provided is outside the current financial period of the Tally company.",
            "solution": "1. Change the date in your Excel file to be within the current financial year.<br>2. Or, change the 'Current Period' in Tally (Gateway of Tally > Alt+F2)."
        }
    
    elif "ledger" in error and "does not exist" in error:
        # Extract ledger name if possible
        return {
            "reason": "The ledger name specified in your data does not exist in Tally.",
            "solution": "1. Check for spelling mistakes.<br>2. Enable 'Automatically create missing ledgers'.<br>3. Create the ledger manually in Tally."
        }
        
    elif "amount" in error:
        return {
            "reason": "The amount contains invalid characters or format.",
            "solution": "Ensure the amount column contains only numbers. Remove currency symbols or commas."
        }
        
    elif "party name" in error:
         return {
            "reason": "The Party Name is missing or invalid.",
            "solution": "Ensure the Party Name column is mapped and contains data."
        }
    
    return {
        "reason": "Tally rejected the data for an unspecified reason.",
        "solution": "Check the data format and Tally status."
    }


@router.get("/companies")
async def get_companies():
    """
    Get all companies from Tally
    """
    try:
        success, companies, error = tally_client.get_companies()
        
        if success:
            return {"companies": companies}
        else:
            # If we can't get companies, return empty list
            logger.warning(f"Could not fetch companies: {error}")
            return {"companies": []}
            
    except Exception as e:
        logger.error(f"Error fetching companies: {str(e)}")
        return {"companies": []}


@router.get("/ledgers")
async def get_ledgers(company: str = None):
    """
    Get all ledgers from Tally for a specific company
    """
    try:
        # Create client with specific company if provided
        client = TallyClient(company_name=company) if company else tally_client
        success, ledgers, error = client.get_ledgers()
        
        if success:
            return {"ledgers": ledgers}
        else:
            raise HTTPException(status_code=500, detail=error)
            
    except Exception as e:
        logger.error(f"Error fetching ledgers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check(company: str = None):
    """
    Check Tally connection and system health
    """
    # Use provided company or default
    company_name = company if company else TALLY_COMPANY
    client = TallyClient(company_name=company_name)
    tally_connected, message = client.check_connection()
    
    return {
        "status": "healthy" if tally_connected else "degraded",
        "tally_connected": tally_connected,
        "tally_company": company_name,
        "message": message
    }
