"""
Test to understand Tally's debit/credit logic for sales vouchers
"""
from services.tally_client import TallyClient
from services.xml_generator import TallyXMLGenerator

client = TallyClient()
generator = TallyXMLGenerator("Vrhealthy")

# Test different combinations
test_cases = [
    {
        "name": "Test 1: Party ISDEEMEDPOSITIVE=Yes, Amount=+11800",
        "party_isdeemedpositive": "Yes",
        "party_amount": "11800",
        "sales_isdeemedpositive": "Yes", 
        "sales_amount": "-10000"
    },
    {
        "name": "Test 2: Party ISDEEMEDPOSITIVE=No, Amount=-11800",
        "party_isdeemedpositive": "No",
        "party_amount": "-11800",
        "sales_isdeemedpositive": "No",
        "sales_amount": "10000"
    }
]

for i, test in enumerate(test_cases, 1):
    print(f"\n{test['name']}")
    print("="*60)
    
    xml = f"""<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Import Data</TALLYREQUEST>
    </HEADER>
    <BODY>
        <IMPORTDATA>
            <REQUESTDESC>
                <REPORTNAME>Vouchers</REPORTNAME>
            </REQUESTDESC>
            <REQUESTDATA>
                <TALLYMESSAGE xmlns:UDF="TallyUDF">
                    <VOUCHER REMOTEID="" VCHKEY="" VCHTYPE="Sales" ACTION="Create" OBJVIEW="Accounting Voucher View">
                        <DATE>20250402</DATE>
                        <VOUCHERTYPENAME>Sales</VOUCHERTYPENAME>
                        <VOUCHERNUMBER>TEST-{i}</VOUCHERNUMBER>
                        <NARRATION>Test voucher {i}</NARRATION>
                        <ALLLEDGERENTRIES.LIST>
                            <LEDGERNAME>Test Customer</LEDGERNAME>
                            <ISDEEMEDPOSITIVE>{test['party_isdeemedpositive']}</ISDEEMEDPOSITIVE>
                            <AMOUNT>{test['party_amount']}</AMOUNT>
                        </ALLLEDGERENTRIES.LIST>
                        <ALLLEDGERENTRIES.LIST>
                            <LEDGERNAME>Sales</LEDGERNAME>
                            <ISDEEMEDPOSITIVE>{test['sales_isdeemedpositive']}</ISDEEMEDPOSITIVE>
                            <AMOUNT>{test['sales_amount']}</AMOUNT>
                        </ALLLEDGERENTRIES.LIST>
                    </VOUCHER>
                </TALLYMESSAGE>
            </REQUESTDATA>
        </IMPORTDATA>
    </BODY>
</ENVELOPE>"""
    
    success, msg = client.send_xml(xml)
    print(f"Result: {msg}")
    print(f"Check Tally Day Book to see where amounts appear")
    input("Press Enter to continue to next test...")
