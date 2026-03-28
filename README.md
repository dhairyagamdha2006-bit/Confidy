# Confidy

**Confidy** is an AI-powered confidence coaching platform that helps users build real-world communication skills through realistic conversation practice, live feedback, personalized scoring, and progress tracking.

It is designed to help users confidently approach people, start conversations naturally, handle rejection better, and build stronger social presence over time.

**Live Demo:** https://confidy.netlify.app

---

## Overview

Confidy turns confidence-building into an interactive training experience.

Instead of giving generic advice, it lets users practice conversations in realistic scenarios, receive AI coaching, track progress across sessions, and improve through structured feedback and language analysis.

The platform combines:
- scenario-based AI coaching
- persistent session history
- progress dashboards
- Python-powered communication analysis
- rewrite suggestions and session summaries

---

## Features

- AI-powered conversation coaching
- Realistic scenario-based practice
- User authentication with Supabase
- Password reset flow
- Persistent conversation and session history
- Dashboard with saved progress and skill tracking
- Delete individual or all old sessions
- Live scoring for:
  - Opening quality
  - Conversation flow
  - Rejection resilience
  - Mindset framing
- Rewrite suggestions and feedback summaries
- Session-based progress tracking
- Python backend for deeper language analysis

---

## Practice Areas

Confidy currently focuses on communication and confidence training in scenarios such as:

- Approaching and starting conversations
- Texting and online conversations
- Rejection recovery and mindset
- Social confidence and group dynamics
- Workplace confidence
- Realistic live coaching simulations

---

## Tech Stack

### Frontend
- HTML
- CSS
- JavaScript

### Backend
- Netlify Functions
- Python FastAPI

### Database / Auth
- Supabase

### AI / NLP
- Claude
- Python-based language analysis engine

### Deployment
- Netlify
- Render

---

## How It Works

1. A user signs up or logs in.
2. The user selects a coaching scenario.
3. Confidy starts an AI-powered conversation practice session.
4. Messages and sessions are saved in Supabase.
5. A Python backend analyzes user responses for communication and confidence signals.
6. Skill scores and feedback are updated live.
7. Users can review, resume, or delete previous sessions from the dashboard.

---

## Architecture

```text
Confidy
├── Frontend (HTML/CSS/JS)
│   ├── Landing page
│   ├── Auth flow
│   ├── Dashboard
│   ├── Chat UI
│   └── Skill tracking
│
├── Backend
│   ├── Netlify Function for AI chat
│   └── Python FastAPI service for scoring + summaries
│
├── Data Layer
│   ├── Supabase Auth
│   ├── Profiles
│   ├── Conversations
│   └── Messages
