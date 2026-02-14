"""
Tally XML Generator Service
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TallyXMLGenerator:
    """Generate Tally-compatible XML for ledgers and vouchers"""
    
    def __init__(self, company_name: str = "TallyHealth"):
        self.company_name = company_name
    
    def generate_ledger_xml(
        self,
        ledger_name: str,
        parent: str = "Sundry Debtors",
        opening_balance: float = 0.0
    ) -> str:
        """
        Generate XML to create a ledger in Tally
        
        Args:
            ledger_name: Name of the ledger
            parent: Parent group (default: Sundry Debtors)
            opening_balance: Opening balance (default: 0)
        
        Returns:
            XML string
        """
        xml = f"""<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Import Data</TALLYREQUEST>
    </HEADER>
    <BODY>
        <IMPORTDATA>
            <REQUESTDESC>
                <REPORTNAME>All Masters</REPORTNAME>
                <STATICVARIABLES>
                    <SVCURRENTCOMPANY>{self.company_name}</SVCURRENTCOMPANY>
                </STATICVARIABLES>
            </REQUESTDESC>
            <REQUESTDATA>
                <TALLYMESSAGE xmlns:UDF="TallyUDF">
                    <LEDGER NAME="{ledger_name}" ACTION="Create">
                        <NAME>{ledger_name}</NAME>
                        <PARENT>{parent}</PARENT>
                        <OPENINGBALANCE>{opening_balance}</OPENINGBALANCE>
                        <ISBILLWISEON>No</ISBILLWISEON>
                        <ISCOSTCENTRESON>No</ISCOSTCENTRESON>
                    </LEDGER>
                </TALLYMESSAGE>
            </REQUESTDATA>
        </IMPORTDATA>
    </BODY>
</ENVELOPE>"""
        return xml
    
    def generate_sales_voucher_xml(
        self,
        date: str,
        party_name: str,
        amount: float,
        sales_ledger: str = "Sales",
        invoice_no: Optional[str] = None,
        narration: Optional[str] = None,
        item_name: Optional[str] = None,
        quantity: Optional[float] = None,
        rate: Optional[float] = None,
        taxable_value: Optional[float] = None,
        igst: Optional[float] = None,
        cgst: Optional[float] = None,
        sgst: Optional[float] = None,
        gst_number: Optional[str] = None
    ) -> str:
        """
        Generate XML for Sales voucher with GST support
        
        Args:
            date: Date in YYYYMMDD format
            party_name: Customer name
            amount: Total amount (including GST)
            sales_ledger: Sales ledger name
            invoice_no: Invoice number
            narration: Narration text
            taxable_value: Taxable amount (before GST)
            igst: IGST amount
            cgst: CGST amount
            sgst: SGST amount
            gst_number: Party's GSTIN
        
        Returns:
            XML string
        """
        ref_no = invoice_no or f"INV-{date}"
        narr = narration or f"Sales to {party_name}"
        
        # Determine View mode
        view_mode = "Invoice Voucher View" if item_name else "Accounting Voucher View"
        
        # Calculate sales amount (if taxable value provided, use it; otherwise use total amount)
        sales_amount = taxable_value if taxable_value else amount
        
        # Build GST number tag if provided
        gst_tag = f"<PARTYGSTIN>{gst_number}</PARTYGSTIN>" if gst_number else ""
        
        # Build ledger entries
        ledger_entries = []
        
        # Party ledger (debit - receivable)
        # In Tally: ISDEEMEDPOSITIVE=Yes with NEGATIVE amount shows POSITIVE in Debit column
        ledger_entries.append(f"""                        <ALLLEDGERENTRIES.LIST>
                            <LEDGERNAME>{party_name}</LEDGERNAME>
                            <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
                            <AMOUNT>{-amount}</AMOUNT>
                        </ALLLEDGERENTRIES.LIST>""")
        
        # Sales ledger (credit)
        # In Tally: ISDEEMEDPOSITIVE=Yes with POSITIVE amount shows POSITIVE in Credit column
        ledger_entries.append(f"""                        <ALLLEDGERENTRIES.LIST>
                            <LEDGERNAME>{sales_ledger}</LEDGERNAME>
                            <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
                            <AMOUNT>{sales_amount}</AMOUNT>
                        </ALLLEDGERENTRIES.LIST>""")
        
        # CGST ledger (credit)
        if cgst:
            ledger_entries.append(f"""                        <ALLLEDGERENTRIES.LIST>
                            <LEDGERNAME>Cgst</LEDGERNAME>
                            <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
                            <AMOUNT>{cgst}</AMOUNT>
                        </ALLLEDGERENTRIES.LIST>""")
        
        # SGST ledger (credit)
        if sgst:
            ledger_entries.append(f"""                        <ALLLEDGERENTRIES.LIST>
                            <LEDGERNAME>Sgst</LEDGERNAME>
                            <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
                            <AMOUNT>{sgst}</AMOUNT>
                        </ALLLEDGERENTRIES.LIST>""")
        
        # IGST ledger (credit)
        if igst:
            ledger_entries.append(f"""                        <ALLLEDGERENTRIES.LIST>
                            <LEDGERNAME>Igst</LEDGERNAME>
                            <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
                            <AMOUNT>{igst}</AMOUNT>
                        </ALLLEDGERENTRIES.LIST>""")
        
        ledger_entries_xml = "\n".join(ledger_entries)
        
        xml = f"""<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Import Data</TALLYREQUEST>
    </HEADER>
    <BODY>
        <IMPORTDATA>
            <REQUESTDESC>
                <REPORTNAME>Vouchers</REPORTNAME>
                <STATICVARIABLES>
                    <SVCURRENTCOMPANY>{self.company_name}</SVCURRENTCOMPANY>
                </STATICVARIABLES>
            </REQUESTDESC>
            <REQUESTDATA>
                <TALLYMESSAGE xmlns:UDF="TallyUDF">
                    <VOUCHER VCHTYPE="Sales" ACTION="Create" OBJVIEW="{view_mode}">
                        <DATE>{date}</DATE>
                        <EFFECTIVEDATE>{date}</EFFECTIVEDATE>
                        <VOUCHERTYPENAME>Sales</VOUCHERTYPENAME>
                        <VOUCHERNUMBER>{ref_no}</VOUCHERNUMBER>
                        <PARTYLEDGERNAME>{party_name}</PARTYLEDGERNAME>
                        {gst_tag}
                        <NARRATION>{narr}</NARRATION>
{ledger_entries_xml}
                    </VOUCHER>
                </TALLYMESSAGE>
            </REQUESTDATA>
        </IMPORTDATA>
    </BODY>
