# PROJECT_BIBLE.md

> **Resume Intelligence Platform --- Single Source of Truth**

------------------------------------------------------------------------

# 1. Project Metadata

**Project Name:** Resume Intelligence Platform

**Owner:** Manish Kumar Gupta

**Repository:** Resume-Intelligence-Platform-Development-

**Project Type:** AI Engineering Portfolio Project

**Target Roles** - AI Engineer - ML Engineer - GenAI Engineer

**Current Version:** v0.1.4

**Current Status:** Active Development

**Current Milestone:** Production Parser (Completed)

**Overall Progress:** ~25%

------------------------------------------------------------------------

# 2. Vision

Build a production-grade AI application that accepts a Job Description
and multiple Resume PDFs, ranks candidates semantically, explains the
ranking, and exports recruiter-friendly results.

The project prioritizes **engineering quality over feature count**.

------------------------------------------------------------------------

# 3. Completed Work

## Foundation (Claude)

-   Repository initialized
-   Production folder structure created
-   FastAPI backend scaffold
-   Streamlit frontend scaffold
-   SQLAlchemy database layer
-   Dockerfile.backend
-   Dockerfile.frontend
-   docker-compose.yml
-   README
-   LICENSE
-   requirements.txt
-   .gitignore
-   Parser scaffold
-   Embedding scaffold
-   Similarity scaffold
-   Scorer scaffold
-   Feedback scaffold
-   Utilities scaffold
-   Unit test scaffold
-   SQLite initialization
-   FastAPI Health endpoint
-   Swagger/OpenAPI
-   Local verification completed

### Local Verification

-   Dependencies installed successfully
-   pytest passing
-   FastAPI booted successfully
-   Health endpoint verified
-   Swagger verified
-   SQLite initialization verified
-   Imports verified

## Production Parser (ChatGPT, reviewed and polished by Claude)

-   `src/utils/logging_config.py`: centralized logging config (INFO
    level, timestamped, consistent format) for application-level
    loggers. Applied once at FastAPI startup.
-   Parser logs parse start, PDF open, page count, success, empty/
    scanned warnings, elapsed time, and exceptions. Resume content is
    never logged (verified: no log call references `raw_text`/`text`).
-   `src/parser/parser_benchmark.py`: CLI benchmark tool
    (`python -m src.parser.parser_benchmark <pdf> [--runs N]`),
    reporting average/min/max/std-dev via the standard library only.
    Includes a discarded warm-up run so cold-start cost (measured at
    ~2x a steady-state parse) doesn't skew Max/Std Dev.
-   Parser robustness: explicit checks for missing file, non-file
    path, and password-protected PDF, each raising `PDFParseError`
    with a clear message. OCR intentionally not implemented.
-   Parser contract unchanged: `extract_text(pdf_path) -> ParsedResume`,
    failures still raise `PDFParseError`.

### Git Note

Initial scaffold committed locally.

Push blocked because cached Git credentials belonged to company account
(`Manish-iovalence`) while repository belongs to personal account
(`Manish-OG`). Resolved by generating a Personal Access Token for the
`Manish-OG` account and reauthenticating.

------------------------------------------------------------------------

# 4. Architecture

User

↓

Streamlit

↓

FastAPI

↓

Parser

↓

Preprocessing

↓

Embeddings

↓

Similarity

↓

Scorer

↓

Feedback

↓

Database

↓

Export

------------------------------------------------------------------------

# 5. Technology Stack

Python

FastAPI

Streamlit

PyMuPDF

Sentence Transformers

PyTorch

Transformers

SQLAlchemy

SQLite

Pandas

Docker

pytest

------------------------------------------------------------------------

# 6. Folder Structure

    app/
    backend/
    frontend/

    src/
    parser/
    preprocess/
    embeddings/
    similarity/
    scorer/
    feedback/
    database/
    models/
    utils/

    tests/
    data/
    models/
    notebooks/

