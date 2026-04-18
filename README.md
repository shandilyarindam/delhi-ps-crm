# Delhi PS-CRM

**WhatsApp-based civic complaint management system for Delhi.**

Citizens file complaints via WhatsApp in Hindi or English. The system uses Gemini AI to classify and extract structured data, stores everything in Supabase, and auto-escalates unresolved complaints using a trained ML model. This production backend replaces a previous n8n automation prototype.

---

## Architecture

| Component                | Technology                        |
|--------------------------|-----------------------------------|
| Backend Framework        | FastAPI (Python 3.11+)            |
| Database & Auth          | Supabase (Postgres + Storage)     |
| AI Classification        | Google Gemini 2.0 Flash           |
| Messaging Channel        | WhatsApp Business API (Meta)      |
| Escalation Model         | GradientBoosting (scikit-learn)   |
| Email Notifications      | Gmail SMTP                        |
| Task Scheduling          | APScheduler (async, 30-min cycle) |
| Deployment               | Railway (Nixpacks)                |

---

## Repository Structure

```
Delhi-PS-CRM/
- delhi-ps-crm-backend/          # FastAPI backend
  - main.py                      # App entry point, lifespan, scheduler
  - config.py                    # Env var loading & validation, Supabase client
  - constants.py                 # Department emails, greetings, categories
  - requirements.txt             # Python dependencies
  - handlers/                    # Conversational state handlers
    - state_machine.py           # Routes messages by user state
    - registration.py            # New user registration
    - idle.py                    # Status check & new complaint trigger
    - filing.py                  # Complaint text, AI analysis, duplicate check
    - confirming.py              # Confirm, attach photo, submit
    - awaiting_photo.py          # WhatsApp image download, Supabase Storage
  - services/                    # External integrations
    - ai.py                      # Gemini AI complaint classifier
    - whatsapp.py                # WhatsApp Cloud API message sender
    - escalation.py              # ML model loader & predictor
    - escalation_cron.py         # Scheduled escalation job
    - email_service.py           # Gmail SMTP email notifications
    - storage.py                 # Supabase storage utilities
  - routers/                     # FastAPI route definitions
    - webhook.py                 # GET/POST /webhook for WhatsApp
    - notifications.py           # POST /notifications/assignment
  - models/                      # ML models & schemas
    - escalation_model.pkl       # Trained GradientBoosting model
    - schemas.py                 # Pydantic schemas
    - README.md                  # Model documentation
- delhi-ps-crm-dashboard.html    # Admin dashboard (standalone)
- index.html                     # Landing page
- ARCHITECTURE.md                # System architecture documentation
- DEMO.md                        # Demo walkthrough
- railway.toml                   # Railway deployment config
- .gitignore
```

---

## Setup

### Prerequisites

- Python 3.11+
- A Supabase project with `users` and `raw_complaints` tables
- A Meta WhatsApp Business API account
- A Google Gemini API key
- A Gmail account with an app password for SMTP

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/Delhi-PS-CRM.git
cd Delhi-PS-CRM/delhi-ps-crm-backend

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Copy `.env.example` to `.env` and fill in all values:

```bash
cp .env.example .env
```

| Variable                  | Description                                             | Required |
|---------------------------|---------------------------------------------------------|----------|
| `WHATSAPP_TOKEN`          | Meta WhatsApp Business API access token                 | Yes      |
| `WHATSAPP_PHONE_NUMBER_ID`| WhatsApp Business phone number ID from Meta dashboard   | Yes      |
| `WHATSAPP_VERIFY_TOKEN`   | Custom token for webhook verification handshake         | Yes      |
| `GEMINI_API_KEY`          | Google Gemini API key for complaint classification      | Yes      |
| `SUPABASE_URL`            | Supabase project URL                                    | Yes      |
| `SUPABASE_KEY`            | Supabase service role or anon key                       | Yes      |
| `HOD_WHATSAPP_NUMBER`     | WhatsApp number for HOD escalation alerts               | Yes      |
| `OPENAI_API_KEY`          | OpenAI key (reserved for future use)                    | No       |
| `GMAIL_ADDRESS`           | Gmail address for department email notifications        | No       |
| `GMAIL_APP_PASSWORD`      | Gmail app password (16-char, not account password)      | No       |

### Run

```bash
uvicorn main:app --reload --port 8000
```

The server starts at `http://localhost:8000`. Use ngrok or a tunnel to expose the webhook URL to Meta.

---

## API Endpoints

| Method | Path                        | Description                                  |
|--------|-----------------------------|----------------------------------------------|
| GET    | `/`                         | Application status check                     |
| GET    | `/health`                   | Health check with version info               |
| GET    | `/webhook`                  | WhatsApp webhook verification (Meta handshake)|
| POST   | `/webhook`                  | Receive incoming WhatsApp messages           |
| POST   | `/notifications/assignment` | Officer assignment and resolution alerts     |

---

## License

MIT -- see [LICENSE](LICENSE) for details.
