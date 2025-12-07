# Complete Setup Guide

## Prerequisites

Before starting, ensure you have the following installed:

### Required Software

1. **Python 3.8 or higher**
   - Check version: `python --version` or `python3 --version`
   - Download: https://www.python.org/downloads/
   - Make sure to check "Add Python to PATH" during installation

2. **Node.js 16 or higher**
   - Check version: `node --version`
   - Download: https://nodejs.org/
   - This also installs npm (Node Package Manager)

3. **Git** (optional, for cloning)
   - Download: https://git-scm.com/downloads

### Required Accounts & Credentials

1. **OpenAI API Key**
   - Sign up at: https://platform.openai.com/
   - Get API key from: https://platform.openai.com/api-keys
   - Make sure you have credits in your OpenAI account

2. **Email Account with SMTP Access**
   - Gmail, Outlook, or any email provider with SMTP support
   - For Gmail: You'll need to create an "App Password" (see below)

## Step-by-Step Installation

### Step 1: Clone or Download the Project

If using Git:
```bash
git clone <repository-url>
cd RFP-ManagementSystem
```

Or download and extract the ZIP file, then navigate to the folder.

### Step 2: Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment (recommended):**
   
   **Windows:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
   
   **Mac/Linux:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment file:**
   ```bash
   # Windows
   copy env.example .env
   
   # Mac/Linux
   cp env.example .env
   ```

5. **Edit the `.env` file** with your credentials:
   
   Open `.env` in a text editor and fill in:
   ```env
   OPENAI_API_KEY=sk-your-actual-openai-api-key-here
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-app-password-here
   EMAIL_WEBHOOK_URL=http://localhost:8000/api/email/receive
   DATABASE_URL=sqlite:///./rfp_management.db
   ```

### Step 3: Get Gmail App Password (if using Gmail)

1. Go to your Google Account: https://myaccount.google.com/
2. Click **Security** → **2-Step Verification** (enable if not already)
3. Go to **App passwords**: https://myaccount.google.com/apppasswords
4. Select app: **Mail**
5. Select device: **Other (Custom name)** → Enter "RFP System"
6. Click **Generate**
7. Copy the 16-character password (use this as `SMTP_PASSWORD`)

**Note:** For other email providers, check their SMTP settings:
- **Outlook**: smtp-mail.outlook.com, port 587
- **Yahoo**: smtp.mail.yahoo.com, port 587
- **Custom**: Check your email provider's documentation

### Step 4: Frontend Setup

1. **Open a new terminal/command prompt** (keep backend terminal open)

2. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

3. **Install Node dependencies:**
   ```bash
   npm install
   ```
   
   This may take a few minutes. Wait for it to complete.

### Step 5: Run the Application

You need **two terminals** running simultaneously:

#### Terminal 1 - Backend Server

```bash
cd backend

# Activate virtual environment if you created one
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

The backend API will be available at: **http://localhost:8000**
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

#### Terminal 2 - Frontend Server

```bash
cd frontend
npm start
```

You should see:
```
Compiled successfully!

You can now view rfp-management-frontend in the browser.

  Local:            http://localhost:3000
```

The frontend will automatically open in your browser at: **http://localhost:3000**

### Step 6: Verify Installation

1. **Check Backend:**
   - Open browser: http://localhost:8000/api/health
   - Should return: `{"status":"healthy"}`

2. **Check Frontend:**
   - Should automatically open at http://localhost:3000
   - You should see the RFP Management System dashboard

3. **Check API Documentation:**
   - Open: http://localhost:8000/docs
   - You should see interactive API documentation

## First Time Usage

### 1. Add a Vendor

1. Click **"Vendors"** in the navigation
2. Click **"Add New Vendor"**
3. Fill in:
   - Name: e.g., "Tech Solutions Inc"
   - Email: e.g., "vendor@example.com" (use a real email if testing)
   - Other fields are optional
4. Click **"Create Vendor"**

### 2. Create Your First RFP

1. Click **"Create RFP"** in the navigation
2. In the chat interface, type something like:
   ```
   I need to procure laptops and monitors for our new office. 
   Budget is $50,000 total. Need delivery within 30 days. 
   We need 20 laptops with 16GB RAM and 15 monitors 27-inch. 
   Payment terms should be net 30, and we need at least 1 year warranty.
   ```
3. Click **"Send"**
4. Wait a few seconds for AI processing
5. You'll see the structured RFP created
6. You'll be automatically redirected to view the RFP

### 3. Send RFP to Vendors

1. Open the RFP you just created
2. Scroll to **"Send RFP to Vendors"** section
3. Check the boxes next to vendors you want to send to
4. Click **"Send RFP to X Vendor(s)"**
5. Emails will be sent via SMTP (requires valid SMTP credentials)

### 4. Test Receiving a Proposal

You can simulate a vendor response using the API:

**Using curl (Mac/Linux):**
```bash
curl -X POST http://localhost:8000/api/email/receive \
  -H "Content-Type: application/json" \
  -d '{
    "from_email": "vendor@example.com",
    "subject": "Re: Request for Proposal: Office Equipment",
    "body": "We are pleased to submit our proposal:\n\nTotal Price: $45,000\nDelivery: 25 days\nPayment Terms: Net 30\nWarranty: 1 year\n\n20 Laptops @ $1,500 each = $30,000\n15 Monitors @ $1,000 each = $15,000",
    "rfp_id": 1
  }'
