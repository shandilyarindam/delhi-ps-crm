# Demo -- Delhi PS-CRM

This document walks through the end-to-end user experience of filing a civic complaint via WhatsApp.

---

## Prerequisites

- The FastAPI backend is running and the WhatsApp webhook is connected to Meta
- Supabase tables (`users`, `raw_complaints`) and storage bucket (`complaint-evidence`) are set up
- The Gemini API key is configured

---

## Demo Flow

### Step 1 -- New User Registration

A citizen sends any message to the Delhi PS-CRM WhatsApp number for the first time.

**System response:**
> Welcome to Delhi PS-CRM! Please tell me your name.

The citizen replies with their name (e.g., "Amit Kumar").

**System response:**
> Thanks Amit Kumar! You're registered. Reply NEW to file a complaint or STATUS to check existing ones.

---

### Step 2 -- Filing a Complaint

The citizen sends **"new"** to start filing a complaint.

**System response:**
> Describe your issue

The citizen describes their complaint in **Hindi or English** (or a mix):

> "Rohini Sector 7 mein paani nahi aa raha hai teen din se. Bahut pareshani ho rahi hai."

or

> "There has been no water supply in Rohini Sector 7 for three days. Residents are frustrated."

**Gemini AI** analyzes the text and responds with a structured summary:

**System response:**
> Thanks -- I've noted your complaint.
> Category    : Water Supply
> Urgency     : High
> Location    : Rohini Sector 7
> Ward        : Rohini West Ward
> Summary     : No water supply in Rohini Sector 7 for three days.
>
> Reply YES to submit, NO to cancel, or send a photo as evidence.

**Note:** Gemini 2.0 Flash handles Hindi, English, and mixed-language (Hinglish) input naturally. No separate translation step is needed.

---

### Step 3 -- Attaching Photo Evidence (Optional)

The citizen can send a photo of the issue (e.g., dry taps, overflowing drains).

**System response:**
> Photo received! Reply YES to submit or NO to cancel.

The photo is uploaded to the `complaint-evidence` Supabase Storage bucket and linked to the complaint.

---

### Step 4 -- Submitting the Complaint

The citizen replies **"yes"** to confirm.

**System response:**
> Your complaint has been registered!
> Ticket ID: A1B2C3D4
> Category: Water Supply
> Urgency: High
> Our team will take action shortly.

The complaint is now stored in the `raw_complaints` table with status `open`. Email notifications are automatically sent to all relevant department teams (e.g., DJB for Water Supply) with ticket details and any photo evidence attached.

---

### Step 5 -- Checking Status

At any time, the citizen can send **"status"** to see all their complaints:

**System response:**
> Your complaints:
>
> 1. Ticket: A1B2C3D4
>    Category: Water Supply
>    Urgency: High
>    Status: open
>    Summary: No water supply in Rohini Sector 7 for three days.

---

### Step 6 -- Automatic Escalation

Every 30 minutes, the **APScheduler** cron job runs the escalation check:

1. It loads all unresolved complaints
2. For each complaint, it counts how many other complaints share the same **category + location** (cluster count)
3. The **GradientBoosting ML model** evaluates three features:
   - Complaint status (assigned vs. not)
   - Urgency level (Low to Critical)
   - Cluster count (geographic/category concentration)
4. If the model predicts escalation, the complaint status changes to `escalated`

The citizen receives a notification:

**System response:**
> Your complaint A1B2C3D4 regarding Water Supply in Rohini Sector 7 has been escalated due to high priority.

Escalation emails are also sent to all relevant department teams.

---

### Step 7 -- Duplicate Detection

If a citizen tries to file a complaint that matches an existing unresolved complaint (same category + location), the system detects the duplicate:

**System response:**
> A similar complaint has already been filed.
>
> Ticket   : A1B2C3D4
> Category : Water Supply
> Location : Rohini Sector 7
> Status   : open
>
> Your complaint is already being tracked. Send NEW to file a different complaint or STATUS to check updates.

---

## Cancellation

At any point during the complaint flow, the citizen can send **"no"** to cancel and return to the idle state.

**System response:**
> Cancelled. Send 'new' to file another complaint.

---

## What Triggers Escalation?

The ML model considers these factors:

| Factor                | Weight Influence                                      |
|-----------------------|-------------------------------------------------------|
| High/Critical urgency | Increases escalation probability                      |
| High cluster count    | Many similar complaints in the same area -> escalate  |
| Not yet assigned      | Unassigned complaints are more likely to escalate     |

The model was trained to identify complaints that need senior attention based on a combination of severity, inaction, and geographic clustering.
