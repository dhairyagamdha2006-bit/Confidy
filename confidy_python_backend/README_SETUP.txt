Confidy Python NLP Backend Setup

Folder placement:
- Put the whole folder `confidy_python_backend` in the root of your GitHub repo.
- Final repo shape should look like this:
  /index.html
  /netlify.toml
  /netlify/functions/chat.js
  /confidy_python_backend/requirements.txt
  /confidy_python_backend/render.yaml
  /confidy_python_backend/app/main.py
  /confidy_python_backend/app/schemas.py
  /confidy_python_backend/app/nlp_engine.py

Local run:
1. cd confidy_python_backend
2. python3 -m venv venv
3. source venv/bin/activate
4. pip install -r requirements.txt
5. uvicorn app.main:app --reload
6. Open http://127.0.0.1:8000/docs

Deploy on Render:
1. Push confidy_python_backend folder to GitHub.
2. In Render, create a New Web Service.
3. Select the same GitHub repo.
4. Set Root Directory = confidy_python_backend
5. Build Command = pip install -r requirements.txt
6. Start Command = uvicorn app.main:app --host 0.0.0.0 --port $PORT
7. Deploy.
8. Copy your Render URL, for example: https://confidy-nlp-api.onrender.com

Frontend/API integration:
- Your frontend or netlify/functions/chat.js should call:
  POST https://YOUR-RENDER-URL/analyze-message
  POST https://YOUR-RENDER-URL/score-session
  POST https://YOUR-RENDER-URL/session-summary

Suggested integration strategy:
- Keep Anthropic chat in netlify/functions/chat.js
- Call Python only for analysis/scoring
- Save Python results to Supabase later if desired