------------------------------------------------------------------------

# 7. Module Responsibilities

Parser - Extract raw PDF text - Return ParsedResume - No cleaning

Preprocess - Cleaning - Normalization - Section extraction

Embeddings - Generate vectors only

Similarity - Compute similarity

Scorer - Weighted scoring

Feedback - Human-readable explanations

Database - Persistence

Backend - APIs only

Frontend - UI only

------------------------------------------------------------------------

# 8. Architecture Principles

-   Single Responsibility Principle
-   Modules communicate through domain models.
-   Business logic never depends on Streamlit.
-   Business logic never depends on FastAPI.
-   Database models are not business models.
-   Prefer composition over inheritance.
-   Small testable functions.
-   Production-oriented code over tutorial code.

------------------------------------------------------------------------

# 9. Domain Models

Introduced in Session 2. Finalized in Session 3.

Current model:

ParsedResume

Purpose:

Represents parser output flowing through the AI pipeline.

Fields:

-   filename
-   raw_text
-   page_count
-   parsed_at

Reason:

Avoid passing raw strings through the pipeline.

Immutability:

`ParsedResume` is a frozen dataclass. A parse either succeeds and
produces a complete, immutable `ParsedResume`, or it fails and raises
`PDFParseError`. There is no partially-valid or mutable intermediate
state.

------------------------------------------------------------------------

# 10. Database Models

Current SQLAlchemy tables

-   Job
-   Resume
-   Candidate
-   Score
-   Feedback
-   Upload

Purpose:

Persistence only.

Not used as business/domain objects.

------------------------------------------------------------------------

# 11. Major Design Decisions

### Separate App and AI Engine

Reason: Frontend/backend can evolve independently.

Status: Accepted

------------------------------------------------------------------------

### Domain Models separate from Database Models

Reason: Business objects and persistence have different
responsibilities.

Status: Accepted

------------------------------------------------------------------------

### dataclass for Internal Domain Models

Reason: Simple, lightweight, Python standard library.

Alternative: Pydantic

Trade-off: Less validation but lower overhead.

Status: Accepted

------------------------------------------------------------------------

### SQLAlchemy only for persistence

Reason: Avoid mixing ORM with business logic.

Status: Accepted

------------------------------------------------------------------------

### Parser Contract: Exceptions, not a result type

Reason: For the current single-PDF-at-a-time milestone, raising
`PDFParseError` on failure is idiomatic Python and keeps the success
path (`ParsedResume`) simple and fully valid by construction. A
richer result type (e.g. carrying `status`/`errors` for partial
failure) was considered and rejected for now because nothing in the
codebase yet needs graceful per-file failure handling.

Revisit trigger: when batch processing is introduced and a single bad
PDF should not abort the whole batch.

Status: Accepted for current milestone; open for revision at the
batch-processing milestone.

------------------------------------------------------------------------

### ParsedResume is a frozen dataclass

Reason: It represents a completed, successful parse result. Nothing
in the codebase mutates it after construction, so making it immutable
prevents accidental mutation and reinforces that it is a value object,
not mutable state.

Status: Accepted

------------------------------------------------------------------------

### Benchmark excludes a warm-up run from reported stats

Reason: measured directly — the first `extract_text()` call in a run
is consistently ~2x slower than steady state (cold import/cache
effects). Without discarding it, Max and Std Dev mostly reflect a
one-time cost rather than real parser variance.

Status: Accepted

------------------------------------------------------------------------

### Logging is centralized for app-level loggers only

