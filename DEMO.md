# Delhi PS-CRM Demo Walkthrough

Complete demonstration of the AI-powered WhatsApp civic grievance management system serving 20 million citizens across Delhi's 272 wards.

---

## Step 1: New User Registration

A citizen sends their first message to the Delhi PS-CRM WhatsApp number.

**Citizen:** "hi"

**Bot Response:**
> Namaskar! Welcome to the Delhi Civic Grievance Portal. I am here to help you report civic issues in your area. To get started, please share your full name.

**Citizen:** "Rajesh Kumar"

**Bot Response:**
> Thank you, Rajesh Kumar. You're registered. Send NEW to report a civic issue or STATUS to track your existing complaints.

---

## Step 2: Filing a Complaint in Hindi

**Citizen:** "new"

**Bot Response:**
> Please describe the civic issue you want to report. Include your location or area name for faster resolution. You can:
> - Type your complaint
> - Send a voice note describing the issue

**Citizen:** "Rohini sector 7 mein paani nahi aa raha hai teen din se. Bahut pareshani ho rahi hai."

**Bot Response (Gemini 2.5 Flash-Lite Analysis):**
> Your complaint has been recorded. Please verify the details below:
>
> Category : Water Supply
> Urgency  : High
> Location : Rohini Sector 7
> Ward     : Rohini Zone
> Summary  : No water supply in Rohini Sector 7 for three days.
>
> Reply YES to submit, NO to cancel, or send a photo as evidence.

---

## Step 3: Filing a Complaint via Voice Note

**Citizen:** "new"

**Bot Response:**
> Please describe the civic issue you want to report. Include your location or area name for faster resolution. You can:
> - Type your complaint
> - Send a voice note describing the issue

**Citizen:** [sends voice note saying "Laxmi Nagar Metro Station ke paas garbage overflowing hai bins mein"]

**Bot Response (Voice Transcription + AI Analysis):**
> Voice note received. Here is what I understood:
>
> Transcription: Laxmi Nagar Metro Station ke paar garbage overflowing hai bins mein
>
> Category : Waste Management
> Urgency  : Medium
> Location : Laxmi Nagar Metro Station
> Ward     : Laxmi Nagar Ward
> Summary  : Garbage overflowing in bins near Laxmi Nagar Metro Station
>
> Reply YES to submit, NO to cancel, or send a photo as evidence.

---

## Step 4: Attaching Photo Evidence

**Citizen:** [sends photo of overflowing garbage bins]

**Bot Response:**
> Photo received! Reply YES to submit or NO to cancel.

---

## Step 5: Submitting and Receiving Ticket Confirmation

**Citizen:** "yes"

**Bot Response:**
> Your complaint has been registered!
> Ticket ID: EB582771
> Category: Waste Management
> Urgency: Medium
> Our team will take action shortly.

---

## Step 6: Checking Complaint Status

**Citizen:** "status"

**Bot Response:**
> Your complaints:
>
> 1. Ticket: EB582771
>    Category: Waste Management
>    Urgency: Medium
>    Status: open
>    Summary: Garbage overflowing in bins near Laxmi Nagar Metro Station

---

## Step 7: Officer Assignment Notification

**Bot Response (automatic when officer assigned via dashboard):**
> Update on your complaint #EB582771
>
> Your complaint regarding "Garbage overflowing in bins in Kirti Nagar." has been assigned to Officer Saksham Gupta.
>
> We are working on resolving this at the earliest.

---

## Step 8: Resolution Notification and Rating Prompt

**Bot Response (automatic when complaint marked resolved):**
> Your complaint #740F4A60 has been resolved.
>
> Category : Electricity
> Location : Hauz Khas
>
> Resolution Notes: transformer was fixed
>
> Please rate your experience with our service. Reply with a number:
>
> 1 - Very Dissatisfied
> 2 - Dissatisfied
> 3 - Neutral
> 4 - Satisfied
> 5 - Very Satisfied
>
> Your feedback helps us improve civic services in Delhi.

---

## Step 9: Rating Submission and Confirmation

**Citizen:** "5"

**Bot Response:**
> Thank you for your feedback. Your rating of 5/5 has been recorded.

---

## Step 10: Automatic ML Escalation

**Bot Response (automatic when ML model triggers escalation):**
> Your complaint EB582771 regarding Waste Management in Laxmi Nagar has been escalated to senior authorities due to high priority and multiple similar reports in the area.

---

## Step 11: Duplicate Complaint Detection

**Citizen:** "new"

**Bot Response:**
> Please describe the civic issue you want to report. Include your location or area name for faster resolution. You can:
> - Type your complaint
> - Send a voice note describing the issue

**Citizen:** "Laxmi Nagar Metro Station ke paas garbage overflowing hai bins mein"

**Bot Response (duplicate detection):**
> A similar complaint has already been filed.
>
> Ticket   : EB582771
> Category : Waste Management
> Location : Laxmi Nagar Metro Station
> Status   : assigned
>
> Your complaint is already being tracked. Send NEW to file a different complaint or STATUS to check updates.

---

## Multi-Language Support Examples

### Hinglish Example
**Citizen:** "Dwarka sector 15 mein road bahut kharab hai, potholes bhar"
**Bot Response:** [AI analysis in Hinglish with proper classification]

### Urdu Example  
**Citizen:** "janakpuri mein pani ki pipe leak ho gayi hai"
**Bot Response:** [AI analysis in Urdu with proper classification]

### Punjabi Example
**Citizen:** "Pitampura mein street lights kaam nahi kar rahe"
**Bot Response:** [AI analysis in Punjabi with proper classification]

---

## System Features Demonstrated

- **Gemini 2.5 Flash-Lite AI**: Processes 8+ Indian languages natively
- **Real-time Classification**: Category, urgency, location, ward, sentiment extraction
- **Voice Note Support**: Transcription + analysis in single API call
- **Photo Evidence**: Supabase Storage integration
- **Duplicate Detection**: Prevents redundant filings
- **ML Escalation**: GradientBoosting model (F1: 0.9273) for automatic escalation
- **Rating System**: Citizen feedback loop for service improvement
- **Officer Accountability**: Real-time assignment tracking
- **State Management**: 7-state conversation flow with database persistence

All bot messages match the exact format used in production, ensuring consistent citizen experience across Delhi's civic grievance management system.
