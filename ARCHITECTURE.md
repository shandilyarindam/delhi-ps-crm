# 🏗️ Architecture — Delhi PS-CRM

> Technical deep-dive into the system design, data flow, and component interactions.

---

## Table of Contents
- [System Overview](#system-overview)
- [Full System Flow](#full-system-flow)
- [Component Breakdown](#component-breakdown)
- [n8n Workflows](#n8n-workflows)
- [WhatsApp State Machine](#whatsapp-state-machine)
- [Database Schema](#database-schema)
- [API Integrations](#api-integrations)
- [Real-time Architecture](#real-time-architecture)
- [Security Model](#security-model)

---

## System Overview

Delhi PS-CRM is a **5-component system** connected through event-driven workflows:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SYSTEM OVERVIEW                                    │
│                                                                               │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐ │
│  │ WhatsApp │──▶│   n8n    │──▶│  OpenAI  │   │ Supabase │◀──│Dashboard │ │
│  │ Business │◀──│Workflows │◀──│  GPT-4o  │   │ Postgres │──▶│  (HTML)  │ │
│  │   API    │   │ (3 flows)│   │          │   │ Realtime │   │          │ │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘ │
│                                                                               │
│  Citizen I/O     Orchestration   Intelligence    Storage       Admin UI       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Full System Flow

```
                           DELHI PS-CRM — FULL DATA FLOW
 ═══════════════════════════════════════════════════════════════════════════════

 CITIZEN LAYER                    PROCESSING LAYER                 ADMIN LAYER
 ─────────────                    ────────────────                 ───────────
                                                                           
 ┌──────────────┐                ┌──────────────┐                          
 │   Citizen    │   WhatsApp     │              │                          
 │   sends      │───Message────▶│   n8n        │                          
 │   "Hi"       │   (webhook)   │   Workflow 1 │                          
 └──────────────┘                │   (Intake)   │                          
        │                        │              │                          
        │                        └──────┬───────┘                          
        │                               │                                  
        ▼                               ▼                                  
 ┌──────────────┐                ┌──────────────┐                          
 │   Citizen    │                │  Check user  │                          
 │   provides   │◀──Bot asks──  │  state in    │                          
 │   name       │   for name    │  Supabase    │                          
 └──────┬───────┘                └──────┬───────┘                          
        │                               │                                  
        ▼                               ▼                                  
 ┌──────────────┐                ┌──────────────┐                          
 │   Citizen    │                │  Register    │                          
 │   describes  │◀──Bot asks──  │  new user    │                          
 │   complaint  │   for issue   │  state→filing│                          
 └──────┬───────┘                └──────┬───────┘                          
        │                               │                                  
        │  "Gali mein kachra            ▼                                  
        │   pada hai bahut"      ┌──────────────┐     ┌──────────────┐    
        │                       │   n8n        │────▶│   OpenAI     │    
        └──────────────────────▶│   Workflow 2 │     │   GPT-4o     │    
                                │   (AI Class) │◀────│              │    
                                │              │     │ • Category   │    
                                └──────┬───────┘     │ • Urgency    │    
                                       │             │ • Sentiment  │    
                                       │             │ • Location   │    
                                       │             │ • Summary    │    
                                       ▼             └──────────────┘    
                                ┌──────────────┐                          
                                │  Store in    │                          
                                │  Supabase    │                          
                                │  raw_        │                          
                                │  complaints  │                          
                                └──────┬───────┘                          
                                       │                                  
                                       │  Realtime                        
                                       │  subscription                    
                                       ▼                                  
                                                          ┌──────────────┐
                                                          │  Dashboard   │
                                                          │              │
                                                          │ • Table      │
                                                          │ • Charts     │
                                                          │ • Map        │
                                                          │ • Kanban     │
                                                          │ • Scorecard  │
                                                          └──────┬───────┘
                                                                 │        
                                       ┌─────────────────────────┘        
                                       │  Officer action                  
                                       │  (Assign/Resolve)               
                                       ▼                                  
                                ┌──────────────┐                          
                                │  Update      │                          
                                │  Supabase    │                          
                                │  status      │                          
                                └──────┬───────┘                          
                                       │                                  
                                       ▼                                  
                                ┌──────────────┐     ┌──────────────┐    
                                │   n8n        │────▶│   WhatsApp   │    
                                │   Workflow 3 │     │   → Citizen  │    
                                │   (Notify)   │     │   "Resolved!"│    
                                └──────────────┘     └──────────────┘    
```

---

## Component Breakdown

### 1. WhatsApp Business API
**Role:** Citizen-facing interface — the only touchpoint citizens interact with.

- Receives incoming messages (text + images) via webhook
- Sends structured responses and status updates
- Handles message templates for notifications
- Supports rich media (photos, documents)

**Why WhatsApp?**
- 500M+ users in India
- No app installation needed
- Works on basic smartphones
- Native Hindi keyboard support
- End-to-end encrypted

### 2. n8n Workflow Engine
**Role:** Central orchestration layer — connects all services together.

- Self-hosted for data sovereignty
- 3 distinct workflows handling the complaint lifecycle
- Webhook-triggered from WhatsApp
- Database-triggered from Supabase
- Handles conditional routing, error handling, and retries

### 3. OpenAI GPT-4o
**Role:** AI intelligence layer — understanding and classifying citizen complaints.

- **Language Understanding:** Processes Hindi, Hinglish, and English natively
- **Classification:** Maps free-text to one of 6 categories
- **Urgency Detection:** Assesses Critical/High/Medium/Low based on content
- **Sentiment Analysis:** Detects Angry/Frustrated/Urgent/Neutral tone
- **Location Extraction:** Pulls location from unstructured text
- **Summarization:** Generates concise English summary for officers
- **Photo Analysis:** Extracts context from complaint images

### 4. Supabase (PostgreSQL)
**Role:** Persistent storage and real-time data layer.

- PostgreSQL database with 2 tables
- Real-time subscriptions via WebSocket (Realtime engine)
- Row-level security policies
- REST API for CRUD operations
- Used by both n8n (write) and Dashboard (read/write)

### 5. Admin Dashboard
**Role:** Government officer interface — command and control center.

- Single HTML file, zero dependencies (CDN-loaded libraries)
- 5 tabs: Complaints, Analytics, Map, Board, Scorecard
- Real-time updates via Supabase subscriptions
- Client-side filtering, sorting, and search
- Officer assignment and resolution workflows

---

## n8n Workflows

### Workflow 1: Complaint Intake (`whatsapp-intake.json`)

**Trigger:** WhatsApp webhook (incoming message)

```
Webhook Received
    │
    ▼
Extract sender number + message body
    │
    ▼
Query Supabase: Does user exist?
    │
    ├── NO → Send "Welcome! What's your name?"
    │        Update state → registering
    │
    ├── State = registering
    │   → Save name to users table
    │   → Send "Thanks {name}! Describe your complaint"
    │   → Update state → filing
    │
    ├── State = filing
    │   → Forward message to Workflow 2 (AI Classification)
    │   → Update state → awaiting_photo
    │   → Send "Got it! Want to attach a photo? Send it or type 'no'"
    │
    ├── State = awaiting_photo
    │   ├── Photo received → Upload, save URL, state → confirming
    │   └── "No" → state → confirming
    │   → Send complaint summary, ask "Confirm? (yes/no)"
    │
    └── State = confirming
        ├── "Yes" → Insert into raw_complaints, state → idle
        │          → Send "Complaint #XXXX filed successfully!"
        └── "No"  → state → idle
                   → Send "Complaint cancelled."
```

### Workflow 2: AI Classification (`ai-classify.json`)

**Trigger:** Called by Workflow 1 when citizen submits complaint text

```
Receive complaint text + photo URL (if any)
    │
    ▼
Construct GPT-4o prompt:
    "You are a Delhi civic complaint classifier.
     Analyze this complaint and return JSON with:
     - category (one of 6)
     - urgency (Critical/High/Medium/Low)
     - sentiment (Angry/Frustrated/Urgent/Neutral)
     - location (extracted from text, or 'Unknown')
     - summary (1-line English summary)"
    │
    ▼
Call OpenAI API (GPT-4o)
    │
    ▼
Parse JSON response
    │
    ▼
Return structured data to Workflow 1
```

**GPT-4o System Prompt:**
```
You are an AI assistant for the Delhi Municipal Corporation's complaint system.
Analyze the following citizen complaint (which may be in Hindi, Hinglish, or English).

Classify into EXACTLY ONE category:
- Waste Management
- Water Supply
- Roads
- Sewage & Drainage
- Electricity
- Other

Assess urgency:
- Critical: Health hazard, safety risk, emergency
- High: Affecting daily life significantly  
- Medium: Inconvenient but manageable
- Low: Minor issue, cosmetic

Detect sentiment:
- Angry: Hostile, threatening, all-caps
- Frustrated: Repeated complaint, exasperation
- Urgent: Time-sensitive language
- Neutral: Factual reporting

Extract location if mentioned. Generate a 1-line English summary.

Return ONLY valid JSON.
```

### Workflow 3: Status Notifications (`status-notify.json`)

**Trigger:** Supabase database trigger on `raw_complaints` UPDATE

```
Complaint status changed
    │
    ├── Status → "assigned"
    │   → Query citizen's WhatsApp number
    │   → Send: "Your complaint #{id} has been assigned to {officer_name}"
    │
    └── Status → "resolved"
        → Query citizen's WhatsApp number
        → Send: "Your complaint #{id} has been resolved! 
                 Notes: {officer_notes}
                 Thank you for reporting."
```

---

## WhatsApp State Machine

Each citizen's conversation follows a finite state machine:

```
                    ┌──────────────────────────────────────────┐
                    │         WHATSAPP STATE MACHINE            │
                    └──────────────────────────────────────────┘

                              ┌─────────┐
                    ┌────────▶│  IDLE   │◀──────────┐
                    │         └────┬────┘           │
                    │              │                 │
                    │         User sends             │
                    │         any message             │
                    │              │                 │
                    │              ▼                 │
                    │    ┌──────────────────┐        │
                    │    │  REGISTERING     │        │
                    │    │  (awaiting name) │        │
                    │    └────────┬─────────┘        │
                    │             │                  │
                    │        User sends              │
                    │        their name              │
                    │             │                  │
                    │             ▼                  │
                    │    ┌──────────────────┐        │
                    │    │    FILING        │        │
                    │    │ (awaiting issue) │        │
                    │    └────────┬─────────┘        │
                    │             │                  │
                    │     User describes             │
                    │     their complaint             │
                    │             │                  │
                    │             ▼                  │
                    │    ┌──────────────────┐        │
                    │    │ AWAITING_PHOTO   │        │
                    │    │ (photo or skip)  │        │
                    │    └────────┬─────────┘        │
                    │             │                  │
                    │      Photo or "No"             │
                    │             │                  │
                    │             ▼                  │
                    │    ┌──────────────────┐        │
                    │    │  CONFIRMING      │        │
                    │    │ (yes/no confirm) │        │
                    │    └───┬──────────┬───┘        │
                    │        │          │             │
                    │    "Yes"        "No"            │
                    │        │          │             │
                    │        ▼          └─────────────┘
                    │   ┌──────────┐
                    │   │ COMPLETE │
                    │   │(inserted)│
                    │   └────┬─────┘
                    │        │
                    └────────┘
```

### State Transitions

| Current State | Input | Action | Next State |
|---|---|---|---|
| *(new user)* | Any message | Create user, ask for name | `registering` |
| `idle` | Any message | Ask for complaint | `filing` |
| `registering` | Name text | Save name, ask for complaint | `filing` |
| `filing` | Complaint text | Send to AI classification | `awaiting_photo` |
| `awaiting_photo` | Photo | Upload photo, ask confirm | `confirming` |
| `awaiting_photo` | "No" / text | Skip photo, ask confirm | `confirming` |
| `confirming` | "Yes" | Insert complaint, confirm | `idle` |
| `confirming` | "No" | Cancel complaint | `idle` |

---

## Database Schema

### Entity Relationship Diagram

```
┌──────────────────────────┐         ┌──────────────────────────────────────┐
│         users            │         │         raw_complaints               │
├──────────────────────────┤         ├──────────────────────────────────────┤
│ whatsapp_number (PK) text│◀───────▶│ id (PK)              uuid           │
│ name                 text│   1:N   │ whatsapp_number       text  (FK)    │
│ state                text│         │ raw_message            text          │
│ created_at      timestampz│        │ timestamp              timestampz   │
└──────────────────────────┘         │ category               text          │
                                     │ urgency                text          │
                                     │ location               text          │
                                     │ sentiment              text          │
                                     │ summary                text          │
                                     │ status                 text          │
                                     │ assigned_to            text          │
                                     │ assigned_at            timestampz   │
                                     │ resolved_at            timestampz   │
                                     │ officer_notes          text          │
                                     │ photo_url              text          │
                                     └──────────────────────────────────────┘
```

### SQL Schema

```sql
-- Users table
CREATE TABLE users (
    whatsapp_number TEXT PRIMARY KEY,
    name TEXT,
    state TEXT DEFAULT 'idle',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Complaints table
CREATE TABLE raw_complaints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    whatsapp_number TEXT REFERENCES users(whatsapp_number),
    raw_message TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    category TEXT CHECK (category IN (
        'Waste Management', 'Water Supply', 'Roads',
        'Sewage & Drainage', 'Electricity', 'Other'
    )),
    urgency TEXT CHECK (urgency IN ('Critical', 'High', 'Medium', 'Low')),
    location TEXT,
    sentiment TEXT CHECK (sentiment IN ('Angry', 'Frustrated', 'Urgent', 'Neutral')),
    summary TEXT,
    status TEXT DEFAULT 'open' CHECK (status IN ('open', 'assigned', 'resolved')),
    assigned_to TEXT,
    assigned_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    officer_notes TEXT,
    photo_url TEXT
);

-- Enable Realtime
ALTER PUBLICATION supabase_realtime ADD TABLE raw_complaints;

-- Indexes for dashboard performance
CREATE INDEX idx_complaints_status ON raw_complaints(status);
CREATE INDEX idx_complaints_category ON raw_complaints(category);
CREATE INDEX idx_complaints_timestamp ON raw_complaints(timestamp DESC);
CREATE INDEX idx_complaints_urgency ON raw_complaints(urgency);
```

---

## API Integrations

| API | Provider | Purpose | Auth Method |
|---|---|---|---|
| WhatsApp Business API | Meta | Citizen messaging | Bearer Token |
| Chat Completions API | OpenAI | GPT-4o classification | API Key |
| Supabase REST API | Supabase | Database CRUD | Anon Key + RLS |
| Supabase Realtime | Supabase | WebSocket subscriptions | Anon Key |
| Nominatim API | OpenStreetMap | Geocoding locations | None (rate-limited) |
| CartoDB Tiles | CartoDB | Dark map basemap | None (public) |

---

## Real-time Architecture

The dashboard uses Supabase Realtime for instant updates without polling:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   n8n        │     │   Supabase   │     │  Dashboard   │
│ (inserts     │────▶│   Postgres   │────▶│  (browser)   │
│  complaint)  │     │              │     │              │
└──────────────┘     │  ┌────────┐  │     │  Subscribed  │
                     │  │Realtime│  │     │  Channels:   │
                     │  │Engine  │──┼────▶│              │
                     │  └────────┘  │ WS  │  • complaints│
                     └──────────────┘     │  • board     │
                                          └──────────────┘
```

**Channels:**
- `complaints-realtime`: Updates the Complaints tab table and stats
- `board-realtime`: Updates the Kanban board cards in real-time

**Event Types Handled:**
- `INSERT`: New complaint → add to table, show toast, update stats
- `UPDATE`: Status change → update row, refresh board, recalculate stats

---

## Security Model

| Layer | Mechanism |
|---|---|
| **API Keys** | Supabase anon key (client-side, RLS-protected) |
| **Database** | Row-Level Security policies on Supabase |
| **WhatsApp** | End-to-end encryption by Meta |
| **Dashboard** | Single-file, no server-side attack surface |
| **AI** | No PII sent to OpenAI beyond complaint text |
| **Network** | All API calls over HTTPS/WSS |

---

*This document is part of the [Delhi PS-CRM](README.md) project.*
