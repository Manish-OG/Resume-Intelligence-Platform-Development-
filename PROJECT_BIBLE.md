# PROJECT_BIBLE.md

> **Resume Intelligence Platform --- Single Source of Truth**

------------------------------------------------------------------------

# 1. Project Metadata

**Project Name:** Resume Intelligence Platform

**Owner:** Manish Kumar Gupta

**Repository:** Resume-Intelligence-Platform-Development-

**Project Type:** AI Engineering Portfolio Project

**Target Roles**
- AI Engineer
- ML Engineer
- GenAI Engineer

**Current Version:** v0.5.0

**Current Status:** Active Development

Current Milestone:
Resume Intelligence Engine (In Progress)

Latest Completed Milestone:
Pipeline Orchestration (parse → preprocess → detect sections → extract contact info)

**Overall Progress:** ~44%

Caveat on that number (added Session 8, read before trusting it): ~44%
reflects a solid, well-tested *foundation* on the resume-ingestion
side only. It does **not** mean 44% of the working product described
in the Vision below exists. As of end of Session 8, there is **no
path a user can run end-to-end** — see Section 12 (Module Status) and
Section 18 (Known Technical Debt) for the honest breakdown of what's
built vs. scaffold vs. not started at all.

Git Note (added Session 8): everything from Session 5 onward
(`StructuredResume` through `src/pipeline.py`) is uncommitted working-
tree state — `git status` shows only the original scaffold merge as
committed history. A new session should confirm with the user whether
to commit before doing further work, since a large amount of
uncommitted work is currently sitting in the working tree.

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

## Preprocessing Pipeline Foundation (Session 5)

- Introduced `StructuredResume` as a new immutable domain model.
- Established a preprocessing contract:
  - Input: `ParsedResume`
  - Output: `StructuredResume`
- Implemented the initial preprocessing pipeline.
- Implemented safe, non-destructive text normalization:
  - Normalize line endings
  - Replace tabs with spaces
  - Remove trailing whitespace
  - Collapse excessive blank lines
  - Trim document boundaries
- Preserved parser metadata throughout preprocessing.
- Added dedicated preprocessing unit tests.
- Verified preprocessing independently of downstream AI modules.

## Resume Section Detection (Session 6, Claude)

- Introduced `Section` and `SectionedResume` as new immutable domain
  models (`SectionType` is the codebase's first Enum: a `str, Enum`
  taxonomy of HEADER/SUMMARY/EXPERIENCE/EDUCATION/SKILLS/PROJECTS/
  CERTIFICATIONS/OTHER).
- Implemented `detect_sections(StructuredResume) -> SectionedResume`
  in `src/preprocess/section_detector.py`: a pure-stdlib, exact-match
  heuristic against a curated heading-keyword table (no NLP
  dependency added).
- Heuristic distinguishes a real heading line ("Education",
  "Work Experience:") from a content line that merely contains a
  keyword ("5 years of experience...") by requiring an exact
  normalized match, not a substring match.
- Detection never raises: a document with no recognized headings
  falls back to a single `OTHER` section; empty/whitespace-only text
  produces zero sections.
- Deliberately did **not** extend `StructuredResume` itself, despite
  that wording in the prior session's TODO — doing so would have
  meant mutating a frozen, previous-stage domain model, which
  contradicts the already-Accepted "One Domain Model Per Processing
  Stage" decision (Section 11). A new domain model was used instead.
- Not wired into `preprocessor.preprocess()`, embeddings, or the
  scorer yet — scoped as one incremental milestone (detect and
  represent only), per Session 5's own lesson about small PRs.
- Added 15 unit tests; verified manually against a realistic
  multi-section resume string (header, summary, experience with two
  entries, education, skills, projects) with correct boundaries and
  colon/case handling.

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

Extraction

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
    extraction/
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

Preprocess - Cleaning - Normalization - Section detection

Extraction - Pull structured facts out of detected sections (contact info now; education/experience/skills entries planned)

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

Current models

## ParsedResume

Purpose

Represents the immutable output of the PDF parser.

Fields

- filename
- raw_text
- page_count
- parsed_at

Produces

Parser

---

## StructuredResume

Purpose

Represents the normalized resume produced by the preprocessing pipeline.

Fields

- filename
- normalized_text
- page_count
- processed_at

Produces

Preprocessing

Reason

Keeps parser output separate from preprocessing output and establishes a stable contract for downstream AI modules.

