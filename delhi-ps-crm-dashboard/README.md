# Delhi PS-CRM - Admin Dashboard

Real-time civic grievance management dashboard for Delhi PS-CRM. Built for government officers to manage, assign, track, and resolve citizen complaints filed via WhatsApp.

## Live Dashboard
[project-tf415.vercel.app](https://project-tf415.vercel.app)

## Features

- **Real-time overview** - live stats for total, open, assigned, resolved, and critical complaints
- **Geospatial map** - complaints plotted across Delhi with urgency colour coding
- **Kanban board** - drag-and-drop complaint management across Open, In Progress, and Resolved columns
- **Officer assignment** - assign complaints to officers in one click, citizen notified instantly on WhatsApp
- **Resolution workflow** - mandatory resolution notes before closing, citizen prompted to rate
- **Analytics** - incident velocity, urgency distribution, category breakdown, resolution trends
- **Officer accountability** - per-officer resolution rates, average turnaround time, active complaint load
- **CSV export** - download complaint data for offline reporting
- **Activity timeline** - full audit trail of every officer action

## Tech Stack

- Next.js 16.2.4
- Tailwind CSS
- Recharts (analytics charts)
- Leaflet (geospatial map)
- Supabase (real-time database)

## Local Setup

```bash
npm install
npm run dev
```

Create `.env.local`:
```
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

Open [http://localhost:3000](http://localhost:3000)

## Part of Delhi PS-CRM

This dashboard is part of the [Delhi PS-CRM](https://github.com/shandilyarindam/delhi-ps-crm) system - an AI-powered WhatsApp civic grievance management platform serving all 272 wards of Delhi.

Built by Team 5Baddies, NSUT.