</ENVELOPE>"""
        return xml
    
    def generate_purchase_voucher_xml(
        self,
        date: str,
        party_name: str,
        amount: float,
        purchase_ledger: str = "Purchase",
        invoice_no: Optional[str] = None,
        narration: Optional[str] = None
    ) -> str:
        """
        Generate XML for Purchase voucher
        """
        ref_no = invoice_no or f"PINV-{date}"
        narr = narration or f"Purchase from {party_name}"
        
        xml = f"""<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Import Data</TALLYREQUEST>
    </HEADER>
    <BODY>
        <IMPORTDATA>
            <REQUESTDESC>
                <REPORTNAME>Vouchers</REPORTNAME>
                <STATICVARIABLES>
                    <SVCURRENTCOMPANY>{self.company_name}</SVCURRENTCOMPANY>
                </STATICVARIABLES>
            </REQUESTDESC>
            <REQUESTDATA>
                <TALLYMESSAGE xmlns:UDF="TallyUDF">
                    <VOUCHER VCHTYPE="Purchase" ACTION="Create" OBJVIEW="Accounting Voucher View">
                        <DATE>{date}</DATE>
                        <EFFECTIVEDATE>{date}</EFFECTIVEDATE>
                        <VOUCHERTYPENAME>Purchase</VOUCHERTYPENAME>
                        <VOUCHERNUMBER>{ref_no}</VOUCHERNUMBER>
                        <PARTYLEDGERNAME>{party_name}</PARTYLEDGERNAME>
                        <NARRATION>{narr}</NARRATION>
                        <ALLLEDGERENTRIES.LIST>
                            <LEDGERNAME>{purchase_ledger}</LEDGERNAME>
                            <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
                            <AMOUNT>{amount}</AMOUNT>
                        </ALLLEDGERENTRIES.LIST>
                        <ALLLEDGERENTRIES.LIST>
                            <LEDGERNAME>{party_name}</LEDGERNAME>
                            <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
                            <AMOUNT>{-amount}</AMOUNT>
                        </ALLLEDGERENTRIES.LIST>
                    </VOUCHER>
                </TALLYMESSAGE>
            </REQUESTDATA>
        </IMPORTDATA>
    </BODY>