---

## Section / SectionType

Purpose

`Section` represents one detected region of a resume (heading + content). `SectionType` is a `str` Enum giving a closed taxonomy: HEADER, SUMMARY, EXPERIENCE, EDUCATION, SKILLS, PROJECTS, CERTIFICATIONS, OTHER.

Fields (`Section`)

- section_type
- heading
- content

Produces

Section detection

---

## SectionedResume

Purpose

Represents a resume broken into detected sections, produced by section detection.

Fields

- filename
- page_count
- processed_at
- sections (tuple of `Section`)

Produces

Section detection

Reason

Keeps section detection's output separate from `StructuredResume` rather than mutating it, per the "One Domain Model Per Processing Stage" decision (Section 11).

---

## ContactInfo

Purpose

Email and phone number extracted from a `SectionedResume`'s HEADER section.

Fields

- email (str | None)
- phone (str | None)

Produces

Contact extraction (`src/extraction/contact_extractor.py`)

Reason

Deliberately not bundled into a broader `ExtractedResume` aggregate yet — see Section 11's "Extraction fields introduced only as they're implemented" decision. A standalone, narrowly-scoped value object avoids repeating the unused-fields mistake already logged in Session 3.

All domain models are immutable (`frozen=True`) value objects.

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

### One Domain Model Per Processing Stage

Reason

Each major stage of the AI pipeline owns its own immutable domain model.

Parser → ParsedResume

Preprocessor → StructuredResume

Section Detection → SectionedResume

Extraction → ContactInfo (and future extraction models)

Future stages may introduce additional domain models where appropriate rather than mutating previous-stage objects.

Benefits

- Clear module boundaries
- Easier testing
- Better maintainability
- Strong contracts
- Separation of responsibilities

Status

Accepted

------------------------------------------------------------------------

### Extraction fields introduced only as they're implemented

Reason: An `ExtractedResume` aggregate (contact, education, experience,
skills, certifications, projects) was considered for the Extraction
stage instead of standalone models like `ContactInfo`. Rejected for
now — placeholder `education`/`experience`/`skills` fields on an
aggregate that only contact extraction populates would repeat the
exact mistake Session 3 already caught and fixed on `ParsedResume`
(unused `status`/`errors` fields implying unsupported behavior). Each
extracted concept gets its own narrow model as it's actually
implemented; a bundling `ExtractedResume` can be introduced once more
than one extracted thing exists to bundle.

Status: Accepted for the current milestone; revisit once a second
extraction slice (e.g. education/experience entries) actually lands.

------------------------------------------------------------------------

### Contact extraction: stdlib regex, not a phone-parsing library

Reason: `phonenumbers` (libphonenumber) would give accurate,
locale-aware international phone parsing, but would be the first new
dependency added since the project's initial scaffold, and only for
one field. Chosen instead: a stdlib `re` pattern covering common NANP
formats (with/without `+1`, parens/dashes/dots/spaces as separators).
Accepted, documented gap: non-NANP international formats and
extensions are not recognized. Consistent with the project's existing
habit of not adding a dependency until a concrete need forces it
(same reasoning already applied to OCR, auto-decryption, MIME
validation in the Parser milestone).

Status: Accepted; revisit if real resumes surface enough
non-US phone formats to matter.

------------------------------------------------------------------------

# 12. Module Status

| Module | Status |
|---------|--------|
| Parser | Production (resumes only — see Job Description row) |
| Domain Models | Production |
| Preprocessing | Foundation Complete + Section Detection |
| Extraction | Contact Info Only (education/experience/skills not extracted) |
| Pipeline Orchestration | Function exists (`src/pipeline.py`), not called from API |
| Job Description Ingestion | **Not started.** No code anywhere parses/handles a Job Description — every module built so far only processes resume PDFs. Required by the Vision (Section 2) but untouched. |
| Embeddings | Scaffold — `encode(text)` exists, never called with real pipeline output |
| Similarity | Scaffold — `cosine_similarity()` exists, never called |
| Scorer | Initial — `compute_score()` exists with hardcoded weights, never fed real similarity/extraction data |
| Feedback | Scaffold — `generate_feedback()` exists, never called |
| Database | Initial — tables exist, nothing writes to them (e.g. `Candidate.email` has been unpopulated since the original scaffold) |
| Backend | Scaffolded, not functional — all 5 routes in `app/backend/api/routes.py` are `raise NotImplementedError` stubs; only `GET /health` actually works |
| Frontend | Scaffold — Streamlit UI renders upload widgets and a "Rank" button, but the handler just shows `"Ranking pipeline not implemented yet"`; no `src/` imports, no API calls |
| Export | **Not started.** No module exists despite being the final step in the Section 4 architecture diagram. |

