# Architecture -- Delhi PS-CRM

## System Overview

Delhi PS-CRM is a WhatsApp-based civic complaint management system. Citizens interact entirely through WhatsApp. The backend processes messages, classifies complaints using AI, stores data in Supabase, and auto-escalates unresolved issues using a trained ML model.

```mermaid
#mermaid-rc05{font-family:inherit;font-size:16px;fill:#E5E5E5;}@keyframes edge-animation-frame{from{stroke-dashoffset:0;}}@keyframes dash{to{stroke-dashoffset:0;}}#mermaid-rc05 .edge-animation-slow{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 50s linear infinite;stroke-linecap:round;}#mermaid-rc05 .edge-animation-fast{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 20s linear infinite;stroke-linecap:round;}#mermaid-rc05 .error-icon{fill:#CC785C;}#mermaid-rc05 .error-text{fill:#3387a3;stroke:#3387a3;}#mermaid-rc05 .edge-thickness-normal{stroke-width:1px;}#mermaid-rc05 .edge-thickness-thick{stroke-width:3.5px;}#mermaid-rc05 .edge-pattern-solid{stroke-dasharray:0;}#mermaid-rc05 .edge-thickness-invisible{stroke-width:0;fill:none;}#mermaid-rc05 .edge-pattern-dashed{stroke-dasharray:3;}#mermaid-rc05 .edge-pattern-dotted{stroke-dasharray:2;}#mermaid-rc05 .marker{fill:#A1A1A1;stroke:#A1A1A1;}#mermaid-rc05 .marker.cross{stroke:#A1A1A1;}#mermaid-rc05 svg{font-family:inherit;font-size:16px;}#mermaid-rc05 p{margin:0;}#mermaid-rc05 .label{font-family:inherit;color:#E5E5E5;}#mermaid-rc05 .cluster-label text{fill:#3387a3;}#mermaid-rc05 .cluster-label span{color:#3387a3;}#mermaid-rc05 .cluster-label span p{background-color:transparent;}#mermaid-rc05 .label text,#mermaid-rc05 span{fill:#E5E5E5;color:#E5E5E5;}#mermaid-rc05 .node rect,#mermaid-rc05 .node circle,#mermaid-rc05 .node ellipse,#mermaid-rc05 .node polygon,#mermaid-rc05 .node path{fill:transparent;stroke:#A1A1A1;stroke-width:1px;}#mermaid-rc05 .rough-node .label text,#mermaid-rc05 .node .label text,#mermaid-rc05 .image-shape .label,#mermaid-rc05 .icon-shape .label{text-anchor:middle;}#mermaid-rc05 .node .katex path{fill:#000;stroke:#000;stroke-width:1px;}#mermaid-rc05 .rough-node .label,#mermaid-rc05 .node .label,#mermaid-rc05 .image-shape .label,#mermaid-rc05 .icon-shape .label{text-align:center;}#mermaid-rc05 .node.clickable{cursor:pointer;}#mermaid-rc05 .root .anchor path{fill:#A1A1A1!important;stroke-width:0;stroke:#A1A1A1;}#mermaid-rc05 .arrowheadPath{fill:#0b0b0b;}#mermaid-rc05 .edgePath .path{stroke:#A1A1A1;stroke-width:2.0px;}#mermaid-rc05 .flowchart-link{stroke:#A1A1A1;fill:none;}#mermaid-rc05 .edgeLabel{background-color:transparent;text-align:center;}#mermaid-rc05 .edgeLabel p{background-color:transparent;}#mermaid-rc05 .edgeLabel rect{opacity:0.5;background-color:transparent;fill:transparent;}#mermaid-rc05 .labelBkg{background-color:rgba(0, 0, 0, 0.5);}#mermaid-rc05 .cluster rect{fill:#CC785C;stroke:hsl(15, 12.3364485981%, 48.0392156863%);stroke-width:1px;}#mermaid-rc05 .cluster text{fill:#3387a3;}#mermaid-rc05 .cluster span{color:#3387a3;}#mermaid-rc05 div.mermaidTooltip{position:absolute;text-align:center;max-width:200px;padding:2px;font-family:inherit;font-size:12px;background:#CC785C;border:1px solid hsl(15, 12.3364485981%, 48.0392156863%);border-radius:2px;pointer-events:none;z-index:100;}#mermaid-rc05 .flowchartTitleText{text-anchor:middle;font-size:18px;fill:#E5E5E5;}#mermaid-rc05 rect.text{fill:none;stroke-width:0;}#mermaid-rc05 .icon-shape,#mermaid-rc05 .image-shape{background-color:transparent;text-align:center;}#mermaid-rc05 .icon-shape p,#mermaid-rc05 .image-shape p{background-color:transparent;padding:2px;}#mermaid-rc05 .icon-shape rect,#mermaid-rc05 .image-shape rect{opacity:0.5;background-color:transparent;fill:transparent;}#mermaid-rc05 .label-icon{display:inline-block;height:1em;overflow:visible;vertical-align:-0.125em;}#mermaid-rc05 .node .label-icon path{fill:currentColor;stroke:revert;stroke-width:revert;}#mermaid-rc05 :root{--mermaid-font-family:inherit;}sends messagePOST /webhooknew useridle + NEWidle + STATUSfilingduplicate checkyesnophoto receivedYES confirmedescalate=1status changeassignedresolvedCitizen WhatsAppMeta Cloud APIFastAPI BackendState MachineRegistration HandlerFiling HandlerStatus HandlerAI Classification\nGemini 2.0 FlashDuplicate?Notify Citizen\nReset to idleConfirming HandlerSupabase Storage\ncomplaint-evidenceInsert raw_complaints\nSupabase PostgresSend Ticket\nWhatsAppEmail Departments\nGmail SMTPAPScheduler\nEvery 30 minEscalation CronML Model\nGradient BoostingUpdate status\nescalatedWhatsApp CitizenEmail HoDWhatsApp HoDSupabase WebhookNotifications RouterWhatsApp Citizen\nOfficer assignedWhatsApp Citizen\nComplaint resolved
```

