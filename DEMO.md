# 🎬 Demo Script — Delhi PS-CRM

> **Presentation guide for Ministry officials and hackathon judges.**
> Duration: ~10 minutes | Prepared for: India Innovates Finals, Bharat Mandapam

---

## 📋 Pre-Demo Checklist

- [ ] Dashboard open in browser (full screen, dark room preferred for maximum impact)
- [ ] WhatsApp Business number ready on phone
- [ ] A second phone for live demo (citizen POV)
- [ ] Stable internet connection
- [ ] Clear the browser console (no errors visible)
- [ ] Ensure Supabase has some existing complaints for a populated dashboard

---

## 🎯 Opening Statement (30 seconds)

> *"20 million people live in Delhi. When a pipe bursts, a road caves in, or garbage piles up — how do they report it? They call a helpline that nobody answers. They file a form on a website they can't read. They download an app they'll never use again.*
>
> *What if they could just send a WhatsApp message — in Hindi — and the government actually listened?"*
>
> **"This is Delhi PS-CRM."**

---

## 🚀 Demo Flow

### Step 1: Show the Dashboard (1 minute)

**Action:** Show the Complaints tab with existing data.

**What to highlight:**
- Dark ops-room aesthetic — "Designed to feel like a government command center"
- Real-time live indicator (green dot pulsing)
- Stat cards at the top — Total, Open, Assigned, Resolved, Critical
- SLA timers color-coded — green (on time), amber (warning), red (breach)
- Escalation badges flashing on overdue critical complaints

**Talking Point:**
> *"This is what every MCD officer sees. Every complaint, every citizen, every department — in real time. No spreadsheets, no email chains, no lost files."*

---

### Step 2: Live WhatsApp Demo — Filing a Complaint (3 minutes)

**Action:** Pick up the citizen phone and send messages live.

#### Message 1: Start
```
📱 Citizen sends: Hi
```
```
🤖 Bot responds: 🏛️ Welcome to Delhi PS-CRM!
                  I help you file civic complaints with the Government of Delhi.
                  Please tell me your name to get started.
```

**Talking Point:**
> *"No app download. No login. No OTP. Just WhatsApp — the app that's already on every phone in India."*

#### Message 2: Registration
```
📱 Citizen sends: Rahul Sharma
```
```
🤖 Bot responds: Thanks, Rahul! 🙏
                  Please describe your civic complaint.
                  You can write in Hindi, English, or Hinglish.
```

**Talking Point:**
> *"Notice — we support Hindi, Hinglish, and English. 90% of Delhi thinks in Hindi. We meet them there."*

#### Message 3: File Complaint (Hindi)
```
📱 Citizen sends: Hamare Saket mein main road par ek bahut bada gadha hai,
                  2 din se koi repair nahi aaya. Bahut khatarnak hai,
                  kal raat ek auto palat gaya
```

**Talking Point:**
> *"This is real Hindi — the way real people talk. No structured form, no dropdown menus. Just natural language."*

```
🤖 Bot responds: 📋 Got it! Here's what I understood:
                  
                  🏷️ Category: Roads
                  🚨 Urgency: Critical
                  📍 Location: Saket, Main Road
                  😤 Sentiment: Frustrated
                  📝 "Large pothole on main road in Saket, unremedied for 2 days.
                       Auto-rickshaw overturned last night."
                  
                  📸 Would you like to attach a photo? Send it now, or type "no" to skip.
```

**Talking Point:**
> *"In under 2 seconds, GPT-4o has classified this as a Roads complaint, marked it Critical because of the accident, detected the citizen is frustrated, extracted the exact location, and generated an English summary for the officer. All from a Hindi message."*

#### Message 4: Photo Evidence
```
📱 Citizen sends: [Photo of pothole]
```
```
🤖 Bot responds: 📸 Photo received! Please confirm:
                  
                  Category: Roads | Urgency: Critical | Location: Saket
                  
                  Type "yes" to submit or "no" to cancel.
```

