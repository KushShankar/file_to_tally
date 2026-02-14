"""
Configuration settings for Tally Agent
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Tally Configuration
TALLY_URL = os.getenv("TALLY_URL", "http://localhost:9000")
TALLY_COMPANY = os.getenv("TALLY_COMPANY", "TallyHealth")

# OpenRouter AI Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
AI_MODEL = "google/gemini-2.0-flash-exp:free"  # Using free Gemini model via OpenRouter

# File Upload Configuration
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Supported file extensions
ALLOWED_EXTENSIONS = {".xlsx", ".xls", ".csv"}

# Tally Field Mappings
TALLY_FIELDS = {
    "date": ["date", "invoice date", "voucher date", "entry date", "transaction date"],
    "party_name": ["party name", "party", "customer", "customer name", "vendor", "supplier", "account"],
    "amount": ["amount", "total", "total amount", "value", "invoice amount", "total invoice"],
    "voucher_type": ["voucher type", "type", "transaction type"],
    "invoice_no": ["invoice no", "invoice number", "bill no", "voucher no", "ref no"],
    "narration": ["narration", "description", "remarks", "details", "particulars"],
    "sales_ledger": ["sales ledger", "sales account", "income account"],
    "purchase_ledger": ["purchase ledger", "purchase account", "expense account"],
    "item_name": ["item", "item name", "product", "product name", "description"],
    "quantity": ["quantity", "qty", "units"],
    "rate": ["rate", "price", "unit price", "rate per unit"],
    "contra_ledger": ["contra ledger", "source account", "cash", "bank", "from account"],
    "taxable_value": ["taxable", "taxable value", "taxable amount", "base amount", "taxable amt"],
    "igst": ["igst", "integrated gst", "igst amount", "igst amt"],
    "cgst": ["cgst", "central gst", "cgst amount", "cgst amt"],
    "sgst": ["sgst", "state gst", "sgst amount", "sgst amt"],
    "gst_number": ["gstin", "gst number", "gst no", "tax id", "gst"],
}

# Voucher Types
VOUCHER_TYPES = {
    "sales": "Sales",
    "purchase": "Purchase", 
    "payment": "Payment",
    "receipt": "Receipt",
    "journal": "Journal",
    "contra": "Contra",
}

# Date format for Tally
TALLY_DATE_FORMAT = "%Y%m%d"  # YYYYMMDD format for Tally XML
DISPLAY_DATE_FORMAT = "%d-%m-%Y"  # DD-MM-YYYY for display
