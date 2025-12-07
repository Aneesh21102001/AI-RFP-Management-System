# RFP Management System

A single-user web application for procurement managers to create RFPs, manage vendors, receive proposals, and compare vendor responses using AI.

## Features

- **Create RFPs**: Natural language input converted to structured RFPs using AI
- **Vendor Management**: Maintain vendor master data and contact information
- **Send RFPs**: Email RFPs to selected vendors via SMTP
- **Receive Responses**: Parse vendor email responses automatically with AI extraction
- **AI Extraction**: Extract key details (prices, terms, conditions) from vendor responses
- **Compare & Recommend**: AI-powered comparison and vendor recommendations

## Tech Stack

### Core Technologies

- **Backend**: FastAPI (Python)
- **Frontend**: React with JavaScript
- **Database**: SQLite (via SQLAlchemy)
- **AI Provider**: OpenAI GPT-4 (via openai)
- **Email**: SMTP via aiosmtplib
- **API Client**: Axios
- **Routing**: React Router DOM

### Key Libraries

**Backend:**
- `pydantic` 2.5.0 - Data validation and settings
- `python-dotenv` 1.0.0 - Environment variable management
- `uvicorn` 0.24.0 - ASGI server

**Frontend:**
- `react-scripts` 5.0.1 - Build tooling
- `react-router-dom` 6.20.1 - Client-side routing

### Why These Choices?

- **Backend: FastAPI (Python)**: Fast, modern, async-capable framework with excellent API documentation. Python has strong AI/ML ecosystem support.
- **Frontend: React with JavaScript**: Industry-standard, type-safe, component-based UI framework
- **Database: SQLite**: Perfect for single-user applications - no setup required, file-based, reliable
- **AI: OpenAI GPT-4**: State-of-the-art language model for natural language understanding and extraction
- **Email: SMTP (aiosmtplib)**: Standard protocol, works with any email provider

## Architecture & Design Decisions

### RFP Structure
RFPs are stored with:
- Core metadata (title, description, budget, delivery timeline)
- Payment terms and warranty requirements
- Items array with quantities and specifications (flexible JSON structure)
- Additional requirements array
- Status tracking (draft, sent, closed)

### AI Integration Points

1. **Natural Language to RFP**: Uses GPT-4 to parse free-form procurement requests into structured RFP format
2. **Email Parsing**: Extracts proposal details from vendor email responses, handling messy formats, tables, and unstructured text
3. **Comparison & Recommendation**: Analyzes multiple proposals considering price, delivery, terms, completeness, and alignment with requirements

### UI/UX Design

- **Chat Interface for RFP Creation**: Natural, conversational flow for describing procurement needs
- **Dashboard**: Overview of RFPs, vendors, and proposals
- **Detail Views**: Comprehensive RFP and proposal details with comparison tables
- **Vendor Management**: Simple CRUD interface for maintaining vendor data

### Email Handling

- **Sending**: SMTP-based email sending with formatted HTML/text RFP documents
- **Receiving**: REST API endpoint for receiving emails (can be connected to email webhook services like SendGrid, Mailgun, or IMAP polling)

## Setup

### Prerequisites

- Python 3.8+
- Node.js 16+
- OpenAI API key
- Email account with SMTP access (Gmail, Outlook, etc.)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Copy environment example and configure
cp env.example .env
# Edit .env with your credentials

# Run the server
python main.py
```

The backend will run on `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will run on `http://localhost:3000`

## Environment Variables

Create a `.env` file in the `backend` directory (see `backend/env.example`):

```env
OPENAI_API_KEY=your_openai_api_key
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_WEBHOOK_URL=http://localhost:8000/api/email/receive
DATABASE_URL=sqlite:///./rfp_management.db
```

### Getting SMTP Credentials

For Gmail:
1. Enable 2-factor authentication
2. Generate an "App Password" in your Google Account settings
3. Use that app password as `SMTP_PASSWORD`

## Usage

### Creating an RFP

1. Navigate to "Create RFP"
2. Describe your procurement needs in natural language, e.g.:
   > "I need to procure laptops and monitors for our new office. Budget is $50,000 total. Need delivery within 30 days. We need 20 laptops with 16GB RAM and 15 monitors 27-inch. Payment terms should be net 30, and we need at least 1 year warranty."