</ENVELOPE>"""
        return xml
    
    def generate_payment_voucher_xml(
        self,
        date: str,
        party_name: str,
        amount: float,
        payment_mode: str = "Cash",
        invoice_no: Optional[str] = None,
        narration: Optional[str] = None
    ) -> str:
        """
        Generate XML for Payment voucher
        """
        ref_no = invoice_no or f"PAY-{date}"
        narr = narration or f"Payment to {party_name}"
        
        xml = f"""<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Import Data</TALLYREQUEST>
    </HEADER>
    <BODY>
        <IMPORTDATA>
            <REQUESTDESC>
                <REPORTNAME>Vouchers</REPORTNAME>
                <STATICVARIABLES>
                    <SVCURRENTCOMPANY>{self.company_name}</SVCURRENTCOMPANY>
                </STATICVARIABLES>
            </REQUESTDESC>
            <REQUESTDATA>
                <TALLYMESSAGE xmlns:UDF="TallyUDF">
                    <VOUCHER REMOTEID="" VCHKEY="" VCHTYPE="Payment" ACTION="Create" OBJVIEW="Accounting Voucher View">
                        <DATE>{date}</DATE>
                        <VOUCHERTYPENAME>Payment</VOUCHERTYPENAME>
                        <VOUCHERNUMBER>{ref_no}</VOUCHERNUMBER>
                        <NARRATION>{narr}</NARRATION>
                        <ALLLEDGERENTRIES.LIST>
                            <LEDGERNAME>{party_name}</LEDGERNAME>
                            <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
                            <AMOUNT>{amount}</AMOUNT>
                        </ALLLEDGERENTRIES.LIST>
                        <ALLLEDGERENTRIES.LIST>
                            <LEDGERNAME>{payment_mode}</LEDGERNAME>
                            <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
                            <AMOUNT>{-amount}</AMOUNT>
                        </ALLLEDGERENTRIES.LIST>
                    </VOUCHER>
                </TALLYMESSAGE>
            </REQUESTDATA>
        </IMPORTDATA>
    </BODY>
</ENVELOPE>"""
        return xml
    
    def generate_receipt_voucher_xml(
        self,
        date: str,
        party_name: str,
        amount: float,
        receipt_mode: str = "Cash",
        invoice_no: Optional[str] = None,
        narration: Optional[str] = None
    ) -> str:
        """
        Generate XML for Receipt voucher
        """
        ref_no = invoice_no or f"REC-{date}"
        narr = narration or f"Receipt from {party_name}"
        
        xml = f"""<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Import Data</TALLYREQUEST>
    </HEADER>
    <BODY>
        <IMPORTDATA>
            <REQUESTDESC>
                <REPORTNAME>Vouchers</REPORTNAME>
                <STATICVARIABLES>
                    <SVCURRENTCOMPANY>{self.company_name}</SVCURRENTCOMPANY>
                </STATICVARIABLES>
            </REQUESTDESC>
            <REQUESTDATA>
                <TALLYMESSAGE xmlns:UDF="TallyUDF">
                    <VOUCHER REMOTEID="" VCHKEY="" VCHTYPE="Receipt" ACTION="Create" OBJVIEW="Accounting Voucher View">
                        <DATE>{date}</DATE>
                        <VOUCHERTYPENAME>Receipt</VOUCHERTYPENAME>
                        <VOUCHERNUMBER>{ref_no}</VOUCHERNUMBER>
                        <NARRATION>{narr}</NARRATION>
                        <ALLLEDGERENTRIES.LIST>
                            <LEDGERNAME>{receipt_mode}</LEDGERNAME>
                            <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
                            <AMOUNT>{amount}</AMOUNT>
                        </ALLLEDGERENTRIES.LIST>
                        <ALLLEDGERENTRIES.LIST>
                            <LEDGERNAME>{party_name}</LEDGERNAME>
                            <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
                            <AMOUNT>{-amount}</AMOUNT>
                        </ALLLEDGERENTRIES.LIST>
                    </VOUCHER>
                </TALLYMESSAGE>
            </REQUESTDATA>
        </IMPORTDATA>
    </BODY>
