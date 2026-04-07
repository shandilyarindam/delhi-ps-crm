<div align="center">

# 🏛️ Delhi PS-CRM

### **AI-Powered Civic Grievance Management for the Government of Delhi**

*Transforming how 20 million citizens report and resolve civic issues — through WhatsApp.*

[![Built with n8n](https://img.shields.io/badge/Built%20with-n8n-FF6D5A?style=for-the-badge&logo=n8n&logoColor=white)](https://n8n.io)
[![Supabase](https://img.shields.io/badge/Supabase-3FCF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)
[![WhatsApp](https://img.shields.io/badge/WhatsApp%20Business-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)](https://business.whatsapp.com)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)
[![India Innovates](https://img.shields.io/badge/🇮🇳%20India%20Innovates-Top%2015%20Finalist-orange?style=flat-square)](#-hackathon)
[![Ministry Presentation](https://img.shields.io/badge/📋%20Selected-Ministry%20Presentation-green?style=flat-square)](#-hackathon)

---

<img src="assets/dashboard-preview.png" alt="Delhi PS-CRM Dashboard" width="800"/>

</div>

---

## 📖 What is Delhi PS-CRM?

**Delhi PS-CRM** (Public Service – Citizen Relationship Management) is an end-to-end civic grievance management system built for the Government of NCT of Delhi. Citizens file complaints via **WhatsApp** in **Hindi, Hinglish, or English** — and AI automatically classifies, prioritizes, and routes them to the right department. Government officers manage everything through a real-time **dark ops-room dashboard**.

No app downloads. No forms. No portals. Just WhatsApp — the app already on every phone in India.

---

## 🔴 The Problem

India's existing civic grievance systems are fundamentally broken:

| Problem | Impact |
|---|---|
| **Portal-dependent** | Citizens must navigate complex government websites |
| **English-only** | Excludes the 90%+ who think in Hindi/Hinglish |
| **No smartphone app adoption** | Government apps see <2% install rates |
| **Manual classification** | Complaints sit in queues for days before routing |
| **Zero transparency** | Citizens file complaints into a black hole |
| **No photo evidence** | Text descriptions are ambiguous and disputed |
| **Duplicate flooding** | Same pothole reported 50 times, each tracked separately |

The result? Citizens lose trust. Officers drown in unstructured data. Problems fester.

---

## 🟢 The Solution

**Meet citizens where they already are — WhatsApp.**

Delhi PS-CRM takes a radically simple approach:

```
📱 Citizen sends WhatsApp message
    → "Hamare gali mein 3 din se kachra pada hai, bahut badbu aa rahi hai"

🤖 AI instantly understands
    → Category: Waste Management
    → Urgency: High  
    → Sentiment: Frustrated
    → Location: Extracted from conversation

📋 Auto-routed to the right department
    → Assigned to nearest available officer
    → SLA timer starts ticking

✅ Citizen gets real-time updates
    → "Your complaint #A7F3B2C1 has been assigned to Saksham Gupta"
    → "Your complaint has been resolved! Thank you for reporting."
```

**No downloads. No forms. No waiting. Just results.**

---

## ✨ Features

### Citizen-Facing (WhatsApp)
| Feature | Description |
|---|---|
| 🤖 **AI-Powered Classification** | GPT-4o automatically categorizes complaints, detects urgency, analyzes sentiment, and extracts location — in any language |
| 🇮🇳 **Hindi/Hinglish Support** | Full native support for Hindi, Hinglish, and English. Citizens write naturally, AI understands perfectly |
| 📸 **Photo Evidence** | Citizens can attach photos of the issue. AI analyzes images for additional context |
| 💬 **Real-time Notifications** | Citizens receive WhatsApp updates at every stage — assignment, resolution, and follow-up |

### Admin Dashboard
| Feature | Description |
|---|---|
| 📊 **Analytics Dashboard** | Real-time charts — complaints by category, urgency distribution, daily trends, resolution times, and sentiment analysis |
| 🗺️ **Live Delhi Map** | Every complaint plotted on an interactive dark-themed map of Delhi, color-coded by urgency |
| 📋 **Kanban Board** | Jira-style drag-and-drop board with Open → In Progress → Resolved workflow |
| 🏆 **Department Scorecard** | Executive report card grading each department (A–F) on resolution rate, speed, and volume |
| 🔁 **Duplicate Detection** | Automatically groups complaints from the same location + category to prevent duplicate work |
| 🚨 **Auto-Escalation** | Critical complaints unresolved for >2 hours get auto-flagged with flashing escalation badges |

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Citizen Interface** | WhatsApp Business API | Complaint intake via India's most used messaging app |
| **Workflow Engine** | n8n (self-hosted) | 3 automated workflows handling the full complaint lifecycle |
| **AI/NLP** | OpenAI GPT-4o | Classification, sentiment analysis, Hindi/Hinglish NLU, photo analysis |
| **Database** | Supabase (PostgreSQL) | Real-time database with row-level security and instant subscriptions |
| **Dashboard** | Vanilla JS + Chart.js + Leaflet | Single-file, zero-dependency admin dashboard |
| **Maps** | Leaflet + CartoDB Dark | Dark-themed interactive complaint mapping |
| **Geocoding** | Nominatim (OpenStreetMap) | Location string → coordinates conversion |
| **Hosting** | Static HTML | Zero-server deployment — works from a single file |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DELHI PS-CRM ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   👤 CITIZEN                                                         │
│   ├── Sends WhatsApp message (Hindi/English/Hinglish)                │
│   ├── Attaches photo evidence (optional)                             │
│   └── Receives real-time status updates                              │
│         │                                                             │
│         ▼                                                             │
│   ┌─────────────┐     ┌──────────────┐     ┌──────────────────┐     │
│   │  WhatsApp    │────▶│    n8n        │────▶│   OpenAI GPT-4o  │     │
│   │  Business    │     │  Workflows   │     │                  │     │
│   │  API         │◀────│  (3 flows)   │◀────│  • Classify      │     │
│   └─────────────┘     └──────┬───────┘     │  • Sentiment     │     │
│                               │             │  • Extract loc   │     │
│                               ▼             │  • Detect urgency│     │
│                        ┌─────────────┐     └──────────────────┘     │
│                        │  Supabase    │                               │
│                        │  (Postgres)  │                               │
│                        │             │                               │
│                        │  • users     │                               │
│                        │  • complaints│                               │
│                        │  • realtime  │                               │
│                        └──────┬──────┘                               │
│                               │                                       │
│                               ▼                                       │
│   ┌─────────────────────────────────────────────────────────┐       │
│   │              ADMIN DASHBOARD (Single HTML File)          │       │
│   │                                                           │       │
│   │  ┌───────────┬───────────┬───────┬────────┬───────────┐ │       │
│   │  │COMPLAINTS │ ANALYTICS │  MAP  │ BOARD  │ SCORECARD │ │       │
│   │  │           │           │       │        │           │ │       │
│   │  │ Table     │ Charts    │Leaflet│ Kanban │ Dept      │ │       │
│   │  │ Filters   │ Stats     │Markers│ DnD    │ Grades    │ │       │
│   │  │ Actions   │ Trends    │Popups │ Modals │ Officers  │ │       │
│   │  └───────────┴───────────┴───────┴────────┴───────────┘ │       │
│   └─────────────────────────────────────────────────────────┘       │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📑 Dashboard Tabs

### 1. 📋 Complaints
The primary command center. A real-time table of all complaints with:
- Full-text search across ticket IDs, locations, and summaries
- Multi-filter by status, category, and urgency
- Inline officer assignment with workload balancing
- Resolution workflow with mandatory notes
- SLA timer with color-coded breach indicators (green → amber → red)
- Photo evidence lightbox viewer
- Duplicate grouping toggle
- Auto-escalation badges for critical overdue complaints

### 2. 📊 Analytics
Executive-level insights with live charts:
- Average resolution time & fastest resolution
- Complaints resolved this week
- Most affected area with complaint count
- Top sentiment breakdown
- Open rate percentage
- Category distribution (horizontal bar chart)
- Urgency breakdown (doughnut chart)
- Daily complaint trend (7-day line chart)

### 3. 🗺️ Map
Interactive dark-themed map of Delhi showing:
- Every complaint as a color-coded marker (by urgency)
- Click-to-reveal popup with full complaint details
- Geocoded from location strings using Nominatim
- CartoDB dark basemap matching the dashboard aesthetic
- Urgency legend overlay

### 4. 📋 Board
Jira-style Kanban workflow:
- Three columns: **Open** → **In Progress** → **Resolved**
- Drag-and-drop to advance complaints through the pipeline
- Auto-triggers assignment modal (Open → In Progress)
- Auto-triggers resolution modal with notes (In Progress → Resolved)
- Backward-move prevention with shake animation
- Real-time card updates via Supabase subscriptions

### 5. 🏆 Scorecard
Department Performance Report Card:
- 6 department cards in a 2×3 grid
- Letter grade (A–F) calculated from resolution metrics
- 4 KPIs per department: Total, Resolved, Avg Resolution Time, Open Rate
- Resolved vs Total progress bar
- Top 3 officers leaderboard with rank medals (🥇🥈🥉)
- 7-day complaint trend indicator
- Summary bar highlighting best, worst, most active, and fastest departments

---

## 🗄️ Database Schema

### `users` Table
| Column | Type | Description |
|---|---|---|
| `whatsapp_number` | `text` (PK) | Citizen's WhatsApp number |
| `name` | `text` | Citizen's registered name |
| `state` | `text` | Conversation state machine state |
| `created_at` | `timestamp` | Registration timestamp |

### `raw_complaints` Table
| Column | Type | Description |
|---|---|---|
| `id` | `uuid` (PK) | Unique complaint identifier |
| `whatsapp_number` | `text` | Filing citizen's number |
| `raw_message` | `text` | Original message (Hindi/English/Hinglish) |
| `timestamp` | `timestamp` | Filing time |
| `category` | `text` | AI-classified department (Waste Management, Water Supply, Roads, Sewage & Drainage, Electricity, Other) |
| `urgency` | `text` | AI-assessed urgency (Critical, High, Medium, Low) |
| `location` | `text` | Extracted location string |
| `sentiment` | `text` | AI-analyzed sentiment (Angry, Frustrated, Urgent, Neutral) |
| `summary` | `text` | AI-generated English summary |
| `status` | `text` | Workflow status (open, assigned, resolved) |
| `assigned_to` | `text` | Assigned officer name |
| `assigned_at` | `timestamp` | Assignment time |
| `resolved_at` | `timestamp` | Resolution time |
| `officer_notes` | `text` | Resolution notes from officer |
| `photo_url` | `text` | URL to photo evidence (if provided) |

---

## 🚶 How It Works — Citizen Journey

```
Step 1: 📱 Citizen opens WhatsApp, sends "Hi" to Delhi PS-CRM number
        → Bot greets, asks for name

Step 2: 👤 Citizen sends their name (e.g., "Rahul Sharma")
        → Bot registers user, asks for complaint

Step 3: 💬 Citizen describes issue in Hindi/Hinglish/English
        → "Hamare mohalle mein 2 din se paani nahi aa raha"

Step 4: 🤖 AI processes the message instantly
        → Category: Water Supply
        → Urgency: High
        → Sentiment: Frustrated  
        → Location: Extracted from context

Step 5: 📸 Bot asks if citizen wants to attach a photo
        → Citizen sends photo of dry taps (optional)

Step 6: ✅ Bot confirms complaint details, asks for confirmation
        → Citizen confirms with "Yes"

Step 7: 📋 Complaint appears in dashboard in real-time
        → Officers see it immediately across all tabs

Step 8: 👮 Officer assigns complaint to field worker
        → Citizen gets WhatsApp: "Assigned to Ritika Singh"

Step 9: 🔧 Field worker resolves the issue
        → Officer marks resolved with notes

Step 10: 🎉 Citizen gets WhatsApp: "Your complaint has been resolved!"
         → Feedback loop closed
```

---

## 📸 Screenshots

<div align="center">

| Complaints Tab | Analytics Tab |
|---|---|
| ![Complaints](assets/screenshots/complaints-tab.png) | ![Analytics](assets/screenshots/analytics-tab.png) |

| Map Tab | Board Tab |
|---|---|
| ![Map](assets/screenshots/map-tab.png) | ![Board](assets/screenshots/board-tab.png) |

| Scorecard Tab | WhatsApp Flow |
|---|---|
| ![Scorecard](assets/screenshots/scorecard-tab.png) | ![WhatsApp](assets/screenshots/whatsapp-flow.png) |

</div>

---

## ⚙️ Setup

### Prerequisites
- [Supabase](https://supabase.com) account (free tier works)
- [n8n](https://n8n.io) instance (self-hosted or cloud)
- [WhatsApp Business API](https://business.whatsapp.com) access
- [OpenAI API](https://platform.openai.com) key

### Steps

1. **Database Setup**
   - Create a new Supabase project
   - Run the SQL schema to create `users` and `raw_complaints` tables
   - Enable Realtime on `raw_complaints` table

2. **n8n Workflows**
   - Import the 3 workflow JSON files into your n8n instance
   - Configure WhatsApp Business API credentials
   - Configure OpenAI API key
   - Configure Supabase connection

3. **Dashboard**
   - Open `delhi-ps-crm-dashboard.html` in a browser
   - Update `SUPABASE_URL` and `SUPABASE_KEY` constants if using your own project
   - That's it — it's a single HTML file, no build step needed

4. **WhatsApp**
   - Connect your WhatsApp Business number to n8n webhook
   - Test with a "Hi" message to start the flow

---

## 🏆 Hackathon

<div align="center">

### 🇮🇳 India Innovates Hackathon

**Delhi PS-CRM was built for the India Innovates hackathon** — a national-level competition focused on technology solutions for governance.

🏅 **Top 15 Finalist** — Selected from thousands of entries nationwide

🏛️ **Bharat Mandapam, New Delhi** — Presented at the grand finals

📋 **Ministry Presentation** — Selected for presentation to Ministry officials

</div>

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

**Built with ❤️ for Delhi**

*By citizens, for citizens — making governance accessible to every Indian.*

🏛️ Government of NCT of Delhi · 🇮🇳 India

</div>
