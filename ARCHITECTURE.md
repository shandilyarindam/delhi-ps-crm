# Delhi PS-CRM Architecture Documentation

## System Overview

Delhi PS-CRM is an AI-powered WhatsApp civic grievance management system serving 20 million citizens across all 272 wards of Delhi. The platform enables citizens to file complaints through WhatsApp in multiple Indian languages, with automatic AI classification, intelligent routing to government departments, and ML-based escalation for unresolved issues. Built for government-scale operations with real-time monitoring, officer accountability, and comprehensive audit trails.

## System Architecture Overview

The request flow follows a stateless, horizontally scalable architecture:

```
WhatsApp Citizen Message
    Meta Cloud API
        POST /webhook (FastAPI)
            HMAC Signature Verification
                Rate Limiting (100 req/min)
                    Deduplication (30-second window)
                        State Machine Router
                            Handler Processing
                                Supabase Database Operations
                                    WhatsApp Response Generation
```

## Complete State Machine

The conversation state machine manages all user interactions through 7 distinct states:

| State | Handler | Description |
|-------|---------|-------------|
| (new user) | registration.py | Creates user row in database, collects full name for registration |
| registering | registration.py | Awaiting name input from new user during onboarding |
| idle | idle.py | Accepts NEW (file complaint), STATUS (check existing), and rating (1-5) commands |
| filing | filing.py | Collects complaint text or voice note, validates input, sends to Gemini AI for analysis |
| confirming | confirming.py | User reviews AI analysis, can attach photo evidence, confirms or cancels |
| awaiting_photo | awaiting_photo.py | Accepts image upload to Supabase Storage, updates complaint draft |
| awaiting_rating | awaiting_rating.py | Citizen prompted to rate resolved complaint, awaiting 1-5 input |

State transitions are atomic and persistent, ensuring no conversation state is lost during server restarts or failover scenarios.

## AI Classification System

The system uses **Gemini 2.5 Flash-Lite** for intelligent complaint classification and analysis. When a citizen files a complaint (text or voice), the content is processed through Gemini AI with a structured prompt that extracts:

- **Category**: Primary classification (Waste Management, Water Supply, Sewage & Drainage, Roads, Electricity, Other)
- **Categories**: All relevant categories for multi-department issues
- **Urgency**: Priority level (Low, Medium, High, Critical)
- **Location**: Specific area, sector, colony, or landmark in Delhi
- **Ward**: Delhi municipal ward inferred from location using comprehensive mapping
- **Summary**: One-sentence description under 15 words
- **Sentiment**: Emotional tone (Neutral, Frustrated, Angry, Urgent)

**Language Support**: Gemini 2.5 Flash-Lite natively processes Hindi, English, Urdu, Punjabi, Haryanvi, Bhojpuri, Hinglish, and mixed-language inputs without requiring separate translation services. The AI is enhanced with comprehensive Delhi ward mapping context for accurate location-to-ward detection.

## Voice Note Processing

Citizens can submit voice notes in any supported Indian language:

1. **Media Extraction**: Webhook extracts `media_id` from WhatsApp audio message
2. **Audio Download**: Handler downloads audio bytes from WhatsApp Cloud API
3. **AI Processing**: Audio bytes sent directly to Gemini 2.5 Flash-Lite with transcription and classification prompt
4. **Structured Output**: Returns transcription, category, urgency, location, ward, summary, and sentiment in single API call
5. **Validation**: Duplicate detection based on extracted category and location
6. **Confirmation**: User receives transcription for verification before submission

WhatsApp voice notes use audio/ogg with opus codec, which Gemini processes natively without additional transcription services.

## ML Escalation System

The escalation system uses a trained GradientBoosting classifier (F1 score: 0.9273) that automatically identifies complaints requiring intervention:

**Escalation Flow**:
```
APScheduler (every 30 min) 
    -> Load unresolved complaints from Supabase
        -> Compute cluster count (category + location grouping)
            -> GradientBoosting model prediction
                -> If escalate: Update status to "escalated"
                    -> WhatsApp notification to citizen
                        -> Email alert to department HoD
```

