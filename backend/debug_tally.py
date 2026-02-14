"""
Test script to see actual Tally error
"""
import requests
import os

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
                        <EFFECTIVEDATE>20260212</EFFECTIVEDATE>
                        <VOUCHERTYPENAME>Sales</VOUCHERTYPENAME>
                        <VOUCHERNUMBER>TEST002</VOUCHERNUMBER>
                        <PARTYLEDGERNAME>Test Customer 123</PARTYLEDGERNAME>
                        <NARRATION>Test sales voucher</NARRATION>
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

print("Sending test sales voucher to Tally...")
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
    
    # Save full response to file
    with open("tally_response.xml", "w", encoding="utf-8") as f:
        f.write(response.text)
    
    print("Full response saved to tally_response.xml")
    
except Exception as e:
    print(f"Error: {e}")