#### Message 5: Confirm
```
📱 Citizen sends: Yes
```
```
🤖 Bot responds: ✅ Complaint #A7F3B2C1 filed successfully!
                  You'll receive updates on WhatsApp as your complaint is processed.
                  Thank you for making Delhi better! 🇮🇳
```

---

### Step 3: Show Real-time Dashboard Update (1 minute)

**Action:** Switch to the dashboard — the complaint should already be there.

**What to highlight:**
- New row highlighted with blue fade animation at the top of the table
- Toast notification appeared: "New complaint: #A7F3B2C1"
- Critical urgency badge (red)
- Photo evidence icon (📷) clickable → opens lightbox
- SLA timer already ticking

**Talking Point:**
> *"The officer didn't refresh the page. They didn't check email. The complaint appeared in real-time — the moment the citizen hit send. This is Supabase Realtime at work."*

---

### Step 4: Officer Assignment (1 minute)

**Action:** Click "Assign" on the new complaint.

**What to show:**
- Officer dropdown shows names + active workload count
- Select an officer (e.g., "Ridhima Aggarwal (2 active)")
- Click "Confirm"
- Status changes from "Open" (amber) to "Assigned" (blue)
- Toast: "Assigned to Ridhima Aggarwal"

**Then switch to citizen phone:**
```
🤖 Bot sends: 📋 Update on complaint #A7F3B2C1:
               Your complaint has been assigned to Officer Ridhima Aggarwal.
               We're on it!
```

**Talking Point:**
> *"The citizen knows exactly who is handling their problem. No more black holes. Full transparency."*

---

### Step 5: Show Analytics Tab (1 minute)

**Action:** Click the Analytics tab.

**What to highlight:**
- Average resolution time
- Complaints by category (bar chart)
- Urgency distribution (doughnut chart)
- Daily trend line (last 7 days)
- Open rate percentage

**Talking Point:**
> *"This isn't just a complaint box. It's an intelligence platform. Department heads can see trends before they become crises. If road complaints spike 200% in South Delhi — they know before the news covers it."*

---

### Step 6: Show Map Tab (30 seconds)

**Action:** Click the Map tab.

**What to highlight:**
- Dark-themed Delhi map with colored markers
- Click a marker → popup with full complaint details
- Color = urgency (red = critical, amber = high, blue = medium)
- Clustering of complaints reveals problem areas

**Talking Point:**
> *"Every complaint is geocoded and plotted on a live map of Delhi. Clusters reveal systemic failures — if 15 water complaints come from the same colony, that's not 15 problems, it's one broken pipeline."*

---

### Step 7: Show Kanban Board (1 minute)

**Action:** Click the Board tab.

**What to highlight:**
- Three columns: Open → In Progress → Resolved
- Drag a card from Open to In Progress → assignment modal appears
- Cards show urgency color, category, location, summary
- Real-time count badges on each column

**Talking Point:**
> *"Officers manage their workflow like a Jira board. Drag to assign, drag to resolve. No training needed — if you've used Trello, you can use this."*

---

### Step 8: Show Scorecard Tab (1 minute)

**Action:** Click the Scorecard tab.

**What to highlight:**
- Summary bar: Best performing, Most complaints, Fastest resolution, Most problematic
- Department cards with letter grades (A–F)
- Metrics: Total, Resolved, Avg Resolution, Open Rate
- Progress bars showing resolution ratios
- Officer leaderboard (🥇🥈🥉)
- 7-day trend arrows

**Talking Point:**
> *"This is the executive report card. Every department gets graded like a school exam — A through F. The Chief Secretary can see at a glance: Which department is drowning? Which officer is a star? Where should we deploy more resources?"*

---

### Step 9: Resolve the Complaint (30 seconds)

**Action:** Go back to Complaints tab, click "Resolve" on the demo complaint.

- Enter resolution notes: "Pothole repaired by road maintenance team. Barricades placed."
- Click "Mark Resolved"
- Status changes to green "Resolved"
- SLA timer shows total resolution time

