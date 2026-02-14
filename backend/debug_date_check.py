"""
Test script to see actual Tally error - 2024 Date
"""
import requests
import os

TALLY_URL = "http://localhost:9000"
COMPANY_NAME = "Vrhealthy"

# Test sales voucher - REMOVED REMOTEID and VCHKEY, Changed Date to 2024
xml = f"""<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Import Data</TALLYREQUEST>
    </HEADER>
    <BODY>
        <IMPORTDATA>
            <REQUESTDESC>
                <REPORTNAME>Vouchers</REPORTNAME>
                <STATICVARIABLES>
                    <SVCURRENTCOMPANY>{COMPANY_NAME}</SVCURRENTCOMPANY>
                </STATICVARIABLES>
            </REQUESTDESC>
            <REQUESTDATA>
                <TALLYMESSAGE xmlns:UDF="TallyUDF">
                    <VOUCHER VCHTYPE="Sales" ACTION="Create" OBJVIEW="Invoice Voucher View">
                        <DATE>20240401</DATE>
                        <VOUCHERTYPENAME>Sales</VOUCHERTYPENAME>
                        <VOUCHERNUMBER>TEST2024-001</VOUCHERNUMBER>
                        <PARTYLEDGERNAME>Test Customer 123</PARTYLEDGERNAME>
                        <NARRATION>Test sales voucher 2024</NARRATION>
                        <ALLLEDGERENTRIES.LIST>
                            <LEDGERNAME>Test Customer 123</LEDGERNAME>
                            <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
                            <AMOUNT>-1000.00</AMOUNT>
                        </ALLLEDGERENTRIES.LIST>
                        <ALLLEDGERENTRIES.LIST>
                            <LEDGERNAME>Sales</LEDGERNAME>
                            <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
                            <AMOUNT>1000.00</AMOUNT>
                        </ALLLEDGERENTRIES.LIST>
                    </VOUCHER>
                </TALLYMESSAGE>
            </REQUESTDATA>
        </IMPORTDATA>
    </BODY>
</ENVELOPE>"""

print("Sending test sales voucher 2024...")
print("="*60)

try:
    response = requests.post(
        TALLY_URL,
        data=xml.encode('utf-8'),
        headers={'Content-Type': 'text/xml;charset=UTF-8'},
        timeout=10
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response Length: {len(response.text)}")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"Error: {e}")
