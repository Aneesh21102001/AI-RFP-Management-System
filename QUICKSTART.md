# Quick Start Guide

## Initial Setup (5 minutes)

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Create environment file
cp env.example .env

# Edit .env file with your credentials:
# - OPENAI_API_KEY (get from https://platform.openai.com/api-keys)
# - SMTP credentials (Gmail, Outlook, etc.)
```

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install
```

### 3. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```
Backend will run on http://localhost:8000

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```
Frontend will run on http://localhost:3000

### 4. Access the Application

Open your browser to http://localhost:3000

## First Steps

1. **Add Vendors**: Go to "Vendors" → "Add New Vendor"
   - Add at least one vendor with email address

2. **Create Your First RFP**: Go to "Create RFP"
   - Type something like: "I need 10 laptops with 16GB RAM, budget $20,000, delivery in 30 days"
   - The AI will create a structured RFP

3. **Send RFP**: 
   - Open the created RFP
   - Select vendors
   - Click "Send RFP" (requires SMTP configuration)

4. **Receive Proposal** (for testing):
   - Use the API endpoint: `POST /api/email/receive`
   - Or manually create a proposal through the API

5. **Compare Proposals**:
   - When you have 2+ proposals for an RFP
   - Click "Compare & Get Recommendation"
   - View AI-powered analysis

## Testing Email Receiving

You can test the email receiving functionality using curl:

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

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (needs 3.8+)
- Verify all dependencies installed: `pip list`
- Check .env file exists and has valid credentials

### Frontend won't start
- Check Node version: `node --version` (needs 16+)
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`

### Email sending fails
- Verify SMTP credentials in .env
- For Gmail: Use App Password, not regular password
- Check firewall/network allows SMTP connections

### AI features not working
- Verify OPENAI_API_KEY is set correctly
- Check you have API credits on OpenAI account
- Check API key has proper permissions

## Next Steps

- Read the full README.md for detailed documentation
- Explore the API documentation at http://localhost:8000/docs
- Customize email templates in `backend/email_service.py`
- Add more vendors and create more RFPs
