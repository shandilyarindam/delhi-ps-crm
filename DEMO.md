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
> Namaskar! Welcome to the Delhi Civic Grievance Portal. I am here to help you report civic issues in your area.
>
> To get started, please share your full name.

The citizen replies with their name (e.g., "Amit Kumar").

**System response:**
> Thank you, Amit Kumar. Your account has been created.
>
> Send NEW to report a civic issue or STATUS to track your existing complaints.

---

### Step 2 -- Filing a Complaint

The citizen sends **"new"** to start filing a complaint.

**System response:**
> Please describe the civic issue you want to report. Include your location or area name for faster resolution.
>
> You can:
> - Type your complaint in Hindi, English, Urdu, Punjabi, or any regional language
> - Send a voice note describing the issue
>
> Our system will automatically understand and process your complaint.

The citizen describes their complaint in **any Indian regional language** (Hindi, English, Urdu, Punjabi, Haryanvi, Bhojpuri, Hinglish, or any mix):

> "Rohini Sector 7 mein paani nahi aa raha hai teen din se. Bahut pareshani ho rahi hai."

or

> "There has been no water supply in Rohini Sector 7 for three days. Residents are frustrated."

**Gemini AI** analyzes the text and responds with a structured summary:

**System response:**
> Your complaint has been recorded. Please verify the details below:
>
> Category : Water Supply
> Urgency  : High
> Location : Rohini Sector 7
> Ward     : Rohini West Ward
> Summary  : No water supply in Rohini Sector 7 for three days.
>
> Reply YES to submit, NO to cancel, or send a photo as evidence.

**Note:** Gemini 2.0 Flash handles Hindi, English, Urdu, Punjabi, Haryanvi, Bhojpuri, Hinglish, and other Indian regional languages naturally. No separate translation step is needed.

---

### Voice Note Filing Scenario

This scenario demonstrates voice note filing. It works in any Indian regional language -- Hindi, English, Urdu, Punjabi, Haryanvi, Bhojpuri, Hinglish, or any mix.

User: [sends voice note saying "Rohini Sector 7 mein teen din se paani nahi aa raha"]

Bot: Voice note received. Here is what I understood:

     Transcription: Rohini Sector 7 mein teen din se paani nahi aa raha

     Category : Water Supply
     Urgency  : High
     Location : Rohini Sector 7
     Ward     : Rohini West Ward
     Summary  : No water supply in Rohini Sector 7 for three days

     Reply YES to submit, NO to cancel, or send a photo as evidence.

User: yes

Bot: Your complaint has been registered with the Delhi Civic Grievance System.

     Ticket ID : A1B2C3D4
     Category  : Water Supply
     Urgency   : High

     The concerned department has been notified. An officer will be assigned shortly.

---

### Step 3 -- Attaching Photo Evidence (Optional)

The citizen can send a photo of the issue (e.g., dry taps, overflowing drains).

**System response:**
> Photo evidence received. Reply YES to submit your complaint or NO to cancel.

The photo is uploaded to the `complaint-evidence` Supabase Storage bucket and linked to the complaint.

---

### Step 4 -- Submitting the Complaint

The citizen replies **"yes"** to confirm.

**System response:**
> Your complaint has been registered with the Delhi Civic Grievance System.
>
> Ticket ID : A1B2C3D4
> Category  : Water Supply
> Urgency   : High
>
> The concerned department has been notified. An officer will be assigned shortly.

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

### Step 6 -- Officer Assignment Notification

When an officer is assigned through the admin dashboard, the citizen receives a WhatsApp notification:

**System response:**
> Update on your complaint A1B2C3D4: Officer Rajesh Sharma has been assigned to your Water Supply complaint in Rohini Sector 7. They will be in touch within 24 hours.

---

### Step 7 -- Resolution and Rating

When the complaint is resolved through the admin dashboard, the citizen receives a resolution notification with a rating prompt:

**System response:**
> Your complaint #A1B2C3D4 has been resolved.
>
> Category : Water Supply
> Location : Rohini Sector 7
>
> Resolution Notes: Water supply pipeline repaired. Normal supply restored.
>
> Please rate your experience. Reply with a number:
> 1 - Very Dissatisfied
> 2 - Dissatisfied
> 3 - Neutral
> 4 - Satisfied
> 5 - Very Satisfied
>
> Your feedback helps us improve civic services in Delhi.

The citizen replies with their rating (e.g., **"4"**):

**System response:**
> Thank you for your feedback. Your rating of 4/5 has been recorded.

The rating is saved to the `raw_complaints` table in the `rating` column for the most recently resolved complaint.

---

### Step 8 -- Automatic Escalation

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

Escalation emails are also sent to all relevant department teams, and the HoD receives a WhatsApp alert.

---

### Step 9 -- Duplicate Detection

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

During the confirmation step, the citizen can send **"no"** to cancel and return to the idle state.

**System response:**
> Your complaint has been cancelled. Send NEW to file a fresh complaint or STATUS to view existing ones.

---

## What Triggers Escalation?

The ML model considers these factors:

| Factor                | Weight Influence                                      |
|-----------------------|-------------------------------------------------------|
| High/Critical urgency | Increases escalation probability                      |
| High cluster count    | Many similar complaints in the same area -> escalate  |
| Not yet assigned      | Unassigned complaints are more likely to escalate     |

The model was trained to identify complaints that need senior attention based on a combination of severity, inaction, and geographic clustering.