3. The AI will parse this and create a structured RFP
4. Review and edit if needed

### Managing Vendors

1. Go to "Vendors" section
2. Add vendors with their contact information
3. Edit or delete as needed

### Sending RFPs

1. Open an RFP (status: draft)
2. Select vendors to send to
3. Click "Send RFP" - emails will be sent automatically

### Receiving Proposals

When a vendor replies via email:
1. Use the `/api/email/receive` endpoint (POST) with:
   ```json
   {
     "from_email": "vendor@example.com",
     "subject": "Re: Request for Proposal: Office Equipment",
     "body": "Here is our proposal...",
     "rfp_id": 1
   }
   ```
2. The system will:
   - Match vendor by email
   - Extract proposal details using AI
   - Store structured proposal data
   - Calculate completeness score

### Comparing Proposals

1. Open an RFP with multiple proposals
2. Click "Compare & Get Recommendation"
3. View AI-powered comparison with:
   - Overall scores for each vendor
   - Strengths and weaknesses
   - Price and delivery rankings
   - Recommended vendor with reasoning

## API Documentation

### RFPs

#### `GET /api/rfps`
List all RFPs.

**Response:**
```json
[
  {
    "id": 1,
    "title": "Office Equipment Procurement",
    "description": "Laptops and monitors for new office",
    "budget": 50000.0,
    "delivery_days": 30,
    "payment_terms": "net 30",
    "warranty_required": "1 year",
    "items": [
      {
        "name": "Laptop",
        "quantity": 20,
        "specifications": {"RAM": "16GB"}
      }
    ],
    "requirements": ["Must be new", "Warranty required"],
    "status": "draft",
    "created_at": "2024-01-15T10:00:00",
    "updated_at": "2024-01-15T10:00:00"
  }
]
```

#### `POST /api/rfps/from-text`
Create RFP from natural language input.

**Request Body:**
```json
{
  "text": "I need to procure laptops and monitors for our new office. Budget is $50,000 total. Need delivery within 30 days. We need 20 laptops with 16GB RAM and 15 monitors 27-inch. Payment terms should be net 30, and we need at least 1 year warranty."
}
```

**Response:** Same as RFP object above

**Error Response (400):**
```json
{
  "detail": "Failed to create RFP: Invalid input format"
}
```

#### `GET /api/rfps/{id}`
Get specific RFP details.

**Response:** Single RFP object

**Error Response (404):**
```json
{
  "detail": "RFP not found"
}
```

#### `PUT /api/rfps/{id}`
Update an RFP.

**Request Body:**
```json
{
  "title": "Updated Title",
  "status": "sent",
  "budget": 55000.0
}
```

**Response:** Updated RFP object

#### `DELETE /api/rfps/{id}`
Delete an RFP.

**Response:**
```json
{
  "message": "RFP deleted successfully"
}
```

### Vendors