```mermaid
#mermaid-rc06{font-family:inherit;font-size:16px;fill:#E5E5E5;}@keyframes edge-animation-frame{from{stroke-dashoffset:0;}}@keyframes dash{to{stroke-dashoffset:0;}}#mermaid-rc06 .edge-animation-slow{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 50s linear infinite;stroke-linecap:round;}#mermaid-rc06 .edge-animation-fast{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 20s linear infinite;stroke-linecap:round;}#mermaid-rc06 .error-icon{fill:#CC785C;}#mermaid-rc06 .error-text{fill:#3387a3;stroke:#3387a3;}#mermaid-rc06 .edge-thickness-normal{stroke-width:1px;}#mermaid-rc06 .edge-thickness-thick{stroke-width:3.5px;}#mermaid-rc06 .edge-pattern-solid{stroke-dasharray:0;}#mermaid-rc06 .edge-thickness-invisible{stroke-width:0;fill:none;}#mermaid-rc06 .edge-pattern-dashed{stroke-dasharray:3;}#mermaid-rc06 .edge-pattern-dotted{stroke-dasharray:2;}#mermaid-rc06 .marker{fill:#A1A1A1;stroke:#A1A1A1;}#mermaid-rc06 .marker.cross{stroke:#A1A1A1;}#mermaid-rc06 svg{font-family:inherit;font-size:16px;}#mermaid-rc06 p{margin:0;}#mermaid-rc06 defs #statediagram-barbEnd{fill:#A1A1A1;stroke:#A1A1A1;}#mermaid-rc06 g.stateGroup text{fill:#A1A1A1;stroke:none;font-size:10px;}#mermaid-rc06 g.stateGroup text{fill:#E5E5E5;stroke:none;font-size:10px;}#mermaid-rc06 g.stateGroup .state-title{font-weight:bolder;fill:#E5E5E5;}#mermaid-rc06 g.stateGroup rect{fill:transparent;stroke:#A1A1A1;}#mermaid-rc06 g.stateGroup line{stroke:#A1A1A1;stroke-width:1;}#mermaid-rc06 .transition{stroke:#A1A1A1;stroke-width:1;fill:none;}#mermaid-rc06 .stateGroup .composit{fill:#f4f4f4;border-bottom:1px;}#mermaid-rc06 .stateGroup .alt-composit{fill:#e0e0e0;border-bottom:1px;}#mermaid-rc06 .state-note{stroke:#A1A1A1;fill:#2D2D2D;}#mermaid-rc06 .state-note text{fill:#E5E5E5;stroke:none;font-size:10px;}#mermaid-rc06 .stateLabel .box{stroke:none;stroke-width:0;fill:transparent;opacity:0.5;}#mermaid-rc06 .edgeLabel .label rect{fill:transparent;opacity:0.5;}#mermaid-rc06 .edgeLabel{background-color:transparent;text-align:center;}#mermaid-rc06 .edgeLabel p{background-color:transparent;}#mermaid-rc06 .edgeLabel rect{opacity:0.5;background-color:transparent;fill:transparent;}#mermaid-rc06 .edgeLabel .label text{fill:#E5E5E5;}#mermaid-rc06 .label div .edgeLabel{color:#E5E5E5;}#mermaid-rc06 .stateLabel text{fill:#E5E5E5;font-size:10px;font-weight:bold;}#mermaid-rc06 .node circle.state-start{fill:#A1A1A1;stroke:#A1A1A1;}#mermaid-rc06 .node .fork-join{fill:#A1A1A1;stroke:#A1A1A1;}#mermaid-rc06 .node circle.state-end{fill:#A1A1A1;stroke:#f4f4f4;stroke-width:1.5;}#mermaid-rc06 .end-state-inner{fill:#f4f4f4;stroke-width:1.5;}#mermaid-rc06 .node rect{fill:transparent;stroke:#A1A1A1;stroke-width:1px;}#mermaid-rc06 .node polygon{fill:transparent;stroke:#A1A1A1;stroke-width:1px;}#mermaid-rc06 #statediagram-barbEnd{fill:#A1A1A1;}#mermaid-rc06 .statediagram-cluster rect{fill:transparent;stroke:#A1A1A1;stroke-width:1px;}#mermaid-rc06 .cluster-label,#mermaid-rc06 .nodeLabel{color:#E5E5E5;}#mermaid-rc06 .statediagram-cluster rect.outer{rx:5px;ry:5px;}#mermaid-rc06 .statediagram-state .divider{stroke:#A1A1A1;}#mermaid-rc06 .statediagram-state .title-state{rx:5px;ry:5px;}#mermaid-rc06 .statediagram-cluster.statediagram-cluster .inner{fill:#f4f4f4;}#mermaid-rc06 .statediagram-cluster.statediagram-cluster-alt .inner{fill:#CC785C;}#mermaid-rc06 .statediagram-cluster .inner{rx:0;ry:0;}#mermaid-rc06 .statediagram-state rect.basic{rx:5px;ry:5px;}#mermaid-rc06 .statediagram-state rect.divider{stroke-dasharray:10,10;fill:#CC785C;}#mermaid-rc06 .note-edge{stroke-dasharray:5;}#mermaid-rc06 .statediagram-note rect{fill:#2D2D2D;stroke:#A1A1A1;stroke-width:1px;rx:0;ry:0;}#mermaid-rc06 .statediagram-note rect{fill:#2D2D2D;stroke:#A1A1A1;stroke-width:1px;rx:0;ry:0;}#mermaid-rc06 .statediagram-note text{fill:#E5E5E5;}#mermaid-rc06 .statediagram-note .nodeLabel{color:#E5E5E5;}#mermaid-rc06 .statediagram .edgeLabel{color:red;}#mermaid-rc06 #dependencyStart,#mermaid-rc06 #dependencyEnd{fill:#A1A1A1;stroke:#A1A1A1;stroke-width:1;}#mermaid-rc06 .statediagramTitleText{text-anchor:middle;font-size:18px;fill:#E5E5E5;}#mermaid-rc06 :root{--mermaid-font-family:inherit;}new username savedsends NEWunrecognized inputcomplaint classifiedduplicate foundphoto receivedYES - complaint filedNO - cancelledregisteringidlefilingconfirming
```