**Honest summary**: resume ingestion (parse → preprocess → detect sections → extract contact info) is solid and tested. Everything after that — richer resume extraction, Job Description handling, embeddings, similarity, scoring, feedback, persistence, the actual API, the actual frontend, and export — is either a disconnected stub or doesn't exist yet. No end-to-end user flow is currently possible.
------------------------------------------------------------------------

# 13. Testing Status

Current

✅ Parser tests passing

✅ Scorer tests passing

✅ Preprocessor tests passing

✅ Section detector tests passing

✅ Contact extractor tests passing

✅ Pipeline orchestration tests passing (real generated PDF, end-to-end)

Current Result

51 / 51 tests passing

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

## Session 5 (ChatGPT)

### Achievements

- Introduced `StructuredResume` domain model.
- Refactored project structure to use one domain model per file.
- Added `parsed_resume.py`.
- Added `structured_resume.py`.
- Added package exports through `src.models`.
- Designed the preprocessing contract.
- Implemented the first production preprocessing pipeline.
- Added safe text normalization.
- Preserved immutable metadata.
- Added preprocessing unit tests.
- Verified all preprocessing tests pass.

### Lessons

- Domain models should represent stages of the pipeline rather than accumulate unrelated responsibilities.
- Stable contracts are more valuable than early feature implementation.
- Small, incremental pull requests are easier to review and maintain than large feature dumps.
- Production preprocessing should initially perform only safe, non-destructive normalization.

------------------------------------------------------------------------

## Session 6 (Claude, feature/section-detection)

### Achievements

