"""
Create Sales and Purchase ledgers
"""
import requests

TALLY_URL = "http://localhost:9000"
COMPANY_NAME = "Vrhealthy"

def create_ledger(name, parent):
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
                        <LEDGER NAME="{name}" ACTION="Create">
                            <NAME>{name}</NAME>
                            <PARENT>{parent}</PARENT>
                            <OPENINGBALANCE>0</OPENINGBALANCE>
                            <ISBILLWISEON>No</ISBILLWISEON>
                            <ISCOSTCENTRESON>No</ISCOSTCENTRESON>
                        </LEDGER>
                    </TALLYMESSAGE>
                </REQUESTDATA>
            </IMPORTDATA>
        </BODY>
    </ENVELOPE>"""

    print(f"Creating ledger '{name}' under '{parent}'...")
    try:
        response = requests.post(
            TALLY_URL,
            data=xml.encode('utf-8'),
            headers={'Content-Type': 'text/xml;charset=UTF-8'},
            timeout=10
        )
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

# Create Ledgers
create_ledger("Sales", "Sales Accounts")
create_ledger("Purchase", "Purchase Accounts")
