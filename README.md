# MentalFlow - AI-Powered Mental Health Platform

Adaptive behavioral activation system with RL + GAN personalization.

## Tech Stack
- Frontend: React 18 + Vite + TypeScript + Tailwind
- Backend: FastAPI + Python
- AI: RL (PPO), GAN, LLM (Groq)
- Database: PostgreSQL

## Quick Start
```bash
# Backend (Python 3.10+)
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
# Tests
pytest

# Frontend
cd ../frontend
npm install
npm run dev
```

## Configuration
Settings are read from environment variables or `backend/.env` (never commit it):
- `SECRET_KEY`, `ENCRYPTION_KEY`: must be set for any real deployment (the built-in defaults are for local development only; the backend logs a warning when they are used).
- `DATABASE_URL`: defaults to a local SQLite file `backend/mentalflow.db`, created on first start.
- `GROQ_API_KEY`: optional. Without it the chatbot and activity generator run in offline fallback mode.

## Features
✅ RL-based difficulty adaptation
✅ GAN-generated personalized activities
✅ Clinical AI chatbot
✅ PHQ-9/GAD-7 assessments
✅ Mood tracking
✅ Gamification (XP, levels, streaks)

## Status
🚀 Production Ready
