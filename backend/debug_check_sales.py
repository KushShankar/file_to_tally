"""
Check if 'Sales' ledger exists
"""
import requests
import xml.etree.ElementTree as ET

TALLY_URL = "http://localhost:9000"
COMPANY_NAME = "Vrhealthy"
LEDGER_NAME = "Sales"

xml = f"""<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>List of Ledgers</ID>
    </HEADER>
    <BODY>
        <DESC>
            <STATICVARIABLES>
                <SVCURRENTCOMPANY>{COMPANY_NAME}</SVCURRENTCOMPANY>
            </STATICVARIABLES>
            <TDL>
                <TDLMESSAGE>
                    <COLLECTION NAME="List of Ledgers" ISINITIALIZE="Yes">
                        <TYPE>Ledger</TYPE>
                        <FILTERS>IsSales</FILTERS>
                    </COLLECTION>
                    <SYSTEM TYPE="Formulae" NAME="IsSales">
                        $Name = "{LEDGER_NAME}"
                    </SYSTEM>
                </TDLMESSAGE>
            </TDL>
        </DESC>
    </BODY>
</ENVELOPE>"""

print(f"Checking if '{LEDGER_NAME}' ledger exists...")
try:
    response = requests.post(
        TALLY_URL,
        data=xml.encode('utf-8'),
        headers={'Content-Type': 'text/xml;charset=UTF-8'},
        timeout=10
    )

    if response.status_code == 200:
        # If ledger exists, it will be returned
        if f"<NAME>{LEDGER_NAME}</NAME>" in response.text:
            print(f"✅ '{LEDGER_NAME}' ledger FOUND!")
        else:
            print(f"❌ '{LEDGER_NAME}' ledger NOT found!")
            print("Full response to be sure:")
            print(response.text[:200]) # Print start
            
    else:
        print(f"Error: {response.status_code}")

except Exception as e:
    print(f"Error: {e}")
