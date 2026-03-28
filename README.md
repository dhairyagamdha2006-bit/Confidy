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

## Deployment

### Frontend
The frontend is deployed on **Netlify**.

### Python Backend
The NLP backend is deployed separately on **Render**.

---

## Why I Built This

Confidy was built to make communication growth measurable, interactive, and practical.

A lot of advice around confidence is vague. Confidy turns it into something users can actually train:

- practice conversations
- get immediate coaching
- track progress over time
- improve through repeated sessions

The goal is to make confidence feel trainable, not mysterious.

---

## Current Highlights

- Full authentication and password reset flow
- Real-time AI coaching
- Persistent chat/session storage
- Session dashboard and history management
- Delete session history support
- Python-powered scoring and summaries
- Personalized rewrite suggestions

---

## Future Improvements

- Stronger dashboard analytics and graphs
- More advanced NLP scoring
- Richer session summaries
- More scenario variety
- Better modular frontend structure
- Multi-model AI routing
- Long-term progress insights across sessions

---

## Resume Summary

**Built Confidy, an AI-powered confidence coaching web app that combines realistic conversation practice, live feedback, session persistence, and Python-based language analysis to help users improve communication skills and track measurable growth over time.**

---

## Author

**Dhairya Gamdha**

---

## License

This project is for educational and portfolio purposes.
