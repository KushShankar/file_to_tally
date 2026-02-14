"""
Tally HTTP Client for communication with Tally Prime
"""
import requests
import logging
from typing import Tuple, List
import xml.etree.ElementTree as ET
from config import TALLY_URL, TALLY_COMPANY

logger = logging.getLogger(__name__)


class TallyClient:
    """Client for communicating with Tally via HTTP"""
    
    def __init__(self, tally_url: str = TALLY_URL, company_name: str = TALLY_COMPANY):
        self.tally_url = tally_url
        self.company_name = company_name
    
    def send_xml(self, xml_data: str) -> Tuple[bool, str]:
        """
        Send XML to Tally
        
        Args:
            xml_data: XML string to send
        
        Returns:
            Tuple of (success, message)
        """
        try:
            logger.info(f"Sending XML to Tally at {self.tally_url}")
            logger.debug(f"XML Data: {xml_data[:500]}...")  # Log first 500 chars
            
            response = requests.post(
                self.tally_url,
                data=xml_data.encode('utf-8'),
                headers={'Content-Type': 'application/xml'},
                timeout=10
            )
            
            logger.info(f"Tally response status: {response.status_code}")
            logger.debug(f"Tally response: {response.text[:500]}")
            
            if response.status_code == 200:
                response_text = response.text
                
                # Try to parse XML response for detailed errors
                try:
                    import xml.etree.ElementTree as ET
                    root = ET.fromstring(response_text)
                    
                    # Check for LINEERROR (detailed error messages with actual text)
                    line_errors = root.findall('.//LINEERROR')
                    if line_errors:
                        error_messages = []
                        for error in line_errors:
                            if error.text and error.text.strip():  # Only add if has actual text
                                error_messages.append(error.text)
                        
                        if error_messages:  # Only return if we found actual error messages
                            logger.error(f"Tally line errors: {'; '.join(error_messages)}")
                            return False, f"Tally error: {'; '.join(error_messages)}"
                    
                    # Check for EXCEPTIONS count
                    exceptions_elem = root.find('.//EXCEPTIONS')
                    if exceptions_elem is not None and exceptions_elem.text and int(exceptions_elem.text) > 0:
                        # Try to find error in LINEERROR
                        line_error = root.find('.//LINEERROR')
                        if line_error is not None and line_error.text and line_error.text.strip():
                            logger.error(f"Tally exception: {line_error.text}")
                            return False, f"Tally error: {line_error.text}"
                        else:
                            logger.error(f"Tally returned {exceptions_elem.text} exceptions but no description")
                            return False, "Tally rejected the voucher. Common causes: ledger doesn't exist, date outside financial period, or invalid data format."
                    
                    # Check for ERRORS count
                    errors_elem = root.find('.//ERRORS')
                    if errors_elem is not None and errors_elem.text and int(errors_elem.text) > 0:
                        # Try to find error description
                        error_desc = root.find('.//ERROR')
                        if error_desc is not None and error_desc.text:
                            logger.error(f"Tally error: {error_desc.text}")
                            return False, f"Tally error: {error_desc.text}"
                        else:
                            logger.error(f"Tally returned {errors_elem.text} errors but no description")
                            return False, f"Tally returned errors. Check if all ledgers exist and data is valid."
                    
                    # If XML parsed successfully but no errors found, check for success indicators
                    created_elem = root.find('.//CREATED')
                    if created_elem is not None and created_elem.text and int(created_elem.text) > 0:
                        logger.info("XML sent successfully to Tally")
                        return True, "Success"
                    
                    # If we got here, XML parsed but no clear success/error indicators
                    # Fall through to text-based checks
                    
                except ET.ParseError:
                    pass  # Not XML or can't parse, continue with text checks
                
                # More comprehensive error checking (only if XML parsing didn't give us an answer)
                error_indicators = [
                    'Error', 'error', 'ERROR',
                    'Failed', 'failed', 'FAILED',
                    'Invalid', 'invalid',
                    'does not exist',
                    'not found',
                    'Company not loaded'
                ]
                
                for indicator in error_indicators:
                    if indicator in response_text:
                        logger.error(f"Tally returned error containing '{indicator}': {response_text[:500]}")
                        return False, f"Tally error: {response_text[:300]}"
                
                # Check if response is empty or just whitespace
                if not response_text.strip():
                    logger.warning("Tally returned empty response")
                    return False, "Tally returned empty response - check if company is loaded"
                
                logger.info("XML sent successfully to Tally")
                return True, "Success"
            else:
                logger.error(f"Tally HTTP error: {response.status_code} - {response.text[:200]}")
                return False, f"HTTP Error {response.status_code}: {response.text[:200]}"
                
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Tally. Is Tally running with HTTP server enabled?")
            return False, "Cannot connect to Tally. Please ensure Tally is running and HTTP server is enabled on port 9000."
        except requests.exceptions.Timeout:
            logger.error("Tally request timeout")
            return False, "Request to Tally timed out"
        except Exception as e:
            logger.error(f"Error sending XML to Tally: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def check_connection(self) -> Tuple[bool, str]:
        """
        Check if Tally is accessible
        
        Returns:
            Tuple of (is_connected, message)
        """
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
                <SVCURRENTCOMPANY>{self.company_name}</SVCURRENTCOMPANY>
            </STATICVARIABLES>
        </DESC>
    </BODY>
</ENVELOPE>"""
        
        try:
            response = requests.post(
                self.tally_url,
                data=test_xml.encode('utf-8'),
                headers={'Content-Type': 'application/xml'},
                timeout=5
            )
            
            if response.status_code == 200:
                return True, f"Connected to Tally at {self.tally_url}"
            else:
                return False, f"Tally responded with status {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return False, f"Cannot connect to Tally at {self.tally_url}. Please ensure Tally is running."
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def get_companies(self) -> Tuple[bool, List[str], str]:
        """
        Fetch all companies from Tally
        
        Returns:
            Tuple of (success, company_list, error_message)
        """
        xml = """<ENVELOPE>
    <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>List of Companies</ID>
    </HEADER>
    <BODY>
        <DESC>
            <STATICVARIABLES>
                <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
            </STATICVARIABLES>
        </DESC>
    </BODY>
</ENVELOPE>"""
        
        try:
            response = requests.post(
                self.tally_url,
                data=xml.encode('utf-8'),
                headers={'Content-Type': 'application/xml'},
                timeout=10
            )
            
            if response.status_code == 200:
                # Parse XML response
                try:
                    root = ET.fromstring(response.text)
                    companies = []
                    
                    # Extract company names
                    for company in root.findall('.//COMPANY'):
                        name = company.find('NAME')
                        if name is not None and name.text:
                            companies.append(name.text)
                    
                    # Also try COMPANYNAME tag
                    for company in root.findall('.//COMPANYNAME'):
                        if company.text and company.text not in companies:
                            companies.append(company.text)
                    
                    logger.info(f"Retrieved {len(companies)} companies from Tally")
                    return True, companies, ""
                    
                except ET.ParseError as e:
                    logger.error(f"Failed to parse Tally response: {str(e)}")
                    return False, [], f"Failed to parse response: {str(e)}"
            else:
                return False, [], f"HTTP Error {response.status_code}"
                
        except Exception as e:
            logger.error(f"Error fetching companies: {str(e)}")
            return False, [], f"Error: {str(e)}"
    
    def get_ledgers(self) -> Tuple[bool, List[str], str]:
        """
        Fetch all ledgers from Tally
        
        Returns:
            Tuple of (success, ledger_list, error_message)
        """
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
                <SVCURRENTCOMPANY>{self.company_name}</SVCURRENTCOMPANY>
            </STATICVARIABLES>
        </DESC>
    </BODY>
</ENVELOPE>"""
        
        try:
            response = requests.post(
                self.tally_url,
                data=xml.encode('utf-8'),
                headers={'Content-Type': 'application/xml'},
                timeout=10
            )
            
            if response.status_code == 200:
                # Parse XML response
                try:
                    root = ET.fromstring(response.text)
                    ledgers = []
                    
                    # Extract ledger names (this may need adjustment based on actual Tally response)
                    for ledger in root.findall('.//LEDGER'):
                        name = ledger.find('NAME')
                        if name is not None and name.text:
                            ledgers.append(name.text)
                    
                    logger.info(f"Retrieved {len(ledgers)} ledgers from Tally")
                    return True, ledgers, ""
                    
                except ET.ParseError as e:
                    logger.error(f"Failed to parse Tally response: {str(e)}")
                    return False, [], f"Failed to parse response: {str(e)}"
            else:
                return False, [], f"HTTP Error {response.status_code}"
                
        except Exception as e:
            logger.error(f"Error fetching ledgers: {str(e)}")
            return False, [], f"Error: {str(e)}"
    
    def ledger_exists(self, ledger_name: str) -> bool:
        """
        Check if a ledger exists in Tally
        
        Args:
            ledger_name: Name of ledger to check
        
        Returns:
            True if ledger exists, False otherwise
        """
        success, ledgers, _ = self.get_ledgers()
        
        if success:
            return ledger_name in ledgers
        
        # If we can't fetch ledgers, assume it doesn't exist
        # This will trigger ledger creation
        return False
