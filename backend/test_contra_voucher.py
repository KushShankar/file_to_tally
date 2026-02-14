import requests

TALLY_URL = "http://localhost:9000"
COMPANY_NAME = "Vrhealthy"

# XML Structure matching what we implemented
xml = """<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Import Data</TALLYREQUEST>
    </HEADER>
    <BODY>
        <IMPORTDATA>
            <REQUESTDESC>
                <REPORTNAME>Vouchers</REPORTNAME>
                <STATICVARIABLES>
                    <SVCURRENTCOMPANY>Vrhealthy</SVCURRENTCOMPANY>
                </STATICVARIABLES>
            </REQUESTDESC>
            <REQUESTDATA>
                <TALLYMESSAGE xmlns:UDF="TallyUDF">
                    <VOUCHER VCHTYPE="Contra" ACTION="Create" OBJVIEW="Accounting Voucher View">
                        <DATE>20240401</DATE>
                        <EFFECTIVEDATE>20240401</EFFECTIVEDATE>
                        <VOUCHERTYPENAME>Contra</VOUCHERTYPENAME>
                        <VOUCHERNUMBER>CNTR-TEST-001</VOUCHERNUMBER>
                        <NARRATION>Test Contra Value</NARRATION>
                        <ALLLEDGERENTRIES.LIST>
                            <LEDGERNAME>Cash</LEDGERNAME>
                            <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
                            <AMOUNT>100.00</AMOUNT>
                        </ALLLEDGERENTRIES.LIST>
                        <ALLLEDGERENTRIES.LIST>
                            <LEDGERNAME>Cash</LEDGERNAME>
                            <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
                            <AMOUNT>-100.00</AMOUNT>
                        </ALLLEDGERENTRIES.LIST>
                    </VOUCHER>
                </TALLYMESSAGE>
            </REQUESTDATA>
        </IMPORTDATA>
    </BODY>
</ENVELOPE>"""
# Cash to Cash transfer (valid in Tally terms for testing structure)

print("Sending Contra Voucher XML...")
try:
    response = requests.post(TALLY_URL, data=xml, headers={'Content-Type': 'text/xml'})
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