#### `GET /api/vendors`
List all vendors.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Tech Solutions Inc",
    "email": "contact@techsolutions.com",
    "phone": "+1-555-0123",
    "address": "123 Tech St, San Francisco, CA",
    "contact_person": "John Doe",
    "notes": "Preferred vendor for IT equipment",
    "created_at": "2024-01-10T10:00:00",
    "updated_at": "2024-01-10T10:00:00"
  }
]
```

#### `POST /api/vendors`
Create a new vendor.

**Request Body:**
```json
{
  "name": "Tech Solutions Inc",
  "email": "contact@techsolutions.com",
  "phone": "+1-555-0123",
  "address": "123 Tech St, San Francisco, CA",
  "contact_person": "John Doe",
  "notes": "Preferred vendor for IT equipment"
}
```

**Response:** Created vendor object

#### `GET /api/vendors/{id}`
Get specific vendor details.

**Response:** Single vendor object

#### `PUT /api/vendors/{id}`
Update a vendor.

**Request Body:**
```json
{
  "phone": "+1-555-9999",
  "notes": "Updated notes"
}
```

**Response:** Updated vendor object

#### `DELETE /api/vendors/{id}`
Delete a vendor.

**Response:**
```json
{
  "message": "Vendor deleted successfully"
}
```

### Proposals

#### `GET /api/proposals?rfp_id={id}`
List proposals, optionally filtered by RFP ID.

**Query Parameters:**
- `rfp_id` (optional): Filter by RFP ID

**Response:**
```json
[
  {
    "id": 1,
    "rfp_id": 1,
    "vendor_id": 1,
    "total_price": 48000.0,
    "delivery_days": 25,
    "payment_terms": "net 30",
    "warranty": "1 year",
    "items": [
      {
        "name": "Laptop",
        "quantity": 20,
        "unit_price": 1500.0,
        "total_price": 30000.0
      }
    ],
    "terms_conditions": "Standard terms apply",
    "completeness_score": 0.95,
    "received_at": "2024-01-20T14:30:00",
    "created_at": "2024-01-20T14:30:00",
    "updated_at": "2024-01-20T14:30:00",
    "vendor": {
      "id": 1,
      "name": "Tech Solutions Inc",
      "email": "contact@techsolutions.com"
    }
  }
]
```

#### `GET /api/proposals/rfp/{rfp_id}/compare`
Compare proposals for an RFP and get AI recommendations.

**Response:**
```json
{
  "comparison": [
    {
      "vendor_name": "Tech Solutions Inc",
      "score": 87.5,
      "strengths": [
        "Best price",
        "Fastest delivery",
        "Complete response"
      ],
      "weaknesses": [
        "Slightly above budget"
      ],
      "price_rank": 1,
      "delivery_rank": 1
    }
  ],
  "recommendation": {
    "recommended_vendor": "Tech Solutions Inc",
    "reason": "Tech Solutions Inc offers the best overall value with competitive pricing, fast delivery, and complete proposal that meets all requirements.",
    "summary": "Recommended vendor balances cost, delivery speed, and proposal completeness."
  }
}
```

**Error Response (404):**
```json
{
  "detail": "No proposals found for this RFP"
}
```

### Email

#### `POST /api/email/send-rfp`
Send RFP to selected vendors via email.

**Request Body:**
```json
{
  "rfp_id": 1,
  "vendor_ids": [1, 2, 3]
}
```

**Response:**
```json
{
  "message": "RFP sending completed",
  "results": [
    {
      "vendor_id": 1,
      "vendor_name": "Tech Solutions Inc",
      "status": "sent"
    },
    {
      "vendor_id": 2,
      "vendor_name": "Another Vendor",
      "status": "failed",
      "error": "SMTP connection failed"
    }
  ]
}
```

**Error Response (404):**
```json
{
  "detail": "RFP not found"
}
```

#### `POST /api/email/receive`
Receive and parse vendor email response.

**Request Body:**
```json
{
  "from_email": "vendor@example.com",
  "subject": "Re: Request for Proposal: Office Equipment",
  "body": "We are pleased to submit our proposal:\n\nTotal Price: $45,000\nDelivery: 25 days\nPayment Terms: Net 30\nWarranty: 1 year\n\n20 Laptops @ $1,500 each = $30,000\n15 Monitors @ $1,000 each = $15,000",
  "rfp_id": 1
}
```

**Response:** Created/updated Proposal object with extracted data

**Error Response (404):**
```json
{
  "detail": "Vendor with email vendor@example.com not found"
}
```

**Error Response (500):**
```json
{
  "detail": "Failed to parse email: AI extraction failed"
}
```

## Decisions & Assumptions

### Data Modeling

**RFP Structure:**
- **Decision**: Used flexible JSON fields for `items` and `requirements` to accommodate varying RFP structures
- **Reasoning**: Different procurement needs have different item types and specifications. A rigid schema would be too limiting.
- **Trade-off**: Less type safety at database level, but more flexibility for real-world use cases

**Proposal Extraction:**
- **Decision**: Store both `raw_response` (original email) and `extracted_data` (AI-parsed structured data)
- **Reasoning**: Allows auditing of AI extraction accuracy and manual correction if needed
- **Assumption**: Vendor emails will be in English and contain proposal information in the body text

**Completeness Score:**
- **Decision**: Calculate 0-1 score based on how well proposal addresses RFP requirements
- **Reasoning**: Helps quickly identify incomplete proposals that need follow-up
- **Assumption**: All RFP requirements are equally important (could be enhanced with weighted scoring)

### AI Integration

**Model Choice: GPT-4:**
- **Decision**: Use GPT-4 for all AI tasks (parsing, extraction, comparison)
- **Reasoning**: GPT-4 provides superior accuracy for complex extraction tasks compared to GPT-3.5
- **Trade-off**: Higher cost, but better accuracy is critical for procurement decisions

**Prompting Strategy:**
- **Decision**: Use structured JSON output with explicit instructions and examples
- **Reasoning**: Reduces parsing errors and ensures consistent data format
- **Assumption**: AI will reliably return valid JSON (handled with error handling and retry logic)

**Temperature Setting:**
- **Decision**: Use temperature=0.3 for all AI calls
- **Reasoning**: Lower temperature ensures more deterministic, consistent outputs for structured data extraction
- **Trade-off**: Less creative, but creativity not needed for data extraction

### Email Handling

**SMTP for Sending:**
- **Decision**: Use standard SMTP instead of email service APIs (SendGrid, Mailgun)
- **Reasoning**: Works with any email provider, no additional service dependencies
- **Assumption**: User has access to SMTP credentials (Gmail, Outlook, etc.)

**Email Receiving:**
- **Decision**: REST API endpoint instead of IMAP polling
- **Reasoning**: Simpler to implement, can be connected to webhook services (SendGrid, Mailgun) for production
- **Assumption**: For single-user demo, manual/automated webhook forwarding is acceptable
- **Future**: Could add IMAP polling for automatic receiving

**Email Parsing:**
- **Decision**: Parse email body text only, not attachments initially
- **Reasoning**: Most vendor responses contain key info in email body
- **Assumption**: Attachments (PDFs, Word docs) are supplementary, not primary proposal content
- **Future**: Could add PDF/Word parsing for attachments

### UI/UX Design

**Chat Interface for RFP Creation:**
- **Decision**: Conversational chat UI instead of multi-step form wizard
- **Reasoning**: More natural for describing procurement needs, reduces cognitive load
- **Assumption**: Users prefer describing needs naturally rather than filling structured forms

**Comparison View:**
- **Decision**: Show both detailed comparison table and AI recommendation
- **Reasoning**: Users need both data (for transparency) and recommendation (for decision support)
- **Assumption**: Users want to understand why a vendor is recommended, not just see a score

**Status Tracking:**
- **Decision**: Simple status field (draft, sent, closed) instead of complex workflow
- **Reasoning**: Single-user app doesn't need approval workflows or versioning
- **Assumption**: User manages RFP lifecycle manually

### Technical Decisions

**SQLite Database:**
- **Decision**: Use SQLite instead of PostgreSQL/MySQL
- **Reasoning**: Single-user application, no setup required, file-based is perfect
- **Assumption**: Data volume will be manageable for single user (< 10,000 records)
- **Trade-off**: No concurrent write support, but not needed for single-user

**FastAPI over Flask/Django:**
- **Decision**: FastAPI for async support and automatic API docs
- **Reasoning**: Better performance for I/O-bound operations (AI calls, email sending)
- **Assumption**: Will benefit from async/await for concurrent operations

**React with JavaScript:**
- **Decision**: JavaScript for type safety in frontend
- **Reasoning**: Catches errors at compile time, better IDE support
- **Assumption**: Type safety worth the additional setup complexity

### Limitations & Known Issues

1. **Email Receiving**: Requires manual webhook setup or API calls. No automatic IMAP polling.
2. **Attachment Parsing**: PDF/Word attachments not parsed (email body only).
3. **Multi-language**: Assumes English for AI parsing (could be enhanced).
4. **Error Recovery**: Limited retry logic for AI API failures.
5. **Data Validation**: Some AI-extracted data may need manual verification.
6. **Email Format**: Assumes vendors reply in standard email format (not complex HTML with nested tables).

## AI Tools Usage

### Tools Used

- **Cursor AI**: Primary development assistant
- **OpenAI GPT-4**: Runtime AI for natural language processing

### What AI Helped With

#### 1. **Initial Architecture & Design**
- **Prompt**: "Design a single-user RFP management system with AI integration"
- **Help**: Generated initial project structure, database schema design, and API endpoint planning
- **Outcome**: Solid foundation that guided the entire implementation

#### 2. **Database Schema Design**
- **Prompt**: "Design database models for RFPs, vendors, and proposals with relationships"
- **Help**: Suggested flexible JSON fields for items/specifications, completeness scoring approach
- **Learning**: Realized need for both structured and flexible fields to handle varied procurement needs

#### 3. **AI Service Implementation**
- **Prompt**: "Create prompts for GPT-4 to extract structured data from natural language and emails"
- **Help**: Refined prompts for reliable JSON extraction, suggested temperature settings
- **Iteration**: Started with simpler prompts, iterated to include examples and explicit JSON format requirements

#### 4. **Frontend Component Structure**
- **Prompt**: "Create React components for RFP management with JavaScript"
- **Help**: Generated component structure, API client patterns, routing setup
- **Refinement**: Simplified initial complex state management to more straightforward patterns

#### 5. **Email Template Design**
- **Prompt**: "Create professional RFP email template with HTML formatting"
- **Help**: Generated both text and HTML versions with proper formatting
- **Enhancement**: Added structured item lists and requirements sections

#### 6. **Error Handling Patterns**
- **Prompt**: "Best practices for error handling in FastAPI with AI service calls"
- **Help**: Suggested try-catch patterns, user-friendly error messages, graceful degradation
- **Implementation**: Added comprehensive error handling throughout

### Notable Prompts & Approaches

#### Effective Prompt Pattern for AI Extraction:
```
You are an AI assistant that extracts [data type] from [source].
[Context about what to extract]
Return ONLY valid JSON, no additional text.
```


This pattern consistently produced reliable JSON output.

#### Iterative Refinement:
- Started with basic extraction prompts
- Added RFP context to extraction prompts (improved accuracy)
- Added explicit field descriptions and examples
- Final version includes both requirements and response context

### What Changed During Development

1. **Initial Plan**: Simple form-based RFP creation
   - **Changed to**: Chat interface after realizing natural language is more intuitive
   - **Reason**: AI tools suggested conversational UI would be better UX

2. **Initial Plan**: Store extracted data only
   - **Changed to**: Store both raw and extracted data
   - **Reason**: Realized need for auditing and manual correction capability

3. **Initial Plan**: Simple price comparison
   - **Changed to**: Multi-factor scoring with strengths/weaknesses
   - **Reason**: AI tools suggested richer comparison would be more valuable

4. **Initial Plan**: Single AI call for comparison
   - **Changed to**: Structured comparison with rankings and recommendations
   - **Reason**: More actionable insights for decision-making

### Key Learnings

1. **Prompt Engineering Matters**: Small changes in prompts significantly affect output quality
2. **Context is Critical**: Providing RFP requirements to extraction prompts improved accuracy
3. **Error Handling**: AI calls can fail in various ways - need robust error handling
4. **User Experience**: Natural language interfaces feel more intuitive than forms
5. **Flexibility vs Structure**: Balance between structured data and flexibility is crucial

### AI-Generated Code Quality

- **Boilerplate**: ~60% of initial code structure (components, API routes, database models)
- **Business Logic**: ~30% (AI service prompts, email templates, comparison logic)
- **Custom Implementation**: ~10% (specific error handling, UI refinements, integration points)

Most AI-generated code required refinement for:
- Error handling specifics
- Type safety improvements
- User experience polish
- Integration between components

## Development

The application uses:
- FastAPI with automatic API documentation at `http://localhost:8000/docs`
- React with JavaScript for type safety
- SQLite database (file: `rfp_management.db` in backend directory)

## Future Enhancements

- IMAP polling for automatic email receiving
- Attachment parsing (PDF, Word documents)
- Email templates customization
- Export proposals to PDF/Excel
- Advanced filtering and search
- Multi-user support with authentication
- Weighted scoring for proposal comparison
- Multi-language support for AI parsing
- Email tracking and read receipts
- Proposal versioning and history