</ENVELOPE>"""
        return xml
    
    def generate_journal_voucher_xml(
        self,
        date: str,
        debit_ledger: str,
        credit_ledger: str,
        amount: float,
        invoice_no: Optional[str] = None,
        narration: Optional[str] = None
    ) -> str:
        """
        Generate XML for Journal voucher
        """
        ref_no = invoice_no or f"JV-{date}"
        narr = narration or f"Journal Entry"
        
        xml = f"""<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Import Data</TALLYREQUEST>
    </HEADER>
    <BODY>
        <IMPORTDATA>
            <REQUESTDESC>
                <REPORTNAME>Vouchers</REPORTNAME>
                <STATICVARIABLES>
                    <SVCURRENTCOMPANY>{self.company_name}</SVCURRENTCOMPANY>
                </STATICVARIABLES>
            </REQUESTDESC>
            <REQUESTDATA>
                <TALLYMESSAGE xmlns:UDF="TallyUDF">
                    <VOUCHER REMOTEID="" VCHKEY="" VCHTYPE="Journal" ACTION="Create" OBJVIEW="Accounting Voucher View">
                        <DATE>{date}</DATE>
                        <VOUCHERTYPENAME>Journal</VOUCHERTYPENAME>
                        <VOUCHERNUMBER>{ref_no}</VOUCHERNUMBER>
                        <NARRATION>{narr}</NARRATION>
                        <ALLLEDGERENTRIES.LIST>
                            <LEDGERNAME>{debit_ledger}</LEDGERNAME>
                            <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
                            <AMOUNT>{amount}</AMOUNT>
                        </ALLLEDGERENTRIES.LIST>
                        <ALLLEDGERENTRIES.LIST>
                            <LEDGERNAME>{credit_ledger}</LEDGERNAME>
                            <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
                            <AMOUNT>{-amount}</AMOUNT>
                        </ALLLEDGERENTRIES.LIST>
                    </VOUCHER>
                </TALLYMESSAGE>
            </REQUESTDATA>
        </IMPORTDATA>
    </BODY>
</ENVELOPE>"""
        return xml
    
    def generate_contra_voucher_xml(
        self,
        date: str,
        debit_ledger: str,
        credit_ledger: str,
        amount: float,
        invoice_no: Optional[str] = None,
        narration: Optional[str] = None
    ) -> str:
        """
        Generate XML for Contra voucher
        """
        ref_no = invoice_no or f"CNTR-{date}"
        narr = narration or f"Contra Entry"
        
        xml = f"""<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Import Data</TALLYREQUEST>
    </HEADER>
    <BODY>
        <IMPORTDATA>
            <REQUESTDESC>
                <REPORTNAME>Vouchers</REPORTNAME>
                <STATICVARIABLES>
                    <SVCURRENTCOMPANY>{self.company_name}</SVCURRENTCOMPANY>
                </STATICVARIABLES>
            </REQUESTDESC>
            <REQUESTDATA>
                <TALLYMESSAGE xmlns:UDF="TallyUDF">
                    <VOUCHER VCHTYPE="Contra" ACTION="Create" OBJVIEW="Accounting Voucher View">
                        <DATE>{date}</DATE>
                        <EFFECTIVEDATE>{date}</EFFECTIVEDATE>
                        <VOUCHERTYPENAME>Contra</VOUCHERTYPENAME>
                        <VOUCHERNUMBER>{ref_no}</VOUCHERNUMBER>
                        <NARRATION>{narr}</NARRATION>
                        <ALLLEDGERENTRIES.LIST>
                            <LEDGERNAME>{debit_ledger}</LEDGERNAME>
                            <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
                            <AMOUNT>{amount}</AMOUNT>
                        </ALLLEDGERENTRIES.LIST>
                        <ALLLEDGERENTRIES.LIST>
                            <LEDGERNAME>{credit_ledger}</LEDGERNAME>
                            <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
                            <AMOUNT>{-amount}</AMOUNT>
                        </ALLLEDGERENTRIES.LIST>
                    </VOUCHER>
                </TALLYMESSAGE>
            </REQUESTDATA>
        </IMPORTDATA>
    </BODY>
</ENVELOPE>"""
        return xml
