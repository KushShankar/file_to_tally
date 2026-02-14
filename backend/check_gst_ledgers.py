"""
Check if GST ledgers exist and list all ledgers
"""
from services.tally_client import TallyClient

client = TallyClient()

# Check specific GST ledgers
gst_ledgers = ["Output CGST", "Output SGST", "Output IGST", "CGST", "SGST", "IGST"]

print("Checking GST ledgers:")
for ledger_name in gst_ledgers:
    exists = client.ledger_exists(ledger_name)
    print(f"  {ledger_name}: {'EXISTS' if exists else 'DOES NOT EXIST'}")

# Try to get list of all ledgers
print("\nFetching all ledgers from Tally...")
try:
    xml = """<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Export Data</TALLYREQUEST>
    </HEADER>
    <BODY>
        <EXPORTDATA>
            <REQUESTDESC>
                <REPORTNAME>List of Accounts</REPORTNAME>
                <STATICVARIABLES>
                    <SVCURRENTCOMPANY>Vrhealthy</SVCURRENTCOMPANY>
                </STATICVARIABLES>
            </REQUESTDESC>
        </EXPORTDATA>
    </BODY>
</ENVELOPE>"""
    
    import requests
    response = requests.post("http://localhost:9000", data=xml, headers={'Content-Type': 'application/xml'})
    
    if response.status_code == 200:
        # Look for GST-related ledgers in response
        if "CGST" in response.text or "SGST" in response.text:
            print("Found GST-related ledgers in Tally!")
            # Extract ledger names containing GST
            import re
            ledgers = re.findall(r'<NAME>(.*?GST.*?)</NAME>', response.text, re.IGNORECASE)
            if ledgers:
                print("\nGST Ledgers found:")
                for ledger in set(ledgers):
                    print(f"  - {ledger}")
        else:
            print("No GST ledgers found in Tally")
    else:
        print(f"Error fetching ledgers: {response.status_code}")
        
except Exception as e:
    print(f"Error: {e}")
