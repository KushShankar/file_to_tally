"""
Test script to fetch Voucher Types from Tally
"""
import requests
import xml.etree.ElementTree as ET

TALLY_URL = "http://localhost:9000"
COMPANY_NAME = "Vrhealthy"

xml = f"""<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>List of VoucherTypes</ID>
    </HEADER>
    <BODY>
        <DESC>
            <STATICVARIABLES>
                <SVCURRENTCOMPANY>{COMPANY_NAME}</SVCURRENTCOMPANY>
            </STATICVARIABLES>
        </DESC>
    </BODY>
</ENVELOPE>"""

print("Fetching Voucher Types from Tally...")
try:
    response = requests.post(
        TALLY_URL,
        data=xml.encode('utf-8'),
        headers={'Content-Type': 'text/xml;charset=UTF-8'},
        timeout=10
    )

    if response.status_code == 200:
        root = ET.fromstring(response.text)
        vtypes = []
        for vtype in root.findall('.//VOUCHERTYPE'):
            name = vtype.get('NAME')  # Try attribute
            if not name:
                name_elem = vtype.find('NAME') # Try child element
                if name_elem is not None:
                    name = name_elem.text
            
            if name:
                vtypes.append(name)
        
        print(f"Found {len(vtypes)} voucher types:")
        print(vtypes)
        
        if "Sales" in vtypes:
            print("\n✅ 'Sales' voucher type found!")
        else:
            print("\n❌ 'Sales' voucher type NOT found!")
            
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"Error: {e}")
