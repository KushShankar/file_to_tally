
import sys
import os
import logging
from datetime import datetime

# Add backend to path
sys.path.append(os.path.abspath("tallyagent/backend"))

from services.xml_generator import TallyXMLGenerator
from services.validator import DataValidator

# Setup logging
logging.basicConfig(level=logging.INFO)

def debug_voucher_xml():
    print("--- Debugging Voucher XML Generation ---")
    
    # Mock data from screenshot
    raw_data = {
        'date': '02-04-2025',
        'invoice_no': 'S-001',
        'party_name': 'Rahul Traders',
        'taxable_value': 10000,
        'cgst': 900,
        'sgst': 900,
        'amount': 11800
    }
    
    print(f"Raw Data: {raw_data}")
    
    # Simulate Validation
    validator = DataValidator()
    
    # Manually run validation logic used in upload.py
    # validate_voucher_entry does this:
    validated = {}
    
    # Date
    valid, date_val, err = validator.validate_date(raw_data['date'])
    print(f"Date Validation: {valid}, {date_val}, {err}")
    validated['date'] = date_val
    
    # Party
    valid, party_val, err = validator.validate_text(raw_data['party_name'], 'Party Name')
    validated['party_name'] = validator.sanitize_ledger_name(party_val)
    
    # Amount
    validated['amount'] = float(raw_data['amount'])
    
    # Others
    validated['invoice_no'] = raw_data['invoice_no']
    validated['taxable_value'] = float(raw_data['taxable_value'])
    validated['cgst'] = float(raw_data['cgst'])
    validated['sgst'] = float(raw_data['sgst'])
    validated['sales_ledger'] = 'Sales'
    
    print(f"Validated Data: {validated}")
    
    # Generate XML
    generator = TallyXMLGenerator(company_name="Vrhealthy") # User mentioned 'Vrhealthy' in previous turn? 
    # Or just default. The screenshot assumes company is selected.
    
    xml = generator.generate_sales_voucher_xml(
        date=validated['date'],
        party_name=validated['party_name'],
        amount=validated['amount'],
        sales_ledger=validated['sales_ledger'],
        invoice_no=validated['invoice_no'],
        taxable_value=validated['taxable_value'],
        cgst=validated['cgst'],
        sgst=validated['sgst']
    )
    
    print("\n--- Generated XML ---")
    # print(xml)
    with open("voucher.xml", "w", encoding="utf-8") as f:
        f.write(xml)
    print("XML written to voucher.xml")
    print("---------------------")

if __name__ == "__main__":
    debug_voucher_xml()
