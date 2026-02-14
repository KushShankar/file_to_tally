"""
Fetch Company Info to see Period
"""
import requests
import xml.etree.ElementTree as ET

TALLY_URL = "http://localhost:9000"
COMPANY_NAME = "Vrhealthy"

xml = f"""<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>Company Info</ID>
    </HEADER>
    <BODY>
        <DESC>
            <STATICVARIABLES>
                <SVCURRENTCOMPANY>{COMPANY_NAME}</SVCURRENTCOMPANY>
            </STATICVARIABLES>
            <TDL>
                <TDLMESSAGE>
                    <COLLECTION NAME="Company Info" ISINITIALIZE="Yes">
                        <TYPE>Company</TYPE>
                        <FETCH>Name, StartingFrom, EndingAt</FETCH>
                    </COLLECTION>
                </TDLMESSAGE>
            </TDL>
        </DESC>
    </BODY>
</ENVELOPE>"""

print("Fetching Company Info...")
try:
    response = requests.post(
        TALLY_URL,
        data=xml.encode('utf-8'),
        headers={'Content-Type': 'text/xml;charset=UTF-8'},
        timeout=10
    )

    if response.status_code == 200:
        root = ET.fromstring(response.text)
        for comp in root.findall('.//COMPANY'):
            name = comp.find('NAME').text if comp.find('NAME') is not None else "Unknown"
            start = comp.find('STARTINGFROM').text if comp.find('STARTINGFROM') is not None else "Unknown"
            # EndingAt might not be standard field, Tally uses BooksFrom
            books_from = comp.find('BOOKSFROM').text if comp.find('BOOKSFROM') is not None else "Unknown"
            
            print(f"Company: {name}")
            print(f"Starting From: {start}")
            print(f"Books From: {books_from}")
            
    else:
        print(f"Error: {response.status_code}")

except Exception as e:
    print(f"Error: {e}")
