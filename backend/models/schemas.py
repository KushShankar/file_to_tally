"""
Pydantic models for request/response validation
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ColumnMapping(BaseModel):
    """Column mapping from Excel to Tally fields"""
    excel_column: str
    tally_field: str
    confidence: float = Field(ge=0.0, le=1.0)


class UploadResponse(BaseModel):
    """Response after file upload"""
    filename: str
    columns: List[str]
    sample_data: List[Dict[str, Any]]
    suggested_mappings: List[ColumnMapping]
    row_count: int


class ProcessRequest(BaseModel):
    """Request to process Excel file"""
    filename: str
    voucher_type: str
    mappings: Dict[str, str]  # Excel column -> Tally field
    create_missing_ledgers: bool = True
    company_name: str = "Vrhealthy"  # Tally company name


class VoucherEntry(BaseModel):
    """Single voucher entry"""
    date: str
    party_name: str
    amount: float
    voucher_type: str
    invoice_no: Optional[str] = None
    narration: Optional[str] = None
    sales_ledger: Optional[str] = None
    purchase_ledger: Optional[str] = None
    item_name: Optional[str] = None
    quantity: Optional[float] = None
    rate: Optional[float] = None
    contra_ledger: Optional[str] = None
    # GST fields
    taxable_value: Optional[float] = None
    igst: Optional[float] = None
    cgst: Optional[float] = None
    sgst: Optional[float] = None
    gst_number: Optional[str] = None


class ProcessingError(BaseModel):
    """Error details for failed entry"""
    row_number: int
    data: Dict[str, Any]
    error: str
    reason: Optional[str] = None
    solution: Optional[str] = None


class ProcessResponse(BaseModel):
    """Response after processing"""
    success_count: int
    failed_count: int
    errors: List[ProcessingError]
    ledgers_created: List[str]
    message: str


class LedgerInfo(BaseModel):
    """Ledger information"""
    name: str
    parent: str = "Sundry Debtors"
    

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    tally_connected: bool
    tally_company: str
    message: str
