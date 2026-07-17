# PROJECT BIBLE
# A Production-Grade AI Resume Intelligence Platform

> **Purpose:** This document is the single source of truth for the project. Any AI assistant (ChatGPT, Claude, Gemini, etc.) should read this file before giving advice or generating code.

---

# 1. AI CONTEXT

If you're an AI assistant:

- Read this file completely before suggesting anything.
- This is a long-term AI Engineering portfolio project.
- The goal is learning, not just finishing.
- Explain **WHY** before **HOW**.
- Do not rewrite working modules unless requested.
- Never change architecture without discussion.
- Prioritize modular, scalable, interview-quality implementations.
- If uncertain, explicitly mention assumptions.
- Keep code production-oriented rather than tutorial-oriented.
- At the end of every session, help update this file.

---

# 2. PROJECT METADATA

Project Name:
Resume Intelligence Platform

Owner:
Manish Kumar Gupta

Repository:

Version:
v0.1.0

Project Type:
AI Engineering Portfolio Project

Target Roles:
- AI Engineer
- ML Engineer
- GenAI Engineer

Status:
Planning

Project Start:

Target Completion:

Current Phase:

Current Milestone:

Current Session:

Current Branch:

Current Commit:

Overall Progress:

Last Updated:

---

# 3. PROJECT OVERVIEW

## Goal

Build a production-style AI web application that accepts one Job Description and multiple Resume PDFs, semantically ranks candidates, identifies missing skills, generates explainable feedback, and exports results.

---

## Objectives

- Demonstrate AI Engineering skills
- Learn production-level project architecture
- Learn FastAPI
- Learn Docker
- Learn NLP with PyTorch
- Build an interview-worthy GitHub project

---

## Target Users

- Recruiters
- HR Teams
- Hiring Managers

---

# 4. PROJECT SCOPE

## MVP Features

- Upload Job Description
- Upload Multiple Resume PDFs
- PDF Parsing
- Text Preprocessing
- Resume Embeddings
- Semantic Matching
- Skill Extraction
- Candidate Ranking
- Explainable Feedback
- SQLite Database
- FastAPI Backend
- Streamlit Frontend
- CSV Export
- Docker Support

---

## Out of Scope (MVP)

- Authentication
- PostgreSQL
- OCR
- LLM Feedback
- Fine-tuned Transformer
- Cloud Deployment
- Recruiter Dashboard

---

# 5. PROJECT ARCHITECTURE

User

↓

Streamlit Frontend

↓

FastAPI Backend

↓

Resume Parser

↓

Text Preprocessing

↓

Embedding Engine

↓

Similarity Engine

↓

Scoring Engine

↓

Feedback Generator

↓

SQLite Database

↓

Export Results

---

# 6. TECHNOLOGY STACK

Language

- Python

AI

- PyTorch
- Hugging Face
- Sentence Transformers

Backend

- FastAPI

Frontend

- Streamlit

Database

- SQLite

PDF Parsing

- PyMuPDF

Data Processing

- Pandas

Deployment

- Docker

Testing

- pytest

Version Control

- Git
- GitHub

Future

- PostgreSQL
- FAISS
- MLflow

---

# 7. PROJECT STRUCTURE

```
resume-intelligence-platform/

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
    utils/

tests/

models/

data/

notebooks/

Dockerfile
docker-compose.yml
requirements.txt
README.md
PROJECT_BIBLE.md
```

---

# 8. MODULE RESPONSIBILITIES

Parser
- Extract text from PDFs
- No preprocessing
- No scoring

Preprocess
- Clean text
- Normalize
- Section extraction

Embeddings
- Generate embeddings only

Similarity
- Compute similarity only

Scorer
- Generate weighted score

Feedback
- Generate explanations

Database
- Store all persistent data

Frontend
- User interaction only

Backend
- API endpoints only

---

# 9. DATA FLOW

Resume PDF

↓

Parser

↓

Clean Text

↓

Section Extraction

↓

Embedding Generation

↓

Similarity

↓

Weighted Score

↓

Feedback

↓

Database

↓

Frontend

---

# 10. DATA CONTRACTS

Parser

Input

Resume.pdf

Output

- Raw Text
- Metadata

---

Embedding

Input

String

Output

