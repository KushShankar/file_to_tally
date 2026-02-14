"""
Test script to send a sample GST voucher and see the exact Tally response
"""
from services.tally_client import TallyClient
from services.xml_generator import TallyXMLGenerator

client = TallyClient()
generator = TallyXMLGenerator("Vrhealthy")

# Create a test sales voucher with GST
xml = generator.generate_sales_voucher_xml(
    date="20230402",
    party_name="Test Customer",
    amount=11800,
    sales_ledger="Sales",
    invoice_no="TEST-001",
    narration="Test GST voucher",
    taxable_value=10000,
    cgst=900,
    sgst=900,
    gst_number=None
)

print("Sending XML:")
print(xml)
print("\n" + "="*80 + "\n")

success, msg = client.send_xml(xml)
print(f"Success: {success}")
print(f"Message: {msg}")