**Model Features**:
- `status_encoded`: Numerical representation of current complaint status
- `urgency_encoded`: Urgency level converted to numerical format  
- `cluster_count`: Number of similar complaints in same category and location

The model triggers escalation for complaints showing patterns of neglect, high urgency, or geographic clustering, ensuring proactive government response.

## Database Schema

### Supabase Tables

#### `users`

| Column            | Type      | Description                                     |
|-------------------|-----------|-------------------------------------------------|
| `id`              | UUID      | Primary key                                     |
| `whatsapp_number` | text      | User's WhatsApp number (unique)                 |
| `name`            | text      | User's registered name                          |
| `state`           | text      | Current conversation state (registering, idle, filing, confirming, awaiting_photo, awaiting_rating) |
| `state_data`      | jsonb     | Temporary data for current flow (draft_id, complaint_id) |
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
| `raw_message`     | text        | Original complaint text or transcription          |
| `status`          | text        | open, assigned, in_progress, escalated, resolved  |
| `photo_url`       | text        | Public URL to evidence photo (nullable)           |
| `assigned_to`     | text        | Assigned officer name (nullable)                  |
| `assigned_officer_id` | UUID     | Officer ID for accountability tracking              |
| `rating`          | integer     | Citizen satisfaction rating 1-5 (nullable)        |
| `timestamp`       | timestamptz | Complaint submission timestamp                    |
| `resolved_at`     | timestamptz | Resolution timestamp (nullable)                   |

#### `complaint_drafts`

| Column            | Type        | Description                                       |
|-------------------|-------------|---------------------------------------------------|
| `id`              | UUID        | Primary key                                     |
| `whatsapp_number` | text        | Citizen's WhatsApp number                        |
| `draft_data`      | jsonb       | Complete complaint draft with AI analysis        |
| `status`          | text        | Always "draft"                                    |
| `created_at`      | timestamptz | Draft creation timestamp                         |
| `updated_at`      | timestamptz | Last update timestamp                            |

### Supabase Storage

| Bucket               | Access  | Description                              |
|-----------------------|---------|------------------------------------------|
| `complaint-evidence`  | Public  | Photo evidence uploaded by citizens       |

Files are stored at the path `{whatsapp_number}/{uuid}.{ext}` with public URLs for evidence access.

## Scalability & Production Deployment

### Horizontal Scaling Architecture

- **Stateless Handlers**: All conversation state persisted in Supabase database, enabling any backend instance to handle any request
- **Database Connection Pooling**: Supabase manages connection pooling, automatic failover, and read replicas
- **Load Balancer Ready**: Multiple FastAPI instances can be deployed behind HTTP load balancer
- **Async I/O**: All external API calls (WhatsApp, Supabase, email) use async httpx for non-blocking operations

### Production Migration Path

The system is architected for seamless migration from Railway to Microsoft Azure for government-scale deployment:

- **Backend**: Azure App Service or Azure Container Apps with auto-scaling policies
- **Database**: Migrate from Supabase to Azure Database for PostgreSQL with read replicas
- **Storage**: Azure Blob Storage for complaint photo evidence with CDN distribution
- **ML Model**: Azure Machine Learning for model serving and retraining pipelines
- **Message Queue**: Azure Service Bus for webhook event queuing under high load
- **Monitoring**: Azure Monitor and Application Insights for comprehensive observability

### Performance Optimizations

- **ML Model Caching**: GradientBoosting model loaded once per process and cached in memory
- **Rate Limiting**: 100 requests per minute per phone number prevents abuse
- **Deduplication**: 30-second window prevents duplicate processing from Meta retries
- **Ward Mapping Cache**: 150+ Delhi location mappings cached for rapid AI context
- **Structured Logging**: JSON logging enables real-time monitoring and alerting

The stateless architecture ensures zero-downtime deployments and automatic failover, meeting government infrastructure reliability requirements.

