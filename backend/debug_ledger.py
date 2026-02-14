"""
Test script to see actual Tally error - Ledger Creation
"""
import requests

TALLY_URL = "http://localhost:9000"
COMPANY_NAME = "Vrhealthy"
LEDGER_NAME = "Test Ledger X1"

# Test ledger creation
xml = f"""<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Import Data</TALLYREQUEST>
    </HEADER>
    <BODY>
        <IMPORTDATA>
            <REQUESTDESC>
                <REPORTNAME>All Masters</REPORTNAME>
                <STATICVARIABLES>
                    <SVCURRENTCOMPANY>{COMPANY_NAME}</SVCURRENTCOMPANY>
                </STATICVARIABLES>
            </REQUESTDESC>
            <REQUESTDATA>
                <TALLYMESSAGE xmlns:UDF="TallyUDF">
                    <LEDGER NAME="{LEDGER_NAME}" ACTION="Create">
                        <NAME>{LEDGER_NAME}</NAME>
                        <PARENT>Sundry Debtors</PARENT>
                        <OPENINGBALANCE>0</OPENINGBALANCE>
                        <ISBILLWISEON>No</ISBILLWISEON>
                        <ISCOSTCENTRESON>No</ISCOSTCENTRESON>
                    </LEDGER>
                </TALLYMESSAGE>
            </REQUESTDATA>
        </IMPORTDATA>
    </BODY>
</ENVELOPE>"""

print(f"Creating ledger '{LEDGER_NAME}'...")
print("="*60)

try:
    response = requests.post(
        TALLY_URL,
        data=xml.encode('utf-8'),
        headers={'Content-Type': 'text/xml;charset=UTF-8'},
        timeout=10
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"Error: {e}")