---

## Request Flow

### 1. Incoming Message

```
WhatsApp -> Meta Webhook -> POST /webhook -> FastAPI -> State Machine
```

1. A citizen sends a WhatsApp message (text or image)
2. Meta's Cloud API delivers it to our `POST /webhook` endpoint
3. The webhook router parses the payload and extracts sender, text, type, and media ID
4. The **state machine** (`handlers/state_machine.py`) looks up the user's current state in Supabase and routes to the appropriate handler

### 2. Conversational State Machine

Users progress through these states:

| State           | Handler              | Description                                    |
|-----------------|----------------------|------------------------------------------------|
| `(new user)`    | `registration.py`    | Creates user row, collects name                |
| `registering`   | `registration.py`    | Awaiting name input                            |
| `idle`          | `idle.py`            | Accepts `new` (file complaint) or `status`     |
| `filing`        | `filing.py`          | Collects complaint text, sends to Gemini AI    |
| `confirming`    | `confirming.py`      | User reviews AI analysis, can attach photo     |
| `awaiting_photo`| `confirming.py`      | Accepts image upload to Supabase Storage       |

At any state (except registration), sending **"no"** cancels the flow and returns to `idle`.

### 3. AI Classification

When a user files a complaint, the text is sent to **Gemini 2.0 Flash** with a structured prompt. The AI returns:

