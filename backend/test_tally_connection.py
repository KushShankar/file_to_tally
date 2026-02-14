"""
Diagnostic script to test Tally connection and XML sending
"""
import requests
import sys

# Test configuration
TALLY_URL = "http://localhost:9000"
COMPANY_NAME = "TallyHealth"  # Change this to your actual company name

def test_connection():
    """Test basic connection to Tally"""
    print(f"\n{'='*60}")
    print("TEST 1: Testing Tally Connection")
    print(f"{'='*60}")
    
    test_xml = f"""<ENVELOPE>
    <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Data</TYPE>
        <ID>CompanyInfo</ID>
    </HEADER>
    <BODY>
        <DESC>
            <STATICVARIABLES>
                <SVCURRENTCOMPANY>{COMPANY_NAME}</SVCURRENTCOMPANY>
            </STATICVARIABLES>
        </DESC>
    </BODY>
</ENVELOPE>"""
    
    try:
        response = requests.post(
            TALLY_URL,
            data=test_xml.encode('utf-8'),
            headers={'Content-Type': 'application/xml'},
            timeout=5
        )
        
        print(f"✓ Connection successful!")
        print(f"  Status Code: {response.status_code}")
        print(f"  Response Length: {len(response.text)} bytes")
        print(f"\n  Response Preview:")
        print(f"  {response.text[:500]}")
        
        if "Company not loaded" in response.text or "does not exist" in response.text:
            print(f"\n⚠ WARNING: Company '{COMPANY_NAME}' may not be loaded in Tally!")
            print(f"  Please check:")
            print(f"  1. Is Tally Prime running?")
            print(f"  2. Is the company '{COMPANY_NAME}' open?")
            print(f"  3. Is the company name spelled exactly as shown in Tally?")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to Tally at {TALLY_URL}")
        print(f"  Please ensure:")
        print(f"  1. Tally Prime is running")
        print(f"  2. ODBC Server is enabled (F12 → Advanced Configuration)")
        print(f"  3. Port is set to 9000")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def test_ledger_creation():
    """Test creating a ledger"""
    print(f"\n{'='*60}")
    print("TEST 2: Testing Ledger Creation")
    print(f"{'='*60}")
    
    ledger_xml = f"""<ENVELOPE>
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
                    <LEDGER NAME="Test Customer 123" ACTION="Create">
                        <NAME>Test Customer 123</NAME>
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
    
    print(f"Attempting to create ledger: 'Test Customer 123'")
    
    try:
        response = requests.post(
            TALLY_URL,
            data=ledger_xml.encode('utf-8'),
            headers={'Content-Type': 'application/xml'},
            timeout=10
        )
        
        print(f"\n  Status Code: {response.status_code}")
        print(f"  Response:")
        print(f"  {response.text}")
        
        # Check for errors
        error_keywords = ['Error', 'error', 'Failed', 'failed', 'Invalid', 'does not exist', 'not found']
        has_error = any(keyword in response.text for keyword in error_keywords)
        
        if has_error:
            print(f"\n✗ Ledger creation FAILED")
            print(f"  Tally returned an error. Check the response above.")
        else:
            print(f"\n✓ Ledger creation appears successful!")
            print(f"  Please check Tally to verify 'Test Customer 123' was created")
            print(f"  Location: Gateway → Accounts Info → Ledgers → Sundry Debtors")
        
        return not has_error
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def test_get_ledgers():
    """Test fetching ledger list"""
    print(f"\n{'='*60}")
    print("TEST 3: Testing Ledger List Retrieval")
    print(f"{'='*60}")
    
    xml = f"""<ENVELOPE>
    <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>LedgerList</ID>
    </HEADER>
    <BODY>
        <DESC>
            <STATICVARIABLES>
                <SVCURRENTCOMPANY>{COMPANY_NAME}</SVCURRENTCOMPANY>
            </STATICVARIABLES>
        </DESC>
    </BODY>
</ENVELOPE>"""
    
    try:
        response = requests.post(
            TALLY_URL,
            data=xml.encode('utf-8'),
            headers={'Content-Type': 'application/xml'},
            timeout=10
        )
        
        print(f"  Status Code: {response.status_code}")
        print(f"  Response Length: {len(response.text)} bytes")
        print(f"\n  Response Preview:")
        print(f"  {response.text[:1000]}")
        
        # Try to count ledgers
        ledger_count = response.text.count('<LEDGER')
        print(f"\n  Found approximately {ledger_count} ledgers")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("TALLY CONNECTION DIAGNOSTIC TOOL")
    print("="*60)
    print(f"\nTally URL: {TALLY_URL}")
    print(f"Company Name: {COMPANY_NAME}")
    print(f"\nIMPORTANT: Make sure Tally Prime is running and")
    print(f"the company '{COMPANY_NAME}' is open!")
    print("="*60)
    
    # Run tests
    test1 = test_connection()
    
    if test1:
        test2 = test_ledger_creation()
        test3 = test_get_ledgers()
        
        print(f"\n{'='*60}")
        print("TEST SUMMARY")
        print(f"{'='*60}")
        print(f"  Connection Test: {'✓ PASS' if test1 else '✗ FAIL'}")
        print(f"  Ledger Creation: {'✓ PASS' if test2 else '✗ FAIL'}")
        print(f"  Ledger Retrieval: {'✓ PASS' if test3 else '✗ FAIL'}")
        print(f"{'='*60}\n")
        
        if test2:
            print("✓ All tests passed! The system can communicate with Tally.")
            print("  If ledgers still don't appear, check:")
            print("  1. Company name in config.py matches Tally exactly")
            print("  2. You're looking in the right company in Tally")
            print("  3. Refresh the ledger list in Tally (F5)")
        else:
            print("⚠ Some tests failed. Review the error messages above.")
    else:
        print(f"\n⚠ Cannot connect to Tally. Please fix connection issues first.")
    
    print("\n")