**Switch to citizen phone:**
```
🤖 Bot sends: ✅ Great news! Complaint #A7F3B2C1 has been resolved!
               
               Resolution: Pothole repaired by road maintenance team.
               Barricades placed.
               
               Thank you for making Delhi better, Rahul! 🇮🇳
```

**Talking Point:**
> *"The loop is closed. The citizen filed in Hindi on WhatsApp, AI classified it, an officer was assigned, the problem was fixed, and the citizen was notified — all without a single form, a single portal visit, or a single phone call."*

---

## 🎯 Closing Statement (30 seconds)

> *"Delhi PS-CRM isn't a prototype. It's a working system — built in 48 hours — that handles the full lifecycle of civic complaints. From a WhatsApp message in Hindi to a resolved ticket with officer notes.*
>
> *500 million Indians use WhatsApp. Zero of them need to download an app to file a complaint.*
>
> *This is how governance should work."*

---

## 📊 Key Statistics to Mention

| Stat | Value |
|---|---|
| WhatsApp users in India | 500M+ |
| Government app adoption rate | <2% |
| Average complaint classification time | <2 seconds |
| Languages supported | Hindi, Hinglish, English |
| Dashboard deployment | Single HTML file, zero server |
| AI accuracy on category classification | ~95% |
| Number of departments covered | 6 |
| Officers per department | 4 |
| Build time | 48 hours |
| Lines of code (dashboard) | ~1,100 |

---

## 💬 Sample Complaints for Demo

### Hindi Complaints

| # | Message | Expected Category | Expected Urgency |
|---|---|---|---|
| 1 | `Hamare gali mein 3 din se kachra pada hai, bahut badbu aa rahi hai` | Waste Management | High |
| 2 | `Saket main road par bahut bada gadha hai, kal auto palat gaya` | Roads | Critical |
| 3 | `2 din se paani nahi aa raha, bacche bimar ho rahe hain` | Water Supply | Critical |
| 4 | `Nali band ho gayi hai, ghar ke aage paani bhar gaya` | Sewage & Drainage | High |
| 5 | `Streetlight 1 hafte se kharab hai, raat mein andhera rehta hai` | Electricity | Medium |

### English Complaints

| # | Message | Expected Category | Expected Urgency |
|---|---|---|---|
| 6 | `There is a massive garbage pile near the park in Dwarka Sector 12, it's been there for a week` | Waste Management | High |
| 7 | `Water pipeline burst on MG Road near metro station, water wasting for 3 hours` | Water Supply | Critical |
| 8 | `Multiple potholes on Ring Road near Moolchand, caused 2 accidents this week` | Roads | Critical |
| 9 | `Sewage overflow in Lajpat Nagar market, health hazard for shop owners` | Sewage & Drainage | Critical |
| 10 | `Power cut in entire Rohini Sector 9 since morning, no update from BSES` | Electricity | High |

### Hinglish Complaints

| # | Message | Expected Category | Expected Urgency |
|---|---|---|---|
| 11 | `Yaar hamare area mein garbage truck aana band ho gaya hai, 5 din ho gaye` | Waste Management | High |
| 12 | `Road completely broken near Connaught Place, daily traffic jam hota hai` | Roads | Medium |
| 13 | `Water supply bohot low pressure aa raha hai, 4th floor tak nahi pahunchta` | Water Supply | Medium |

---

## ⚠️ Troubleshooting During Demo

| Issue | Fix |
|---|---|
| Dashboard not loading | Check internet, refresh page |
| WhatsApp bot not responding | Check n8n workflow is active |
| Complaint not appearing on dashboard | Check Supabase Realtime is enabled |
| Map not showing markers | Nominatim rate limit — wait 30 seconds |
| Charts not rendering | Click Analytics tab again to re-render |

---

*Prepared for India Innovates Finals — Bharat Mandapam, New Delhi*
