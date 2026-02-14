# User Guide - Excel to Tally AI Agent

Complete guide on how to use the Excel to Tally AI Agent to import your accounting data.

---

## Overview

The Excel to Tally AI Agent helps you:
- Convert Excel data to Tally vouchers automatically
- Save hours of manual data entry
- Reduce errors in data entry
- Import bulk transactions quickly

---

## Preparing Your Excel File

### Required Columns

Every Excel file must have these **3 essential columns**:

1. **Date** - Transaction date
2. **Party Name** - Customer/Vendor name
3. **Amount** - Transaction amount

### Optional Columns

You can also include:
- Invoice Number
- Narration/Description
- Item Name
- Quantity
- Rate
- Sales/Purchase Ledger

### Column Naming Tips

The AI is smart and can recognize various column names:

✅ **Date**: "Date", "Invoice Date", "Transaction Date", "Entry Date"  
✅ **Party**: "Customer", "Vendor", "Party Name", "Account Name"  
✅ **Amount**: "Amount", "Total", "Invoice Amount", "Value"

### Date Format

Supported date formats:
- DD-MM-YYYY (12-02-2026)
- DD/MM/YYYY (12/02/2026)
- YYYY-MM-DD (2026-02-12)
- DD-MMM-YYYY (12-Feb-2026)

### Amount Format

- Use numbers only: `10000` or `10000.50`
- Commas are okay: `10,000`
- Currency symbols will be removed automatically

---

## Step-by-Step Usage

### Step 1: Upload Your File

1. Open the web interface at `http://localhost:8000`
2. **Drag and drop** your Excel file into the upload zone
   - OR click the upload zone to browse for a file
3. Wait for the file to upload and analyze

**Supported formats**: .xlsx, .xls, .csv

### Step 2: Select Voucher Type

Choose the type of voucher you want to create:

- **💰 Sales** - For sales invoices
- **🛒 Purchase** - For purchase invoices
- **💸 Payment** - For payments made
- **🧾 Receipt** - For receipts received
- **📝 Journal** - For journal entries

### Step 3: Confirm Column Mapping

The AI will suggest how to map your Excel columns to Tally fields.

**Review the mappings**:
- ✅ Green badge (80%+) - High confidence, likely correct
- ⚠️ Yellow badge (50-80%) - Medium confidence, please verify
- ❌ Red badge (<50%) - Low confidence, please check

**Adjust if needed**:
- Click the dropdown to change any mapping
- Select "-- Not Mapped --" to skip a column

**Required mappings**:
- Date ✅
- Party Name ✅
- Amount ✅

### Step 4: Preview Your Data

Review the sample data shown in the preview table to ensure everything looks correct.

### Step 5: Process

**Options**:
- ✅ **Automatically create missing ledgers** (recommended)
  - If a customer/vendor doesn't exist in Tally, it will be created automatically

Click **"Process & Send to Tally"**

### Step 6: Review Results

The system will show:
- ✅ Number of successful entries
- ❌ Number of failed entries
- 📋 List of any errors with details
- 🆕 Ledgers that were created

---

## Voucher Type Details

### Sales Vouchers

**Use for**: Customer invoices, sales transactions

**Required fields**:
- Date
- Customer Name
- Amount

**Optional fields**:
- Invoice Number
- Sales Ledger (default: "Sales")
- Narration

**Example Excel**:

| Date       | Customer Name | Amount | Invoice No | Narration           |
|------------|---------------|--------|------------|---------------------|
| 12-02-2026 | ABC Corp      | 10000  | INV001     | Sale of goods       |
| 13-02-2026 | XYZ Ltd       | 15000  | INV002     | Consulting services |

### Purchase Vouchers

**Use for**: Vendor invoices, purchase transactions

**Required fields**:
- Date
- Vendor Name
- Amount

**Optional fields**:
- Invoice Number
- Purchase Ledger (default: "Purchase")
- Narration

**Example Excel**:

| Date       | Vendor Name    | Amount | Bill No | Narration        |
|------------|----------------|--------|---------|------------------|
| 12-02-2026 | Supplier ABC   | 8000   | B001    | Raw materials    |
| 13-02-2026 | Vendor XYZ     | 12000  | B002    | Office supplies  |

### Payment Vouchers

**Use for**: Payments made to vendors, expenses

**Required fields**:
- Date
- Party Name
- Amount

**Example Excel**:

