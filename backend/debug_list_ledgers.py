"""
List all ledgers using TallyClient logic
"""
import requests
import xml.etree.ElementTree as ET

TALLY_URL = "http://localhost:9000"
COMPANY_NAME = "Vrhealthy"

xml = f"""<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>All Ledgers</ID>
    </HEADER>
    <BODY>
        <DESC>
            <STATICVARIABLES>
                <SVCURRENTCOMPANY>{COMPANY_NAME}</SVCURRENTCOMPANY>
            </STATICVARIABLES>
            <TDL>
                <TDLMESSAGE>
                    <COLLECTION NAME="All Ledgers" ISINITIALIZE="Yes">
                        <TYPE>Ledger</TYPE>
                    </COLLECTION>
                </TDLMESSAGE>
            </TDL>
        </DESC>
    </BODY>
</ENVELOPE>"""

print("Fetching all ledgers...")
try:
    response = requests.post(
        TALLY_URL,
        data=xml.encode('utf-8'),
        headers={'Content-Type': 'text/xml;charset=UTF-8'},
        timeout=10
    )

    if response.status_code == 200:
        root = ET.fromstring(response.text)
        ledgers = []
        for ledger in root.findall('.//LEDGER'):
            name = ledger.get('NAME')
            if name:
                ledgers.append(name)
        
        print(f"Found {len(ledgers)} ledgers:")
        print(ledgers)
        
        if "Sales" in ledgers:
            print("\n✅ 'Sales' ledger FOUND!")
        else:
            print("\n❌ 'Sales' ledger NOT found!")
            
    else:
        print(f"Error: {response.status_code}")

except Exception as e:
    print(f"Error: {e}")