- Reviewed Session 5's write-up against the actual repo before starting (ran the test suite, diffed the deleted `resume_models.py` against its replacements) — everything Session 5 claimed checked out.
- Designed and implemented resume section detection via a plan-mode pass: explored the codebase (confirmed no NLP dependency exists and no section logic existed anywhere), then a design pass that produced the exact-match heuristic and file layout below.
- Added `Section`/`SectionType` (the codebase's first Enum) and `SectionedResume` domain models, kept separate from `StructuredResume` per the existing "One Domain Model Per Processing Stage" decision, deliberately overriding the more casual "Extend StructuredResume" TODO wording from Session 5.
- Implemented `detect_sections()` as a pure-stdlib, exact-match heuristic (no substring matching) against a curated heading-keyword table, with a caught and fixed bug during implementation: the first draft mislabeled a no-heading-found document as `HEADER` instead of `OTHER` (the buffer's type defaulted to `HEADER` for "content before the first heading" and was never corrected when no heading ever appeared) — fixed by tracking whether any heading matched at all and relabeling the trailing buffer to `OTHER` before the final flush.
- Added 15 unit tests (30/30 total passing) and manually verified against a realistic multi-section resume string.
- Cross-reviewed the design with ChatGPT, which surfaced a real gap: an unrecognized heading-like line (e.g. "Awards") between two recognized sections was silently absorbed into the preceding section's content instead of being isolated — verified this directly by running the code (not just reading it), confirming the gap was real. Considered and rejected a generic "line looks like a heading" heuristic (isolated-by-blank-line, short, no punctuation) after hand-tracing it against a common resume layout (a heading followed by a blank line, then its first bullet, e.g. "Experience" / blank / "Team Lead") and finding it would misclassify a short job-title line as a new section — a regression, not a fix. Instead extended the existing curated `ALIASES` table with an `OTHER` vocabulary (Awards, Publications, Languages, Volunteer Work, Interests, References, Activities, Leadership, Affiliations, Honors), reusing the same trusted exact-match mechanism already validated for EXPERIENCE/EDUCATION/etc. rather than introducing new false-positive surface. 32/32 tests passing after the fix.

### Lessons

- Tracing an algorithm by hand against its own stated edge cases (here: "zero headings found") before running tests is what caught the HEADER/OTHER mislabeling bug — it would have passed every test that didn't specifically target the no-heading case.
- A TODO written in one session ("Extend StructuredResume") can conflict with an already-Accepted design decision from an earlier session ("One Domain Model Per Processing Stage") — when they conflict, the accepted architectural principle should win, and the deviation should be flagged explicitly rather than silently followed or silently ignored.
- A second reviewer (ChatGPT) asking "does X actually happen?" is only useful if the answer comes from running the code, not from re-reading it — the fix that seemed obvious in the abstract (generic heading detection) would have been a net regression; the safe fix reused an already-validated mechanism instead of inventing a new heuristic.

------------------------------------------------------------------------

## Contact Info Extraction (Session 7, Claude)

### Achievements

- Added `ContactInfo` domain model and a new `src/extraction/` package (`contact_extractor.py`), the first pipeline stage split out from `src/preprocess/` — extraction is a distinct concern from cleaning/section-splitting and is expected to grow, so it gets its own package now rather than a mid-project split later.
- Deliberately kept `ContactInfo` standalone rather than introducing an `ExtractedResume` aggregate with placeholder education/experience/skills fields — see the new "Extraction fields introduced only as they're implemented" design decision (Section 11), directly reapplying the Session 3 lesson about unused fields.
- User explicitly decided stdlib `re` over adding the `phonenumbers` dependency for phone parsing — documented as a new design decision with the accepted trade-off (non-NANP formats not recognized).
- `extract_contact_info(SectionedResume) -> ContactInfo` reads only the HEADER section, never raises (no HEADER → both fields `None`), and takes the first (leftmost) regex match when multiple emails/phones are present.
- Added 14 unit tests (46/46 total passing) and manually verified end-to-end (`StructuredResume` → `detect_sections` → `extract_contact_info`) against the same realistic resume string used to verify section detection.

### Lessons

- Caught my own mistake before it shipped: called `ExitPlanMode` with the previous (already-implemented) plan's text pasted in by accident instead of the new plan. The plan file on disk was correct; the tool-call content wasn't. Flagged it to the user immediately rather than letting the mismatch stand.
- A new pipeline stage (Extraction) getting its own `src/` package from day one, rather than being bolted onto `src/preprocess/` and split out later, avoids a mid-project reorganization once it grows beyond one function.
- `src/database/models.py` already has an unpopulated `Candidate.email` column from the original scaffold — a reminder that pre-existing schema doesn't imply pre-existing logic; it stayed untouched since wiring persistence is a separate concern from this milestone.

------------------------------------------------------------------------

## Pipeline Orchestration (Session 8, Claude)

### Achievements

- Explored `app/backend/` for the first time this project's session history: found every route in `app/backend/api/routes.py` is a stub (`raise NotImplementedError`), no DB-session FastAPI dependency exists (`src/database/db.py`'s `get_session()` is a plain factory, not a `Depends`-compatible generator), and there are zero API tests (no `TestClient` usage anywhere).
- Given that, explicitly narrowed scope with the user before planning: a pure orchestration function only, not wiring into FastAPI — bundling API-layer work (DB session pattern, HTTP error mapping, first-ever API tests) into the same pass would have violated the project's own "small PRs over feature dumps" lesson.
- Added `src/pipeline.py`: `PipelineResult` (bundles `SectionedResume` + `ContactInfo`) and `process_resume(pdf_path) -> PipelineResult`, chaining `extract_text` → `preprocess` → `detect_sections` → `extract_contact_info`. No new error handling added — `PDFParseError` already propagates correctly from the parser stage; every later stage already guarantees it never raises.
- `PipelineResult` deliberately kept out of `src/models/` — unlike the per-stage domain models, nothing downstream consumes it as input; documented as a terminal caller-convenience bundle, not a pipeline-stage model.
- Added 5 unit tests (51/51 total passing), reusing `test_parser.py`'s PyMuPDF-generated-PDF-at-test-time pattern to test the real chain end-to-end (not just synthetic pre-built dataclasses).
- Manually ran `process_resume()` against the actual resume in `samples/Manish_ResumeDA01.pdf` (not just a synthetic string) — correctly extracted email, phone, and six ordered sections (Header, Education, Work Experience, Certifications, Projects, Skills) from a real PDF.

### Lessons

- Made the identical `ExitPlanMode` copy-paste mistake again (pasted the stale section-detection plan instead of the new one) — caught and flagged immediately both times, but worth noting as a recurring failure mode to watch for, not a one-off.
- Reading the actual state of a previously-unexamined area (`app/backend/`) before planning changed the recommended scope substantially — "wire the pipeline" sounded like one small task until the backend turned out to have no DB-session pattern, no error-to-HTTP mapping, and no test infrastructure at all; asking the user to explicitly scope down was better than silently assuming the narrow interpretation.
- Testing against a real sample PDF (not just synthetic constructed text) caught nothing new this time, but is worth keeping as a standard verification step — synthetic tests only prove the code does what the test says, not what a real messy document produces.

------------------------------------------------------------------------

# 16. Current TODO

## High Priority

- Wire `src/pipeline.py`'s `process_resume()` into the FastAPI `/upload-resume` route (needs: a real DB-session `Depends` pattern, HTTP error mapping for `PDFParseError`, and the project's first API tests via `TestClient` — all still nonexistent)
- Design education/experience entry extraction (dates, companies, degrees) as the next extraction slice
- Extend `ALIASES` for further common headings not yet recognized (e.g. Certifications synonyms, Summary synonyms)
- **Not yet scheduled but large and unstarted**: Job Description ingestion (no parser/model/route exists — the Vision requires it, nothing built so far touches it) and an Export module (final architecture step, doesn't exist). Neither has a milestone plan yet; either could reasonably become "the next session" instead of the two options below.

## Medium

- Non-NANP phone format support (revisit stdlib-vs-`phonenumbers` decision if needed)
- Additional Unicode normalization

## Low

- FAISS
- PostgreSQL
- MLflow
------------------------------------------------------------------------

# 17. Next Session

Goal

Three live options, not yet narrowed down — confirm with the user which one before planning: (1) wire `process_resume()` into the FastAPI `/upload-resume` route, (2) begin the next resume-extraction slice (education/experience entries), or (3) start Job Description ingestion, which nothing built so far touches at all and which the Vision (Section 2) requires. Pick one, don't bundle multiple (see Session 8's scope-narrowing decision and its lesson about reading unexamined areas before committing to scope).

