"""
Test script to check and create GST ledgers
"""
from services.tally_client import TallyClient
from services.xml_generator import TallyXMLGenerator

client = TallyClient()
generator = TallyXMLGenerator("Vrhealthy")

# Check if GST ledgers exist
gst_ledgers = ["Output CGST", "Output SGST", "Output IGST"]

for ledger_name in gst_ledgers:
    exists = client.ledger_exists(ledger_name)
    print(f"{ledger_name}: {'EXISTS' if exists else 'DOES NOT EXIST'}")
    
    if not exists:
        print(f"Creating {ledger_name}...")
        xml = generator.generate_ledger_xml(ledger_name, "Duties & Taxes")
        success, msg = client.send_xml(xml)
        print(f"  Result: {msg}")
