# MediGuide LK — Web UI

A Next.js frontend for the MediGuide LK multi-agent RAG chatbot. Talks to
the existing Python pipeline (`services/pipeline.py`) through a small
FastAPI adapter (`api_server.py`, added to the main project repo).

```
Next.js (this repo)  --HTTP-->  FastAPI (api_server.py)  -->  MedicalAIPipeline
     Vercel                          Render                    (unchanged)
```

## Design notes

Direction: **"Clinical Field Notes"** — a calm exam-room paper texture
paired with a live vitals-monitor motif, since the whole premise of the
app is "read the vital signs out of a document instead of a patient."

- **Palette** — warm paper `#F5F3EE`, deep teal ink `#16262B`, clinical
  teal primary `#0E6F63`, muted amber for "needs review" `#C1502E`, muted
  green for "verified" `#2E7D53`, warm hairline `#DAD4C4`.
- **Type** — Fraunces (display, used sparingly for the wordmark/quotes),
  Inter (body), IBM Plex Mono (citations, scores, timestamps — reads like
  a lab readout).
- **Signature element** — the pulse-line divider (`PulseDivider.tsx`): an
  EKG-style trace that sits idle as a hairline and animates left-to-right
  while a request is in flight, replacing a generic spinner.
- **Layout** — conversation on the left, a live "Retrieval Trace" panel
  on the right showing the extracted query, cited source passages, and a
  faithfulness "vitals" readout for whichever answer is selected. Mobile
  collapses the trace inline under each message.

## Local setup

1. **Backend** (from the main project repo, `diseases-rag-chatbot-DS205.3-coursework-develop/`):
   ```bash
   pip install -r requirements.txt
   uvicorn api_server:app --reload --port 8000
   ```
   Make sure `.env` has `LLM_API_KEY` set and `data/faiss_db` /
   `data/bm25_data.pkl` already exist (run `python build_database.py`
   once if not).

2. **Frontend** (this repo):
   ```bash
   npm install
   cp .env.local.example .env.local   # NEXT_PUBLIC_API_URL=http://localhost:8000
   npm run dev
   ```
   Open http://localhost:3000.

## Free deployment

**Backend → Render** (has a genuine free tier for web services; the
free instance spins down after ~15 min idle, so the first request after
a gap takes 30–60s to wake up — expected on free tier, not a bug):

1. Push the main project repo (with `api_server.py`) to GitHub.
2. On Render: New → Web Service → connect the repo.
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`
   - Add env vars: `LLM_API_KEY`, `ALLOWED_ORIGINS=https://<your-vercel-domain>`
3. `data/faiss_db` and `data/bm25_data.pkl` need to be in the repo (or
   rebuilt on deploy via `python build_database.py` as part of the build
   step) since Render's free tier has an ephemeral filesystem.

**Frontend → Vercel** (free Hobby tier, built for Next.js):

1. Push this `mediguide-web` folder to its own GitHub repo (or a
   subfolder of the same repo, setting Vercel's "Root Directory").
2. Import it on vercel.com → set env var
   `NEXT_PUBLIC_API_URL=https://<your-render-service>.onrender.com`.
3. Deploy.

Railway and Fly.io no longer have real permanent free tiers as of 2026
(trial credits only) — Render + Vercel is the free-tier-friendly combo
for this stack.