Tasks (if API wiring)

- Design a `Depends`-compatible DB session generator (none exists yet; `get_session()` is a plain factory).
- Decide HTTP error mapping for `PDFParseError` (e.g. 422 vs 400).
- Add the project's first API tests via `TestClient`.
- Decide what `/upload-resume` persists (which `PipelineResult` fields map to which `Resume`/`Candidate` columns).

Tasks (if extraction slice)

- Design a representation for extracted entries within EDUCATION/EXPERIENCE sections (still no NLP dependency unless a concrete need forces one).
- Extend `ALIASES` for common headings not yet recognized.
- Add comprehensive unit tests.

Tasks (if Job Description ingestion — least explored option, start with research)

- Explore first: no one has looked at whether a JD is expected as a PDF (reusing `extract_text`), pasted text, or something else — the Vision (Section 2) just says "accepts a Job Description," undefined further. Check `src/database/models.py`'s `Job` table (`id`, `title`, `description`, `created_at`) for hints about the intended shape.
- Decide whether JD parsing reuses existing parser/preprocess stages or needs its own, given a JD is structurally very different from a resume (no sections like Experience/Education in the same sense).
- Add comprehensive unit tests.

Do not begin embeddings, semantic search, scoring, or LLM feedback until resume preprocessing is fully complete.
------------------------------------------------------------------------

# 18. Known Technical Debt

-   Parser catches generic Exception for the fitz.open/get_text block
-   No API schemas yet
-   No relationships in SQLAlchemy models
-   Preprocessing currently performs only safe normalization; section
    detection is a separate stage/function (`detect_sections()`), not
    merged into `preprocess()` — both are chained together in
    `src/pipeline.py`'s `process_resume()` instead.
-   Section detection uses a fixed, curated heading-keyword list
    (`ALIASES` in `section_detector.py`), including a curated OTHER
    vocabulary (Awards, Publications, Languages, Volunteer Work,
    Interests, References, Activities, Leadership, Affiliations,
    Honors) so these get their own OTHER-typed section rather than
    bleeding into whichever section preceded them. A heading outside
    this curated vocabulary (e.g. an idiosyncratic custom heading) is
    still treated as content of whichever section is currently open —
    deliberately not "fixed" further with a generic heading-detection
    heuristic, since plain extracted text carries no formatting cues
    (bold, font size) to reliably distinguish a novel heading from a
    short content line like a job title.