- **Category**: Primary category (Waste Management, Water Supply, Sewage & Drainage, Roads, Electricity, Other)
- **Categories**: All relevant categories (multi-category support)
- **Urgency**: Low, Medium, High, Critical
- **Location**: Extracted from the complaint text
- **Ward**: Delhi municipal ward derived from the location
- **Summary**: One-sentence summary
- **Sentiment**: Neutral, Frustrated, Angry, Distressed, Polite

Gemini handles **Hindi and English** input naturally -- no translation step is needed.

### 4. Complaint Submission

After the user confirms (replies "YES"), the complaint is inserted into the `raw_complaints` table with all AI-analyzed fields. The user receives a ticket ID (first 8 characters of the UUID). Email notifications are sent to all relevant department teams via Gmail SMTP.

---

## Escalation Flow

```
APScheduler (every 30 min) -> ML Model prediction -> Supabase update -> WhatsApp alert + Email
```

1. **APScheduler** triggers `run_escalation_check()` every 30 minutes
2. The cron job loads all unresolved complaints from Supabase
3. For each complaint, it computes a **cluster count** (how many complaints share the same category + location)
4. The **GradientBoosting model** receives three features: `status_encoded`, `urgency_encoded`, `cluster_count`
5. If the model predicts `1` (escalate), the complaint status is updated to `escalated`, the citizen receives a WhatsApp notification, and escalation emails are sent to all relevant departments

---

## Database Schema

### Supabase Tables

#### `users`

| Column            | Type      | Description                                     |
|-------------------|-----------|-------------------------------------------------|
| `id`              | UUID      | Primary key                                     |
| `whatsapp_number` | text      | User's WhatsApp number (unique)                 |
| `name`            | text      | User's registered name                          |
| `state`           | text      | Current conversation state                      |
| `state_data`      | jsonb     | Temporary data for the current flow (e.g. draft)|
| `created_at`      | timestamp | Registration timestamp                          |

#### `raw_complaints`

| Column            | Type        | Description                                       |
|-------------------|-------------|---------------------------------------------------|
| `id`              | UUID        | Primary key (ticket ID derived from first 8 chars) |
| `whatsapp_number` | text        | Complainant's WhatsApp number                     |
| `category`        | text        | AI-classified primary category                    |
| `categories`      | text[]      | All relevant AI-classified categories             |
| `urgency`         | text        | AI-classified urgency level                       |
| `location`        | text        | Extracted location                                |
| `ward`            | text        | Delhi municipal ward                              |
| `sentiment`       | text        | AI-detected sentiment                             |
| `summary`         | text        | AI-generated summary                              |
| `status`          | text        | open, assigned, in_progress, escalated, resolved  |
| `photo_url`       | text        | Public URL to evidence photo (nullable)           |
| `assigned_to`     | text        | Assigned officer name (nullable)                  |
| `timestamp`       | timestamptz | Complaint submission timestamp                    |

### Supabase Storage

| Bucket               | Access  | Description                              |
|-----------------------|---------|------------------------------------------|
| `complaint-evidence`  | Public  | Photo evidence uploaded by citizens       |

Files are stored at the path `{whatsapp_number}/{uuid}.{ext}`.

---

## Scalability

- **Stateless handlers**: All conversation state is stored in Supabase, not in memory. Any backend instance can handle any request.
- **Managed Postgres**: Supabase handles database scaling, backups, and connection pooling.
- **Horizontal scaling**: Deploy multiple instances on Railway behind a load balancer. The APScheduler job uses `replace_existing=True` to prevent duplicate escalation runs.
- **Async throughout**: All I/O (WhatsApp API calls, Supabase queries) uses `httpx` async HTTP client.
- **ML model caching**: The escalation model is loaded once and cached in memory for the process lifetime.
