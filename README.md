# Resume Intelligence Platform

An AI application that ranks resumes against a job description using semantic
similarity and skill matching, explains each score, flags missing skills, and
exports the results.

> Work in progress — see [Roadmap](#roadmap) for build status.

## Architecture

```
User -> Streamlit Frontend -> FastAPI Backend -> Resume Parser -> Embedding Engine
     -> Scoring Engine -> Feedback Generator -> SQLite Database -> Export (CSV/Excel)
```

## Tech Stack

Python, PyTorch, Sentence Transformers, PyMuPDF, FastAPI, Streamlit, SQLite,
FAISS, Pandas, Docker.

## Project Structure

```
app/
  backend/        FastAPI app, routes, config
  frontend/       Streamlit UI
src/
  parser/         PDF text extraction
  preprocess/     Text cleaning/normalization
  embeddings/     Sentence-transformer encoding
  similarity/     Cosine similarity computation
  scorer/         Weighted scoring engine
  feedback/       Strengths/weaknesses/recommendation generation
  database/       SQLAlchemy models + session
  utils/          Shared helpers (file validation, etc.)
models/           Saved model checkpoints (gitignored)
data/             Sample resumes/JDs for local testing (gitignored)
notebooks/        Exploration notebooks
tests/            Unit/integration tests
```

## Getting Started

```bash
python -m venv .venv
source .venv/bin/activate  # .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Run the API
uvicorn app.backend.main:app --reload

# Run the frontend (separate terminal)
streamlit run app/frontend/streamlit_app.py

# Run tests
pytest
```

### With Docker

```bash
docker compose up --build
```

Backend: http://localhost:8000/docs · Frontend: http://localhost:8501

## Scoring

Final score is a configurable weighted blend:

| Component  | Default Weight |
|------------|-----------------|
| Semantic match  | 50% |
| Skill match     | 30% |
| Experience match| 10% |
| Education match | 10% |

## Roadmap

- [x] Project scaffold
- [ ] PDF parsing
- [ ] Text preprocessing
- [ ] Embeddings + semantic similarity
- [ ] Skill extraction + matching
- [ ] Weighted scoring engine
- [ ] FastAPI backend
- [ ] Streamlit frontend
- [ ] SQLite persistence
- [ ] Feedback generation
- [ ] Batch processing + error handling
- [ ] Dockerization
- [ ] Tests + docs
- [ ] Deployment

## License

MIT
