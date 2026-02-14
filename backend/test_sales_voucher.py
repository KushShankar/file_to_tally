"""
Test script to see actual Tally error
"""
import requests

TALLY_URL = "http://localhost:9000"
COMPANY_NAME = "Vrhealthy"

# Test sales voucher
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
                    <VOUCHER REMOTEID="" VCHKEY="" VCHTYPE="Sales" ACTION="Create" OBJVIEW="Invoice Voucher View">
                        <DATE>20260212</DATE>
                        <VOUCHERTYPENAME>Sales</VOUCHERTYPENAME>
                        <VOUCHERNUMBER>TEST001</VOUCHERNUMBER>
                        <PARTYLEDGERNAME>Test Customer 123</PARTYLEDGERNAME>
                        <NARRATION>Test sales voucher</NARRATION>
                        <ALLLEDGERENTRIES.LIST>
                            <LEDGERNAME>Test Customer 123</LEDGERNAME>
                            <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
                            <AMOUNT>1000</AMOUNT>
                        </ALLLEDGERENTRIES.LIST>
                        <ALLLEDGERENTRIES.LIST>
                            <LEDGERNAME>Sales</LEDGERNAME>
                            <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
                            <AMOUNT>-1000</AMOUNT>
                        </ALLLEDGERENTRIES.LIST>
                    </VOUCHER>
                </TALLYMESSAGE>
            </REQUESTDATA>
        </IMPORTDATA>
    </BODY>
</ENVELOPE>"""

print("Sending test sales voucher to Tally...")
print("="*60)

response = requests.post(
    TALLY_URL,
    data=xml.encode('utf-8'),
    headers={'Content-Type': 'application/xml'},
    timeout=10
)

print(f"Status Code: {response.status_code}")
print(f"\nFull Response:")
print(response.text)
print("="*60)

# Parse for errors
import xml.etree.ElementTree as ET
try:
    root = ET.fromstring(response.text)
    
    # Check for line errors
    line_errors = root.findall('.//LINEERROR')
    if line_errors:
        print("\n❌ LINE ERRORS FOUND:")
        for error in line_errors:
            print(f"  - {error.text}")
    
    # Check error count
    errors = root.find('.//ERRORS')
    if errors is not None:
        print(f"\nError Count: {errors.text}")
    
    created = root.find('.//CREATED')
    if created is not None:
        print(f"Created Count: {created.text}")
        
except Exception as e:
    print(f"\nCouldn't parse XML: {e}")
