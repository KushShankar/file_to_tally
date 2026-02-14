# Excel to Tally AI Agent

🚀 **Automatically convert Excel sales/purchase data into Tally-compatible XML format and import it into Tally Prime**

## Features

✅ **AI-Powered Column Mapping** - Automatically detects and maps Excel columns to Tally fields  
✅ **Multiple Voucher Types** - Supports Sales, Purchase, Payment, Receipt, and Journal vouchers  
✅ **Auto-Create Ledgers** - Automatically creates missing party ledgers in Tally  
✅ **Smart Validation** - Validates dates, amounts, and required fields before processing  
✅ **User-Friendly Interface** - Simple drag-and-drop web interface  
✅ **Error Reporting** - Detailed error messages for failed entries  

## System Requirements

- **Python 3.8+**
- **Tally Prime** (running locally)
- **Modern web browser** (Chrome, Firefox, Edge)
- **OpenRouter API key** (for AI features)

## Quick Start

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Tally Prime

1. Open Tally Prime
2. Go to **Gateway of Tally → F12: Configure → Advanced Configuration**
3. Enable **ODBC Server** on port **9000**
4. Restart Tally

### 3. Start the Application

#### Option A: One-Click Launcher (Recommended)

**Windows:**
Double-click `run.bat`

**Linux/Mac:**
Run `./run_linux.sh` in your terminal.

#### Option B: Manual Start

```bash
cd backend
python main.py
```

The application will start at: **http://localhost:8000** and automatically open in your default browser.

### 4. Use the Web Interface

1. Open your browser and go to `http://localhost:8000`
2. Upload your Excel file
3. Select voucher type
4. Confirm column mappings (AI will suggest mappings)
5. Click "Process & Send to Tally"

## Excel File Format

Your Excel file should contain the following columns (column names can vary):

### For Sales Vouchers:
- **Date** - Transaction date (DD-MM-YYYY or any common format)
- **Customer Name** - Party name
- **Amount** - Total amount
- **Invoice Number** (optional)
- **Narration** (optional)

### For Purchase Vouchers:
- **Date** - Transaction date
- **Vendor Name** - Party name
- **Amount** - Total amount
- **Invoice Number** (optional)
- **Narration** (optional)

### For Payment/Receipt Vouchers:
- **Date** - Transaction date
- **Party Name** - Party name
- **Amount** - Total amount
- **Narration** (optional)

## Configuration

Edit `backend/config.py` to customize:

```python
TALLY_URL = "http://localhost:9000"  # Tally server URL
TALLY_COMPANY = "TallyHealth"         # Your company name
OPENROUTER_API_KEY = "your-api-key"   # Your OpenRouter API key
```

## Project Structure

```
tallyagent/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration
│   ├── requirements.txt        # Python dependencies
│   ├── models/
│   │   └── schemas.py          # Pydantic models
│   ├── services/
│   │   ├── excel_parser.py     # Excel parsing
│   │   ├── ai_mapper.py        # AI column mapping
│   │   ├── validator.py        # Data validation
│   │   ├── xml_generator.py    # Tally XML generation
│   │   └── tally_client.py     # Tally HTTP client
│   └── routes/
│       └── upload.py           # API routes
├── frontend/
│   ├── index.html              # Web interface
│   ├── style.css               # Styling
│   └── app.js                  # Frontend logic
├── samples/
│   ├── sales_sample.xlsx       # Sample sales file
│   └── sample_output.xml       # Sample XML output
└── docs/
    ├── SETUP.md                # Detailed setup guide
    └── USER_GUIDE.md           # User manual
```

## API Endpoints

- `POST /api/upload` - Upload Excel file and get AI-suggested mappings
- `POST /api/process` - Process file and send to Tally
- `GET /api/ledgers` - Get all ledgers from Tally
- `GET /api/health` - Check Tally connection status

## Troubleshooting

### Tally Connection Failed
- Ensure Tally Prime is running
- Check that ODBC server is enabled on port 9000
- Verify company name in `config.py` matches Tally

### Upload Failed
- Check file format (.xlsx, .xls, or .csv)
- Ensure file is not corrupted
- Check file size (max 10MB)

### Processing Errors
- Verify required columns are mapped (Date, Party Name, Amount)
- Check date format in Excel
- Ensure amounts are numeric

## License

MIT License - Free to use and modify

## Support

For issues and questions, please check the documentation in the `docs/` folder.