Reason: `configure_logging()` reconfigures the root logger, so any
logger obtained via `logging.getLogger(__name__)` (e.g. the parser's)
picks up the consistent format. It does **not** cover uvicorn's own
`uvicorn`/`uvicorn.error`/`uvicorn.access` loggers, which are
configured separately with `propagate=False` and keep their own
default format when the app is run via `uvicorn app.backend.main:app`.
Verified by booting the app both ways.

Status: Accepted as a known scope boundary, not a defect.

------------------------------------------------------------------------

### OCR, auto-decryption, MIME validation, multiple exception classes: rejected

Reason: none are needed yet. Scanned/image-only PDFs and
password-protected PDFs both raise `PDFParseError` with a clear
message today, which is enough until a real requirement forces
OCR or auto-decryption. A single `PDFParseError` class is sufficient
while there is exactly one caller.

Status: Accepted; revisit only if a concrete milestone needs it.

------------------------------------------------------------------------

# 12. Module Status

  Module          Status
  --------------- --------------------
  Parser          Production (logging, benchmarking, robustness)
  Domain Models   Finalized (ParsedResume)
  Preprocess      Scaffold
  Embeddings      Scaffold
  Similarity      Scaffold
  Scorer          Initial
  Feedback        Scaffold
  Database        Initial
  Backend         Working
  Frontend        Scaffold

------------------------------------------------------------------------

# 13. Testing Status

Current

✅ Parser tests passing (missing file, directory input, empty/no-text
PDF, password-protected PDF, successful parse type/filename/
page_count/raw_text, immutability)

✅ Scorer tests passing

Current Result

11 / 11 tests passing

------------------------------------------------------------------------

# 14. Verification Checklist

Completed

-   pytest
-   compileall
-   FastAPI
-   Swagger
-   Health endpoint
-   SQLite initialization
-   Parser success-path contract verified by tests
-   Benchmark CLI run and validated (correct invocation, warm-up
    excluded, ~7.9ms avg / ~0.7ms std-dev on a sample resume)
-   Logging verified in two modes: direct import (custom format
    applies) and live `uvicorn` run (app-level logs formatted;
    uvicorn's own server logs are not, by design)

------------------------------------------------------------------------

# 15. Session Log

## Session 1 (Scaffold)

Completed by Claude.

Created production scaffold, Docker, database, API, tests and
documentation.

------------------------------------------------------------------------

## Session 2 (ChatGPT)

Achievements

-   Reviewed architecture
-   Introduced domain-model architecture
-   Created src/models
-   Added ParsedResume dataclass
-   Refactored parser to return ParsedResume
-   Preserved backward compatibility
-   Verified project after refactor
-   All tests passing
-   FastAPI healthy
-   Swagger working

Lessons

-   Difference between Domain Models and Database Models
-   Why data contracts matter
-   Why dataclasses were chosen
-   Importance of architectural boundaries

------------------------------------------------------------------------

## Session 3 (Claude, feature/parser-contract-milestone)

Achievements

-   Reviewed Session 2's refactor: ran the diff, executed the parser
    against a generated PDF, and found that `status`/`errors` on
    `ParsedResume` were unreachable because `extract_text()` always
    raises on failure
-   Removed unused `status` and `errors` fields from `ParsedResume`
-   Made `ParsedResume` a frozen dataclass
-   Fixed missing trailing newline in `pdf_parser.py`
-   Added success-path tests generating a temporary PDF at test time
    (via PyMuPDF, no binary fixtures committed): return type, filename,
    page_count, raw_text content, and immutability
-   Synced this document with the repository (previous committed copy
    had drifted from the actual project state)

Lessons

-   A domain model's fields should match what the code actually
    produces; unused fields that imply an unsupported behavior are a
    real defect, not just a style nit
-   Passing tests only certify what they actually assert; a test suite
    can be green while covering none of a refactor's new behavior
-   Documentation drift is easiest to catch by diffing what's
    committed against what's claimed as current

------------------------------------------------------------------------

## Session 4 (ChatGPT: production parser; Claude: review + polish)

Achievements

-   ChatGPT added structured logging, the benchmark CLI, and
    robustness checks (missing file, non-file path, password-protected
    PDF), expanding the test suite to 11/11 passing
-   Claude reviewed by running the actual code rather than trusting
    the write-up, and found: an untracked personal resume PDF in
    `samples/` with no `.gitignore` entry (fixed), a documented
    benchmark command that fails as written (missing required `pdf`
    arg, plus a `uv run` prefix the project doesn't actually use),
    unwarmed benchmark stats skewed ~10x by cold-start cost (fixed
    with a discarded warm-up run), and a "centralized logging" claim
    that doesn't extend to uvicorn's own server logs (documented as a
    scope boundary, not fixed in code)
-   ChatGPT and Claude agreed on which findings to act on before
    syncing this document

Lessons

-   A milestone write-up's claims are only as good as running the
    actual commands it describes
-   A tool being installed on a machine (`uv`) doesn't mean a project
    uses it — check for the project's actual manifest/lockfiles
-   Untracked sample/personal files need an explicit `.gitignore`
    entry before they exist, not after

------------------------------------------------------------------------

# 16. Current TODO

High Priority

-   None open for the parser at this time. Scanned-PDF handling via
    OCR was evaluated and deliberately rejected for this milestone
    (see Section 11: "OCR, auto-decryption, MIME validation..." design
    decision) — scanned PDFs still raise `PDFParseError` with a clear
    message, which is considered sufficient until OCR is an actual
    requirement.

Medium

-   Preprocessing module
-   Section extraction
-   Email/phone extraction

Low

-   FAISS
-   PostgreSQL
-   MLflow

------------------------------------------------------------------------

# 17. Next Session

Goal

Begin the Resume Intelligence Engine milestone: resume preprocessing,
text normalization, section detection, and a structured resume
representation. Do not start embeddings, semantic search, RAG, or LLM
feedback before this milestone is complete.

Tasks

-   Preprocessing module (cleaning, normalization)
-   Section extraction (education, experience, skills, etc.)
-   Structured resume representation (new domain model, separate from
    `ParsedResume`)

------------------------------------------------------------------------

# 18. Known Technical Debt

-   Parser catches generic Exception for the fitz.open/get_text block
-   No API schemas yet
-   No relationships in SQLAlchemy models

------------------------------------------------------------------------

# 19. Performance Goals

PDF Parsing \<2 sec (met: ~7.9ms avg on a sample resume, see
benchmark in Section 3)

Embedding \<1 sec

Similarity \<200 ms

API \<1 sec

------------------------------------------------------------------------

# 20. Interview Talking Points

You should be able to explain:

-   Why domain models exist
-   Difference between ORM models and business models
-   Why parser returns ParsedResume instead of string
-   Why modules have single responsibilities
-   Why architecture matters before adding ML
-   Why ParsedResume is frozen and carries no status/errors fields
-   Why the parser raises exceptions instead of returning a result
    type, and what would change that decision

------------------------------------------------------------------------

# 21. Philosophy

This project is **not** a tutorial clone.

Goals:

-   Learn AI Engineering
-   Learn Software Engineering
-   Learn production architecture
-   Build something interview-worthy

Understanding is preferred over speed.

Quality is preferred over quantity.

------------------------------------------------------------------------

# 22. End-of-Session Checklist

Completed (Session 3)

-   Parser contract finalized (exceptions on failure, frozen
    ParsedResume on success)
-   Dead status/errors fields removed
-   Success-path tests added and passing
-   EOF newline fixed
-   PROJECT_BIBLE synced with repository

Completed (Session 4)

-   Structured logging, benchmark CLI, and robustness checks added
    (ChatGPT); reviewed by running the actual code (Claude)
-   `samples/` added to `.gitignore` (untracked personal PDF was
    previously unignored)
-   Benchmark warm-up run added, excluded from reported stats
-   Trailing whitespace fixed in pdf_parser.py
-   Logging scope documented accurately (app-level, not uvicorn's own
    server logs)
-   Benchmark CLI documented as plain `python -m ...` (not `uv run` —
    project has no `pyproject.toml`/`uv.lock`)
-   PROJECT_BIBLE synced with repository
