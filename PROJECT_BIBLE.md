# PROJECT_BIBLE.md

> **Resume Intelligence Platform --- Single Source of Truth**

------------------------------------------------------------------------

# 1. Project Metadata

**Project Name:** Resume Intelligence Platform

**Owner:** Manish Kumar Gupta

**Repository:** Resume-Intelligence-Platform-Development-

**Project Type:** AI Engineering Portfolio Project

**Target Roles** - AI Engineer - ML Engineer - GenAI Engineer

**Current Version:** v0.1.3

**Current Status:** Active Development

**Current Milestone:** Parser Contract Finalization

**Overall Progress:** ~20%

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

# 12. Module Status

  Module          Status
  --------------- --------------------
  Parser          Contract Finalized
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

✅ Parser tests passing (missing file, empty/no-text PDF, successful
parse type/filename/page_count/raw_text, immutability)

✅ Scorer tests passing

Current Result

9 / 9 tests passing

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

# 16. Current TODO

High Priority

-   Add parser logging
-   Add parser performance metrics
-   Handle malformed/scanned PDFs better

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

Add structured logging and benchmarking to the parser, per the
reordered roadmap agreed after Session 3's review.

Tasks

-   Structured logging around parse attempts (success/failure, timing)
-   Parser benchmarking (target: PDF parsing < 2 sec, see Section 19)
-   Only after logging/benchmarking: proceed to preprocessing

------------------------------------------------------------------------

# 18. Known Technical Debt

-   Parser catches generic Exception
-   No structured logging
-   No parser metrics
-   No API schemas yet
-   No relationships in SQLAlchemy models

------------------------------------------------------------------------

# 19. Performance Goals

PDF Parsing \<2 sec

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

Completed

-   Parser contract finalized (exceptions on failure, frozen
    ParsedResume on success)
-   Dead status/errors fields removed
-   Success-path tests added and passing
-   EOF newline fixed
-   PROJECT_BIBLE synced with repository
