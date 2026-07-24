# Demo Guide — Resume Intelligence Platform

A practical guide for running this project live and walking someone through
it. Two audiences in mind: **you, prepping before a demo**, and **anyone
else who clones this repo and wants to see it work.**

------------------------------------------------------------------------

## 1. Before you demo — a clean run-through

Do this once, in private, before showing it to anyone. It catches the two
most common surprises (cold-start delay, leftover test data) before they
happen live.

### 1.1 Reset to a clean state (optional, recommended)

If you've been testing locally, `data/app.db` may have leftover candidates
from earlier runs — `/rank` scores *every* resume ever uploaded against
whatever job you pick, so old test data will show up in results.

Stop any running backend first (Ctrl+C), then:

```cmd
:: Windows cmd.exe
del /f data\app.db
del /q data\uploads\*
```

```bash
# Git Bash / macOS / Linux
rm -f data/app.db
rm -rf data/uploads/*
```

It recreates itself automatically the next time the backend starts.

### 1.2 Pick your demo files

You'll want:
- One job description PDF (a real one reads better than a synthetic one)
- 2-3 resume PDFs — ideally one strong match, one weak match, and one with
  an interesting edge case (e.g. no clearly-dated Experience section) —
  this lets you show the honest-limitations behavior on purpose instead
  of stumbling into it live.

------------------------------------------------------------------------

## 2. Running it

Two ways to run this. Docker is what you'd actually ship; plain Python is
faster to restart between test runs while you're prepping.

### 2.1 Plain Python (fastest iteration)

```bash
python -m venv .venv.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

# Terminal 1 — backend
uvicorn app.backend.main:app --reload

# Terminal 2 — frontend
python -m streamlit run app/frontend/streamlit_app.py
```

**Important:** always use `python -m streamlit run`, never bare
`streamlit run`. The bare form doesn't add the project root to
`sys.path`, and the frontend imports from the top-level `app` package —
you'll get `ModuleNotFoundError: No module named 'app'` otherwise. (This
bit both the Docker image and a live local run before it was fixed —
see `PROJECT_BIBLE.md`, Session 25, if you want the full story.)

Frontend: `http://localhost:8501`
Backend Swagger docs: `http://localhost:8000/docs`

### 2.2 Docker (what you'd actually ship)

```bash
docker-compose up --build
```

Same URLs as above. First build takes several minutes (`torch` +
`sentence-transformers` are large downloads); subsequent builds are
faster via layer caching. Verified working end-to-end, including
container-to-container networking (frontend reaches backend via
`http://backend:8000`, not `localhost`).

------------------------------------------------------------------------

## 3. The live walkthrough

A script you can follow, adapt, or ignore in favor of your own words —
but the *order* matters: it front-loads credibility (Swagger, real API)
before the part people will have opinions about (the actual scores).

### Step 1 — Show the API is real (30 seconds)

Open `http://localhost:8000/docs`. Point out the actual routes
(`/upload-job`, `/upload-resume`, `/rank`, `/results`, `/download`).
This establishes it's a real backend with a documented contract, not a
demo hack.

### Step 2 — Upload

Switch to the frontend. Type a job title, drop in the JD PDF, drop in
2-3 resume PDFs, click **Upload**. Call out:
- The two-step Upload/Rank split — uploading is persistent, ranking is
  cheap to retry.
- If you deliberately include a corrupt file: it gets skipped with a
  warning, the rest still upload. (Genuinely useful to demo on purpose —
  shows you thought about failure modes, not just the happy path.)

### Step 3 — Rank

Click **Rank candidates**. If the backend just started, call out the
cold-start caption *before* it appears — "first ranking after a restart
loads the AI model, ~20-30 seconds; every one after that is fast." This
pre-empts anyone thinking it's frozen.

### Step 4 — Read one result together

Pick your strongest-match resume. Point at the **Final Score** first —
it's the number people look for. Then expand **Details** and walk
through:
- The four component scores (Semantic / Skill / Experience / Education)
  and what each one actually measures.
- The **Strengths** / **Weaknesses** text — specifically call out any
  honest "couldn't verify" language if it shows up. This is the single
  best moment in the demo: it's proof the system doesn't fabricate
  confidence it doesn't have.
- If `missing_skills` doesn't appear for a candidate: mention that's
  deliberate — `None` means "not computed," and the UI won't pretend
  that's the same as "nothing missing."

### Step 5 — Name what's next, unprompted

Before anyone asks "is this accurate," say it yourself: *"The scoring
model itself is the intentionally unpolished part — small pretrained
embedding model, exact-keyword skill matching, validated against a
handful of real resumes. The focus here was the system around the
model: architecture, tests, honest failure handling, Docker packaging."*
Saying this first turns a potential gotcha into a demonstration of
self-awareness.

------------------------------------------------------------------------

## 4. Questions to be ready for

**"Why did my resume score so low?"**
> Usually one of: the JD and resume use different wording for the same
> skills (the embedding model measures phrasing overlap, not just
> meaning), the Experience section doesn't have a machine-parseable date
> range, or the exact-keyword skill matcher missed a synonym. All three
> are named, known limitations — not bugs.

**"Would you trust this to actually screen candidates?"**
> No — and saying that directly is the right answer, not a weakness.
> Real resume screening has real consequences (bias, false negatives on
> qualified people); this is a demonstration of engineering practice, not
> a validated hiring tool.

**"What would you change to make it more accurate?"**
> Fine-tune or swap in an embedding model trained on resume/JD pairs,
> replace exact-keyword skill matching with something synonym-aware, and
> build a real labeled validation set to measure against — instead of
> hand-tuning against one or two real resumes.

**"Is this AI-generated?"**
> Built with Claude Code as an AI pair-programmer, with every
> architectural decision — and the plan-then-cross-review workflow used
> throughout — driven by you. Full design history is in
> `PROJECT_BIBLE.md` if anyone wants to check.

------------------------------------------------------------------------

## 5. If something breaks mid-demo

- **`ModuleNotFoundError: No module named 'app'`** — you ran bare
  `streamlit run`. Stop it, restart with `python -m streamlit run
  app/frontend/streamlit_app.py`.
- **Rank button does nothing / spinner never resolves** — check the
  backend terminal for errors; a fresh backend process needs ~20-30s on
  its *first* rank call while the embedding model loads. Don't panic
  before that window has passed.
- **Old/unexpected candidates in results** — `data/app.db` has leftover
  data from earlier testing. See Section 1.1 to reset it.
- **Docker frontend container won't start** — confirm both images were
  built after the `Dockerfile.frontend` `CMD` fix (`python -m streamlit
  run`, not bare `streamlit run`). `docker-compose build --no-cache
  frontend` if in doubt.

------------------------------------------------------------------------

## 6. Where to point people for more depth

- `README.md` — quick overview, stack, getting started.
- `PROJECT_BIBLE.md` — the full story: every design decision, every
  session's work, every known limitation and why it's there, ~90
  interview talking points tied to real code. This is the single source
  of truth if anyone wants to go deep.