Embedding Vector

---

Similarity

Input

Resume Embedding

JD Embedding

Output

Similarity Score

---

Scorer

Output

Semantic Score

Skill Score

Experience Score

Education Score

Final Score

Recommendation

---

# 11. DEVELOPMENT ROADMAP

Day 1

Environment
Repository
Project Structure

Day 2

PDF Parsing

Day 3

Preprocessing

Day 4

Embeddings

Day 5

Skill Extraction

Day 6

Scoring

Day 7

FastAPI

Day 8

Streamlit

Day 9

SQLite

Day 10

Feedback

Day 11

Batch Processing

Day 12

Docker

Day 13

Testing

Day 14

Documentation
Deployment
Demo

---

# 12. CURRENT STATUS

Completed

-

-

-

In Progress

-

Next

-

---

# 13. CURRENT TODO

High Priority

-

Medium Priority

-

Low Priority

-

---

# 14. DESIGN DECISIONS

Decision

Reason

Alternatives

Trade-offs

Status

Example

Decision

SQLite

Reason

Simple MVP

Alternative

PostgreSQL

Trade-off

Less scalable

Status

Accepted

(Add future decisions below this.)

---

# 15. DEPENDENCIES

Python

FastAPI

Streamlit

PyTorch

Sentence Transformers

Transformers

PyMuPDF

SQLAlchemy

Pandas

pytest

Docker

---

# 16. CODING STANDARDS

Style

PEP8

Naming

snake_case

Classes

PascalCase

Constants

UPPER_CASE

Function Rules

- Single responsibility
- Small functions
- Type hints
- Docstrings

Maximum Function Size

~50 lines

Maximum File Size

~300 lines

---

# 17. GIT WORKFLOW

Branch Strategy

main

↓

feature/parser

↓

feature/preprocess

↓

feature/embeddings

↓

feature/scorer

↓

feature/frontend

↓

merge

Commit Convention

feat:

fix:

docs:

refactor:

test:

style:

perf:

chore:

---

# 18. SESSION LOG

## Session Template

Date:

Goals:

Completed:

Problems:

Solutions:

Lessons Learned:

Files Modified:

Commit:

Next Session Goal:

(Add every session below.)

---

# 19. CHANGELOG

v0.1.0

Project Initialized

v0.2.0

Parser

v0.3.0

Preprocessing

(Update continuously.)

---

# 20. ERROR LOG

Date

Problem

Root Cause

Solution

Status

(Add future issues.)

---

# 21. KNOWN LIMITATIONS

- Dictionary-based skill extraction
- SQLite only
- No OCR
- No Authentication
- No multilingual support
- No fine-tuned model

---

# 22. FUTURE ROADMAP

Version 2

- PostgreSQL
- FAISS
- Fine-tuning

Version 3

- LLM Feedback
- Recruiter Dashboard

Version 4

- Authentication
- OCR
- Analytics Dashboard

---

# 23. PERFORMANCE GOALS

PDF Parse

<2 sec

Embedding

<1 sec

Similarity

<200 ms

API Response

<1 sec

---

# 24. LEARNING NOTES

(Add concepts learned.)

Example

Today I learned

- Sentence Transformers
- Cosine Similarity
- FastAPI Dependency Injection

---

# 25. INTERVIEW STORIES

Challenge

Problem

Solution

Result

Lesson

(Add important experiences.)

---

# 26. REFERENCES

Datasets

Documentation

Research Papers

Articles

Useful GitHub Repositories

---

# 27. PROJECT PHILOSOPHY

This is NOT a tutorial project.

This is NOT a cloned GitHub repository.

This project should demonstrate:

- AI Engineering
- Software Engineering
- Clean Architecture
- Testing
- Deployment
- Documentation
- Interview Readiness

Quality is preferred over quantity.

Understanding is preferred over speed.

Every implementation should be explainable.

---

# 28. END OF SESSION CHECKLIST

Before ending a session:

- Update Current Status
- Update TODO
- Update Session Log
- Update Changelog
- Record Design Decisions (if any)
- Record Errors (if any)
- Commit changes
- Push to GitHub
- Decide next session's goal

---

# 29. NOTES

(Free space for ideas, reminders, feature requests, random thoughts, or future improvements.)
