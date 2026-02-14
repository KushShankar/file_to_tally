# Setup Guide - Excel to Tally AI Agent

This guide will walk you through setting up the Excel to Tally AI Agent system from scratch.

## Prerequisites

Before you begin, ensure you have:

1. **Windows PC** with administrator access
2. **Tally Prime** installed and licensed
3. **Internet connection** for downloading dependencies
4. **OpenRouter API key** (free tier available)

---

## Step 1: Install Python

### Download Python

1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Download **Python 3.11** or later
3. Run the installer

### Important During Installation

✅ **Check "Add Python to PATH"** (very important!)  
✅ Click "Install Now"

### Verify Installation

Open Command Prompt (search for "cmd" in Windows) and type:

```bash
python --version
```

You should see: `Python 3.11.x` or similar

---

## Step 2: Get OpenRouter API Key

1. Go to [openrouter.ai](https://openrouter.ai)
2. Sign up for a free account
3. Go to **API Keys** section
4. Create a new API key
5. Copy the key (starts with `sk-or-v1-...`)

---

## Step 3: Download the Project

1. Download the project folder to your Desktop
2. You should have a folder called `tallyagent`

---

## Step 4: Install Python Dependencies

### Open Command Prompt in Project Folder

1. Press `Windows + R`
2. Type `cmd` and press Enter
3. Navigate to the backend folder:

```bash
cd Desktop\tallyagent\backend
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required Python packages. Wait for it to complete (may take 2-3 minutes).

---

## Step 5: Configure the Application

### Edit Configuration File

1. Open `backend\config.py` in Notepad
2. Find this line:

```python
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "sk-or-v1-...")
```

3. Replace the API key with your actual OpenRouter API key
4. Find this line:

```python
TALLY_COMPANY = os.getenv("TALLY_COMPANY", "TallyHealth")
```

5. Replace `"TallyHealth"` with your actual Tally company name
6. Save and close the file

---

## Step 6: Configure Tally Prime

### Enable HTTP Server in Tally

1. **Open Tally Prime**
2. Press `F12` (Configure)
3. Go to **Advanced Configuration**
4. Find **ODBC Server** section
5. Set the following:
   - **Enable ODBC Server**: Yes
   - **Port**: 9000
   - **Allow connections from**: All
6. Press `Ctrl + A` to accept
7. **Restart Tally Prime**

### Verify Tally Configuration

After restarting Tally:
1. Open your company
2. The ODBC server should be running on port 9000

---

## Step 7: Start the Application

### Run the Backend Server

In Command Prompt (in the `backend` folder):

```bash
python main.py
```

You should see:

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Keep this window open!** This is your server running.

---

## Step 8: Access the Web Interface

1. Open your web browser (Chrome, Firefox, or Edge)
2. Go to: **http://localhost:8000**
3. You should see the Excel to Tally AI Agent interface

### Check Connection Status

At the top of the page, you should see:
- 🟢 **Connected to Tally (TallyHealth)** - Good!
- 🔴 **Tally not connected** - Check Tally configuration

---

## Step 9: Test with Sample Data

### Create a Test Excel File

Create a new Excel file with these columns:

| Date       | Customer Name | Amount |
|------------|---------------|--------|
| 12-02-2026 | ABC Corp      | 10000  |
| 13-02-2026 | XYZ Ltd       | 15000  |

Save as `test_sales.xlsx`

### Upload and Process

1. Drag and drop the file into the upload zone
2. Select **Sales** voucher type
3. Confirm the AI-suggested mappings
4. Click **Process & Send to Tally**
5. Check Tally for the new vouchers!

---

## Troubleshooting

### "Python is not recognized"

**Problem**: Python not in PATH  
**Solution**: Reinstall Python and check "Add Python to PATH"

### "Cannot connect to Tally"

**Problem**: Tally ODBC server not running  
**Solution**: 
1. Check Tally is open
2. Verify ODBC server is enabled (F12 → Advanced Configuration)
3. Restart Tally

### "Module not found" errors

**Problem**: Dependencies not installed  
**Solution**: Run `pip install -r requirements.txt` again

### "Port 8000 already in use"

**Problem**: Another application using port 8000  
**Solution**: 
1. Close other applications
2. Or edit `main.py` and change port to 8001

### "OpenRouter API error"

**Problem**: Invalid API key  
**Solution**: 
1. Check your API key in `config.py`
2. Ensure it starts with `sk-or-v1-`
3. Verify you have credits in OpenRouter

---

## Next Steps

Once everything is working:

1. Read the **USER_GUIDE.md** for detailed usage instructions
2. Prepare your Excel files according to the format
3. Start importing data into Tally!

---

## Getting Help

If you encounter issues:

1. Check the error message carefully
2. Review this setup guide again
3. Check Tally configuration
4. Verify Python and dependencies are installed correctly

---

## Security Notes

⚠️ **Important**:
- Keep your OpenRouter API key private
- Don't share your `config.py` file
- The application runs locally on your computer
- No data is sent to external servers (except OpenRouter for AI mapping)