| Date       | Party Name   | Amount | Narration          |
|------------|--------------|--------|--------------------|
| 12-02-2026 | Supplier ABC | 5000   | Payment for goods  |

### Receipt Vouchers

**Use for**: Receipts from customers

**Required fields**:
- Date
- Party Name
- Amount

**Example Excel**:

| Date       | Party Name | Amount | Narration           |
|------------|------------|--------|---------------------|
| 12-02-2026 | ABC Corp   | 10000  | Payment received    |

---

## Common Scenarios

### Scenario 1: Bulk Sales Import

You have 100 sales invoices in Excel.

1. Prepare Excel with: Date, Customer, Amount, Invoice No
2. Upload file
3. Select "Sales" voucher type
4. Confirm mappings
5. Enable "Create missing ledgers"
6. Process

Result: All 100 sales vouchers created in Tally!

### Scenario 2: Monthly Expenses

You have monthly expense data.

1. Prepare Excel with: Date, Vendor, Amount, Description
2. Upload file
3. Select "Payment" voucher type
4. Map columns
5. Process

### Scenario 3: Customer Receipts

You received payments from multiple customers.

1. Prepare Excel with: Date, Customer, Amount
2. Upload file
3. Select "Receipt" voucher type
4. Process

---

## Tips for Best Results

### ✅ Do's

- Use consistent date formats
- Keep column names simple and clear
- Remove empty rows from Excel
- Use the first row for headers
- Test with a small file first (5-10 rows)

### ❌ Don'ts

- Don't use merged cells
- Don't include totals in data rows
- Don't use special characters in party names
- Don't leave required fields empty

---

## Understanding Errors

### "Date is empty"
**Cause**: Missing date in a row  
**Fix**: Fill in the date for that row

### "Amount must be positive"
**Cause**: Amount is zero or negative  
**Fix**: Check the amount value

### "Party Name is required"
**Cause**: Customer/Vendor name is missing  
**Fix**: Add the party name

### "Invalid date format"
**Cause**: Date is not in a recognized format  
**Fix**: Use DD-MM-YYYY or similar standard format

### "Tally error: ..."
**Cause**: Tally rejected the voucher  
**Fix**: Check Tally configuration and ledger names

---

## Ledger Management

### Auto-Create Ledgers

When enabled (default), the system will:
1. Check if party ledger exists in Tally
2. If not found, create it automatically
3. For Sales: Creates under "Sundry Debtors"
4. For Purchase: Creates under "Sundry Creditors"

### Manual Ledger Creation

If you prefer to create ledgers manually:
1. Uncheck "Automatically create missing ledgers"
2. Ensure all party names exist in Tally before processing
3. Errors will be shown for missing ledgers

---

## Best Practices

### 1. Start Small
- Test with 5-10 rows first
- Verify results in Tally
- Then process larger files

### 2. Backup Tally Data
- Always backup your Tally data before bulk imports
- Use Tally's backup feature

### 3. Review Mappings
- Don't blindly trust AI suggestions
- Always review the column mappings
- Check the preview data

### 4. Check Results
- Review the success/error report
- Verify entries in Tally
- Fix errors and re-process failed rows

### 5. Keep Excel Files
- Save your Excel files for reference
- Use descriptive file names
- Include date in filename (e.g., `sales_feb2026.xlsx`)

---

## Frequently Asked Questions

### Q: Can I import GST invoices?
**A**: Currently, the system supports simple entries without GST. GST support may be added in future versions.

### Q: What if my Excel has different column names?
**A**: The AI will try to map them automatically. You can also manually adjust the mappings.

### Q: Can I undo imported vouchers?
**A**: You need to delete vouchers manually in Tally. Always test with small files first!

### Q: How many rows can I import at once?
**A**: The system can handle thousands of rows, but start with smaller batches for testing.

### Q: What if some rows fail?
**A**: The system will show detailed errors. Fix the issues in Excel and re-upload just the failed rows.

---

## Getting Help

If you need assistance:

1. Check this user guide
2. Review the error messages carefully
3. Verify your Excel file format
4. Check Tally connection status
5. Refer to SETUP.md for configuration issues

---

## Summary

The Excel to Tally AI Agent makes data import simple:

1. 📊 Prepare Excel file
2. 📤 Upload file
3. 🎯 Select voucher type
4. ✅ Confirm mappings
5. 🚀 Process
6. ✨ Done!

Happy importing! 🎉