```

**Using PowerShell (Windows):**
```powershell
$body = @{
    from_email = "vendor@example.com"
    subject = "Re: Request for Proposal: Office Equipment"
    body = "We are pleased to submit our proposal:`n`nTotal Price: $45,000`nDelivery: 25 days`nPayment Terms: Net 30`nWarranty: 1 year`n`n20 Laptops @ $1,500 each = $30,000`n15 Monitors @ $1,000 each = $15,000"
    rfp_id = 1
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/email/receive" -Method POST -Body $body -ContentType "application/json"
```

**Or use the API docs:**
1. Go to http://localhost:8000/docs
2. Find `POST /api/email/receive`
3. Click "Try it out"
4. Fill in the request body
5. Click "Execute"

### 5. Compare Proposals

1. Create at least 2 proposals for the same RFP (repeat step 4 with different vendors)
2. Open the RFP detail page
3. Scroll to the **"Proposals"** section
4. Click **"Compare & Get Recommendation"**
5. View the AI-powered comparison and recommendation

## Troubleshooting

### Backend Issues

**Problem: `python: command not found`**
- **Solution**: Use `python3` instead, or add Python to your PATH

**Problem: `ModuleNotFoundError`**
- **Solution**: Make sure you activated the virtual environment and ran `pip install -r requirements.txt`

**Problem: `OPENAI_API_KEY` not found**
- **Solution**: Check your `.env` file exists in the `backend` directory and has the correct key

**Problem: Database errors**
- **Solution**: Delete `rfp_management.db` in the backend directory and restart (database will be recreated)

**Problem: Port 8000 already in use**
- **Solution**: Change port in `main.py` or kill the process using port 8000

### Frontend Issues

**Problem: `npm: command not found`**
- **Solution**: Install Node.js from https://nodejs.org/

**Problem: `npm install` fails**
- **Solution**: 
  - Delete `node_modules` folder
  - Delete `package-lock.json`
  - Run `npm install` again
  - If still fails, try `npm install --legacy-peer-deps`

**Problem: Port 3000 already in use**
- **Solution**: 
  - The terminal will ask if you want to use a different port (type 'y')
  - Or kill the process using port 3000

**Problem: CORS errors in browser console**
- **Solution**: Make sure backend is running and CORS is configured for localhost:3000

### Email Issues

**Problem: SMTP authentication failed**
- **Solution**: 
  - For Gmail: Make sure you're using an App Password, not your regular password
  - Check SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD in `.env`
  - Verify 2-factor authentication is enabled (for Gmail)

**Problem: Email sending times out**
- **Solution**: 
  - Check firewall settings
  - Verify SMTP port (587 for TLS, 465 for SSL)
  - Try a different email provider

### AI/OpenAI Issues

**Problem: AI features not working**
- **Solution**: 
  - Verify `OPENAI_API_KEY` is correct in `.env`
  - Check you have credits in your OpenAI account
  - Check API key permissions at https://platform.openai.com/api-keys
  - Look at backend terminal for error messages

**Problem: Rate limit errors**
- **Solution**: You've hit OpenAI's rate limit. Wait a few minutes and try again, or upgrade your OpenAI plan

## Development Tips

### Viewing API Documentation

FastAPI automatically generates interactive API docs:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Database Location

The SQLite database is created at:
- **Location**: `backend/rfp_management.db`
- **To reset**: Delete this file and restart the backend

### Environment Variables

All environment variables are in `backend/.env`:
- Never commit this file (it's in `.gitignore`)
- Use `backend/env.example` as a template

### Logs

- **Backend logs**: Check the terminal where you ran `python main.py`
- **Frontend logs**: Check the browser console (F12) and the terminal where you ran `npm start`

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [QUICKSTART.md](QUICKSTART.md) for a condensed guide
- Explore the API at http://localhost:8000/docs
- Customize email templates in `backend/email_service.py`
- Add more features as needed!

## Getting Help

If you encounter issues:
1. Check the Troubleshooting section above
2. Review error messages in the terminal/browser console
3. Verify all prerequisites are installed correctly
4. Ensure all environment variables are set
5. Check that both backend and frontend servers are running