-   `src/pipeline.py`'s `process_resume()` chains parse → preprocess →
    detect sections → extract contact info, but is not yet called
    from anywhere — `app/backend/api/routes.py`'s `/upload-resume` is
    still a stub (`raise NotImplementedError`), and there is no
    FastAPI DB-session dependency pattern to persist a `PipelineResult`
    even once it's called.
-   Contact extraction's phone regex covers common NANP formats only
    (with/without `+1`, parens/dashes/dots/spaces); non-NANP
    international formats and extensions (`x123`) are not recognized.
    If multiple emails/phones appear in the header, only the first
    (leftmost) match is kept — no disambiguation logic exists.
-   No Job Description ingestion exists at all — no parser, no model,
    no route. Every module built through Session 8 only handles
    resume PDFs. This is a large, entirely unstarted piece of the
    Vision (Section 2), not a small gap.
-   No Export module exists, despite being the final step in the
    Section 4 architecture diagram.
-   Embeddings, Similarity, Scorer, Feedback, Database, Backend (past
    `/health`), and Frontend are all scaffold/stub code that has never
    been exercised with real pipeline output — see Section 12's
    "Honest summary" for the full picture. There is currently no
    end-to-end path a user could actually run.
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
-   Why each pipeline stage owns its own domain model
-   Why preprocessing returns StructuredResume instead of modifying ParsedResume
-   Why immutable value objects improve maintainability
-   Why section detection uses exact-match against curated keywords instead of substring matching or an NLP library
-   Why a document with no recognized headings falls back to OTHER, not HEADER, and why that distinction matters
-   Why section detection produces a new SectionedResume model instead of extending StructuredResume
-   Why ContactInfo is standalone instead of bundled into an ExtractedResume aggregate today
-   Why phone extraction uses a stdlib regex instead of a phone-parsing library, and what the accepted trade-off is
-   Why contact extraction only reads the HEADER section instead of scanning the whole document
-   Why `PipelineResult` lives outside `src/models/` unlike the other domain models
-   Why wiring the API route was deliberately deferred instead of bundled into this milestone

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

Completed (Session 5)

- Added StructuredResume domain model.
- Introduced preprocessing pipeline.
- Added safe text normalization.
- Preserved immutable metadata.
- Added preprocessing unit tests.
- Verified all tests passing.
- Established preprocessing contract.
- Refactored domain models into one file per model.

Completed (Session 6)

- Verified Session 5's claims against the repo before starting new work.
- Added `Section`/`SectionType`/`SectionedResume` domain models.
- Implemented `detect_sections()` heuristic section detection.
- Found and fixed a HEADER-vs-OTHER mislabeling bug during hand-tracing, before it could hide behind a passing test suite.
- Cross-reviewed with ChatGPT; verified and fixed a real gap it surfaced (unrecognized secondary headings like "Awards" bleeding into the preceding section) by extending the curated ALIASES vocabulary rather than adding a risky generic heuristic.
- Added 17 unit tests (net, after replacing one outdated test) — 32/32 total passing — and verified manually against a realistic resume.
- PROJECT_BIBLE synced with repository.

Completed (Session 7)

- Added `ContactInfo` domain model and new `src/extraction/` package (`contact_extractor.py`).
- Decided (with user) stdlib regex over adding the `phonenumbers` dependency; documented as a design decision.
- Decided against an `ExtractedResume` aggregate this pass, reapplying the Session 3 unused-fields lesson.
- Implemented `extract_contact_info()`: HEADER-scoped, never raises, first-match-wins.
- Added 14 unit tests — 46/46 total passing — and verified manually end-to-end (parse → structure → sections → contact info).
- PROJECT_BIBLE synced with repository (architecture diagram, folder structure, module responsibilities, domain models, design decisions, TODO, tech debt, session log).

Completed (Session 8)

- Explored `app/backend/` for the first time; found all routes stubbed, no DB-session dependency pattern, no API tests — narrowed scope with the user to a pure orchestration function, deferring API wiring.
- Added `src/pipeline.py`: `PipelineResult` + `process_resume()`, chaining all four existing stages.
- Added 5 unit tests (real PyMuPDF-generated PDF, not synthetic dataclasses) — 51/51 total passing.
- Manually verified against the actual `samples/Manish_ResumeDA01.pdf` resume, not just test fixtures — correct email, phone, and six ordered sections.
- PROJECT_BIBLE synced with repository (version, module status, testing status, TODO/next session split by option, tech debt, session log, interview talking points).
