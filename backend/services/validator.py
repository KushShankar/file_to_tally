"""
Data validation service
"""
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Tuple
import logging
import re

logger = logging.getLogger(__name__)


class DataValidator:
    """Validate and clean data before sending to Tally"""
    
    @staticmethod
    def validate_date(date_value: Any) -> Tuple[bool, str, str]:
        """
        Validate and convert date to Tally format (YYYYMMDD)
        
        Returns:
            Tuple of (is_valid, formatted_date, error_message)
        """
        if pd.isna(date_value) or date_value == '':
            return False, '', 'Date is empty'
        
        try:
            # Convert to string first
            date_str = str(date_value).strip()
            
            # Try various date formats
            date_formats = [
                '%d-%m-%Y',
                '%d/%m/%Y',
                '%Y-%m-%d',
                '%Y/%m/%d',
                '%d.%m.%Y',
                '%m-%d-%Y',
                '%m/%d/%Y',
                '%d-%b-%Y',
                '%d %b %Y',
                '%d-%B-%Y',
            ]
            
            parsed_date = None
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    break
                except ValueError:
                    continue
            
            # If still not parsed, try pandas
            if not parsed_date:
                parsed_date = pd.to_datetime(date_str, errors='coerce')
                if pd.isna(parsed_date):
                    return False, '', f'Invalid date format: {date_str}'
            
            # Format for Tally (YYYYMMDD)
            formatted = parsed_date.strftime('%Y%m%d')
            return True, formatted, ''
            
        except Exception as e:
            return False, '', f'Date validation error: {str(e)}'
    
    @staticmethod
    def validate_amount(amount_value: Any) -> Tuple[bool, float, str]:
        """
        Validate and convert amount to float
        
        Returns:
            Tuple of (is_valid, amount, error_message)
        """
        if pd.isna(amount_value) or amount_value == '':
            return False, 0.0, 'Amount is empty'
        
        try:
            # Convert to string and clean
            amount_str = str(amount_value).strip()
            
            # Remove currency symbols and commas
            amount_str = re.sub(r'[₹$,\s]', '', amount_str)
            
            # Convert to float
            amount = float(amount_str)
            
            # Check if positive
            if amount <= 0:
                return False, 0.0, 'Amount must be positive'
            
            # Round to 2 decimal places
            amount = round(amount, 2)
            
            return True, amount, ''
            
        except ValueError:
            return False, 0.0, f'Invalid amount format: {amount_value}'
        except Exception as e:
            return False, 0.0, f'Amount validation error: {str(e)}'
    
    @staticmethod
    def validate_text(text_value: Any, field_name: str, required: bool = True) -> Tuple[bool, str, str]:
        """
        Validate text field
        
        Returns:
            Tuple of (is_valid, cleaned_text, error_message)
        """
        if pd.isna(text_value) or text_value == '':
            if required:
                return False, '', f'{field_name} is required'
            else:
                return True, '', ''
        
        try:
            # Convert to string and clean
            text = str(text_value).strip()
            
            # Remove special characters that might break XML
            text = re.sub(r'[<>&"]', '', text)
            
            # Limit length
            if len(text) > 255:
                text = text[:255]
            
            return True, text, ''
            
        except Exception as e:
            return False, '', f'{field_name} validation error: {str(e)}'
    
    @staticmethod
    def sanitize_ledger_name(ledger_name: str) -> str:
        """
        Sanitize ledger name for Tally
        """
        if not ledger_name:
            return ''
        
        # Remove special characters
        sanitized = re.sub(r'[<>&"]', '', ledger_name.strip())
        
        # Replace multiple spaces with single space
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        return sanitized
    
    @staticmethod
    def validate_voucher_entry(
        row: Dict[str, Any],
        mappings: Dict[str, str],
        voucher_type: str
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        Validate a complete voucher entry
        
        Args:
            row: Dictionary of row data
            mappings: Column mappings (Excel column -> Tally field)
            voucher_type: Type of voucher
        
        Returns:
            Tuple of (is_valid, validated_data, error_message)
        """
        validated = {}
        errors = []
        
        # Reverse mappings to get Excel column for each Tally field
        reverse_mappings = {v: k for k, v in mappings.items()}
        
        # Validate date (required)
        if 'date' in reverse_mappings:
            date_col = reverse_mappings['date']
            is_valid, date_val, error = DataValidator.validate_date(row.get(date_col))
            if not is_valid:
                errors.append(f"Date: {error}")
            else:
                validated['date'] = date_val
        else:
            errors.append("Date field not mapped")
        
        # Validate party name (required)
        if 'party_name' in reverse_mappings:
            party_col = reverse_mappings['party_name']
            is_valid, party_val, error = DataValidator.validate_text(
                row.get(party_col), 'Party Name', required=True
            )
            if not is_valid:
                errors.append(f"Party Name: {error}")
            else:
                validated['party_name'] = DataValidator.sanitize_ledger_name(party_val)
        else:
            errors.append("Party Name field not mapped")
        
        # Validate amount (required)
        if 'amount' in reverse_mappings:
            amount_col = reverse_mappings['amount']
            is_valid, amount_val, error = DataValidator.validate_amount(row.get(amount_col))
            if not is_valid:
                errors.append(f"Amount: {error}")
            else:
                validated['amount'] = amount_val
        else:
            errors.append("Amount field not mapped")
        
        # Validate optional fields
        optional_fields = [
            'invoice_no', 'narration', 'sales_ledger', 'purchase_ledger',
            'item_name', 'quantity', 'rate', 'contra_ledger',
            'taxable_value', 'igst', 'cgst', 'sgst', 'gst_number'
        ]
        
        for field in optional_fields:
            if field in reverse_mappings:
                col = reverse_mappings[field]
                value = row.get(col)
                
                if field in ['quantity', 'rate', 'taxable_value', 'igst', 'cgst', 'sgst']:
                    # Numeric validation
                    is_valid, num_val, error = DataValidator.validate_amount(value)
                    if is_valid:
                        validated[field] = num_val
                elif field == 'gst_number':
                    # GST number validation (15 characters alphanumeric)
                    is_valid, text_val, error = DataValidator.validate_text(
                        value, 'GST Number', required=False
                    )
                    if is_valid and text_val:
                        # Basic GST number format validation (15 chars)
                        gst_clean = text_val.strip().upper()
                        if len(gst_clean) == 15:
                            validated[field] = gst_clean
                else:
                    # Text validation
                    is_valid, text_val, error = DataValidator.validate_text(
                        value, field.replace('_', ' ').title(), required=False
                    )
                    if is_valid and text_val:
                        if 'ledger' in field:
                            validated[field] = DataValidator.sanitize_ledger_name(text_val)
                        else:
                            validated[field] = text_val
        
        # Add voucher type
        validated['voucher_type'] = voucher_type
        
        if errors:
            return False, validated, '; '.join(errors)
        
        return True, validated, ''
