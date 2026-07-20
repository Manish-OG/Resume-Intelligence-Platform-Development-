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

**Current Version:** v0.13.0

**Current Status:** Active Development

Current Milestone:
Resume Intelligence Engine (In Progress)

Latest Completed Milestone:
Skill matching — `/rank` now exposes a second real signal (`skill_score`) alongside `semantic_score`; `Scorer`'s weighted blend still deferred (experience/education remain unreal)

**Overall Progress:** ~71%

Caveat on that number (updated Session 16, first written Session 8):
~71% reflects real, composed, end-to-end functionality: both ingestion
sides persist real rows, and `POST /rank` genuinely ranks every
persisted resume against a job using two real signals — semantic
similarity and skill overlap — both verified against real data
(Section 14). It does **not** mean 71% of the working product
described in the Vision below exists: ranking is still missing
experience/education scoring, `Scorer`'s weighted blend stays unwired,
nothing is persisted to `Score`, `/results`/`/download` remain stubs,
feedback generation doesn't exist, and the actual frontend is still
scaffold. See Section 12 (Module Status) and Section 18 (Known
Technical Debt) for the honest breakdown.

Git Note (updated Session 16, first written Session 8): all work
through Session 14 (Embeddings module hardening) was committed and
pushed — PR #4, `a54d584`. That is still the last commit on `main` —
**both Session 15 (`POST /rank`) and Session 16 (skill matching) are
uncommitted working-tree state as of this writing**, sitting together
in one working tree (two milestones' worth of un-pushed work, not
one). Verified directly via `git log`/`git status`, not assumed from
a prior note. If a new session finds this note still true, confirm
with the user whether to commit before doing further work — recurring
every session because commits happen at the user's discretion, not
automatically.

(The previously-noted stray `extract` file was resolved and deleted
with the user's explicit permission in an earlier session; no longer
present.)

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

Parser - Extract raw PDF text - Return ParsedResume - No cleaning (also reused as-is for Job Description PDFs — see Section 11)

Preprocess - Cleaning - Normalization - Section detection

Extraction - Pull structured facts out of one document's detected sections (contact info, name, education/experience entries, and skills list now — all single-document, never compares two documents)

Embeddings - Generate vectors only

Similarity - Compute similarity

Scorer - Weighted scoring; also owns document-to-document comparison (e.g. `compute_skill_score()` comparing a resume's skills against a JD) — Extraction never compares two documents, Scorer does

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

---

## CandidateName

Purpose

Candidate name extracted from a `SectionedResume`'s HEADER section.

Fields

- name (str | None)

Produces

Name extraction (`src/extraction/name_extractor.py`)

Reason

Kept as its own model rather than added as a third field on `ContactInfo` — a name is identity information, not a contact channel, and folding it into `ContactInfo` would have stretched that model's meaning and risked a future breaking rename. Mirrors the same "each extracted concept gets its own narrow model" precedent `ContactInfo` itself established in Session 7.

---

## ResumeEntry

Purpose

One structural entry within an EDUCATION or EXPERIENCE section, produced by date-anchored segmentation.

Fields

- title (str | None)
- dates (str | None)
- details (str)

Produces

Entry extraction (`src/extraction/entry_extractor.py`)

Reason

Deliberately kept to structural fields only (title/dates/details) — not decomposed into semantic fields (degree, GPA, location, company, role). No reliable text-only delimiter exists to split those apart from plain extracted text; attempting it would risk confidently-wrong structured data. See Section 11's design decision for the full reasoning, including the real hand-traced evidence this was tested against.

`title` documents an implementation rule (the nearest non-blank line preceding a recognized date line), not a claim that every resume places the institution/company there — see Section 11.

---

## ResumeSkills

Purpose

Flat list of skills extracted from a resume's SKILLS section.

Fields

- skills (tuple[str, ...])

Produces

Skills extraction (`src/extraction/skills_extractor.py`)

Reason

A single field, unlike `ResumeEntry`'s three — still wrapped in a dataclass rather than passed around as a bare tuple, for consistency with this project's established "every extraction concept returns a typed domain object" convention (`CandidateName` set this precedent for a single-field case). Case-insensitively deduplicated at extraction time so a skill listed twice doesn't distort downstream matching ratios (see `compute_skill_score()`, `src/scorer/skill_matcher.py`).

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

### DB session: generator-based `get_db()` replaces `get_session()`

Reason: `get_session()` was a plain factory (`return SessionLocal()`)
with no cleanup and no way to plug into FastAPI's `Depends()`. Replaced
with the standard FastAPI generator-dependency idiom (`yield` inside a
`try`/`finally` that closes the session). Zero callers existed for the
old function, so this was a clean swap, not a breaking change.

Status: Accepted.

------------------------------------------------------------------------

### `PDFParseError` maps to HTTP 422, not 400

Reason: a corrupt, scanned, or password-protected PDF is a
syntactically valid multipart upload — the *request* is well-formed;
the uploaded document's *content* is what's unprocessable. FastAPI
already uses 422 for its own "well-formed request, semantically bad
payload" validation errors, so this reuses an existing convention
rather than introducing a new one (400 was considered and rejected).

Status: Accepted.

------------------------------------------------------------------------

### `/upload-resume` persists to the `Upload` table only (Resume/Candidate deferred)

Reason: a literal "persist the full `PipelineResult`" doesn't map onto
today's schema. `Candidate.name` is `NOT NULL` but no code anywhere
extracts a name; `Resume.raw_text` is `NOT NULL` but `PipelineResult`
doesn't carry a flat text field. Inventing a placeholder name (e.g.
filename or `"Unknown"`) would repeat the unused/fake-field mistake
already caught and fixed on `ParsedResume` in Session 3. Instead, this
milestone persists only what the pipeline actually and cleanly
produces (`Upload.file_name`/`file_path`/`uploaded_at`) and returns
`sections` + `contact` directly in the JSON response. `Resume`/
`Candidate`/`Score` population is explicitly deferred to the next
extraction slice (name extraction), not silently faked.

Cross-reviewed with ChatGPT, which independently reached the same
conclusion and additionally recommended never writing a *partial*
`Resume` row — persist `Upload` only, or `Upload` + a fully valid
`Resume`, never something in between.

Status: Accepted for this milestone; revisit once name extraction exists.

------------------------------------------------------------------------

### `Resume.raw_text` means `ParsedResume.raw_text`, not `StructuredResume.normalized_text`

Reason: this needed pinning down before any code touches it, since the
two are not equivalent. `ParsedResume.raw_text` is the canonical,
unmodified parser output; `StructuredResume.normalized_text` is a
derived artifact. Persisting the canonical form lets normalization
logic evolve later without needing to touch (or re-derive) stored
data. Raised and settled during ChatGPT cross-review; not yet acted on
in code since no route persists `Resume` rows this milestone — recorded
here so Milestone B (name extraction + `Resume`/`Candidate`
persistence) doesn't have to re-litigate it.

Status: Accepted; to be applied when `Resume` persistence is implemented.

------------------------------------------------------------------------

### Name extraction: own `CandidateName` model, first-HEADER-line heuristic

Reason: considered adding `name: str | None` directly to `ContactInfo`
instead (one function call, one pass over HEADER content) but rejected
it — a name isn't a contact channel, and stretching `ContactInfo`'s
meaning risks a future breaking rename across `PipelineResult`, tests,
and the API response. A separate `CandidateName` model + a separate
`extract_name()` in a new `name_extractor.py` mirrors the exact
`ContactInfo`/`contact_extractor.py` precedent instead.

Extraction heuristic: the first non-empty line of the HEADER section
is the name, unless it matches the existing email/phone regexes
(reused from `contact_extractor.py`), in which case `None` is
returned rather than misreporting a contact line as a name. No NLP
dependency, consistent with every other extraction/detection decision
in this project. Verified against the real sample resume
(`samples/Manish_ResumeDA01.pdf`) as well as synthetic fixtures.

Accepted, documented gap: a HEADER that opens with something other
than a name (address, objective statement, photo caption) will
misextract. No real resume seen so far exhibits this, so no guess-work
heuristic (e.g. a word-count cap) was added to guard against it —
consistent with the project's habit of not adding untuned checks for
unobserved failure modes.

Status: Accepted.

------------------------------------------------------------------------

### `PipelineResult` gains `raw_text`, excluded from the API response via a new `UploadResumeResponse` schema

Reason: persisting `Resume.raw_text` (= `ParsedResume.raw_text`, per the
decision above) requires reaching it from the route. Two options were
weighed: (a) add `raw_text: str` to `PipelineResult`, one parse per
request; (d) have the route call `extract_text()` a second time,
keeping `PipelineResult` unchanged. Chose (a) — a second full parse
per request, even at ~8ms, reads as an oversight to a future reviewer,
and the real objection to (a) (the full raw resume text leaking into
the HTTP response) is better solved directly than worked around.

Solved directly by introducing `app/backend/api/schemas.py`'s
`UploadResumeResponse` — a route-local API schema (not a domain
model) that selects `sections`/`contact`/`name` (plus the new
`resume_id`/`candidate_id`) and omits `raw_text`. This is the first
concrete use of a schema layer, addressing part of the long-standing
"No API schemas yet" tech debt item — introduced now because a real,
current need exists (hide a persistence-only field from the response,
expose real DB-generated IDs), not speculatively.

Status: Accepted.

------------------------------------------------------------------------

### `Candidate` rows are not deduplicated

Reason: re-uploading the same person's resume creates a new
`Candidate` row every time; no find-or-create-by-email logic exists.
Considered and rejected for now: real dedup requires deciding how to
handle a `None` email (unmatchable), a candidate with two different
emails across resumes, and false-positive matches — real business
logic with no concrete requirement driving it yet. Consistent with
this project's repeated pattern (OCR, `phonenumbers`, generic heading
detection) of not building speculative logic ahead of an actual need.

Status: Accepted for this milestone; revisit once a concrete
requirement needs "one candidate, many resumes" semantics.

------------------------------------------------------------------------

### `Resume`/`Candidate` persistence is skipped when name extraction returns `None`

Reason: `Candidate.name` is `NOT NULL`. Rejected: a placeholder name
(repeats the fake-field anti-pattern caught in Session 3 and reapplied
several times since). Rejected: failing the request — a missing name
is a heuristic gap, not a parse failure; sections and contact still
extracted correctly, so a 4xx/5xx would misrepresent what actually
went wrong. Chosen: when `CandidateName.name is None`, skip `Resume`/
`Candidate` creation entirely, persist `Upload` only (identical to the
"no name" case's existing behavior), and still return 200 with the
full `sections`/`contact`/`name` — `resume_id`/`candidate_id` are
`None` in that response.

Status: Accepted.

------------------------------------------------------------------------

### Education/Experience entry extraction: date-anchored segmentation, structural fields only

Reason: before designing, hand-traced candidate heuristics against the
real sample resume's actual EDUCATION and EXPERIENCE content (not
synthetic fixtures) — the same practice Session 6 used for section
detection. Findings that shaped the design:

- A blank-line-separated-paragraphs heuristic (the obvious first
  idea) finds zero entry boundaries in the real EDUCATION section —
  its three entries run with no blank lines between them.
- A date-line-anchored heuristic correctly recovers all three
  EDUCATION entries, using `re.fullmatch` (not `.search()`) so a
  bullet merely *mentioning* a year can't trigger a false boundary.
- The same real resume's EXPERIENCE section contains **zero**
  standalone date lines at all — the chosen heuristic must produce an
  honest single-entry fallback here, not force incorrect structure.

Chosen design: for each date line found (full-line match against a
month/year/range pattern), the nearest preceding non-blank line
becomes that entry's `title` — documented explicitly as "the line the
extractor found," not "the institution/company is always the
preceding line" (refined after ChatGPT cross-review, which correctly
flagged the original wording as overclaiming a universal resume
property rather than describing an implementation rule). Everything
else in the entry stays in `details` as raw, undecomposed text — no
attempt to further split degree/GPA/location apart, since no reliable
delimiter exists for that in plain extracted text (also confirmed
during cross-review). If no section line fullmatches a date, the
whole section becomes one entry with `title=None, dates=None` rather
than guessing.

Known limitation (added per ChatGPT cross-review): the extractor
assumes one date anchor per logical entry. An entry containing more
than one standalone date-shaped line (e.g. a sub-timeline within a
single job) will be over-segmented into multiple entries. Not
observed in the one real resume available, but a real, plausible
resume layout — logged here rather than silently risked.

Explicitly out of scope this milestone: DB persistence. No
`Education`/`Experience` tables exist in the schema; adding them is a
separate schema-design decision, deferred the same way `ContactInfo`
and `CandidateName` extraction each preceded their own persistence
milestone.

Cross-reviewed with ChatGPT to convergence; both reviewers agreed the
core principle at stake — "never fabricate structure the source text
does not reliably contain" — mattered more than extracting one
additional field.

Status: Accepted.

------------------------------------------------------------------------

### Job Description ingestion: PDF upload, not pasted text

Reason: before designing, this needed actual research (flagged as the
least-explored TODO item) rather than an assumption. Two independent
pieces of existing scaffold evidence agree: `app/frontend/streamlit_app.py`
already has `st.file_uploader("Job description (PDF)", type="pdf")`,
and the `/upload-job` route stub's signature already took
`file: UploadFile`. The `Job.description: str` column (no `file_path`)
initially looked like it might hint at pasted text, but isn't a real
contradiction — it mirrors exactly how `Resume.raw_text` already
stores parsed text from an uploaded resume PDF, with the file path
tracked separately in the already-generic `Upload` table.

Status: Accepted.

------------------------------------------------------------------------

### JD ingestion reuses `extract_text()`/`clean_text()`, not `detect_sections()`

Reason: checked by reading the actual code, not assumed. `extract_text()`
(PDF → raw text) and `clean_text()` (the inner, fully generic text-hygiene
function inside `preprocessor.py` — line endings, tabs, trailing
whitespace, blank-line collapsing, boundary trim) have nothing
resume-specific in them and are safe to reuse directly.
`detect_sections()` is not: its matching logic
(`section_detector.py`) does an exact match, after stripping a
trailing colon, against a curated `ALIASES` table that includes bare
`"education"` and `"experience"`. A JD's own Requirements block
commonly uses short subheadings like:
```
Requirements
Education
Bachelor's degree in Computer Science or related field
Experience
3+ years of software development experience
```
A line that's literally `"Education"` or `"Experience"` would
exact-match and get mislabeled as a resume-style section on a
document that isn't a resume — a concrete, traceable false-positive,
not a hypothetical one. Verified end-to-end with exactly this content
(manual live-server test): the JD's "Education"/"Experience"
subheadings are stored as plain text, untouched, in `Job.description`.

A small orchestration helper, `parse_job_description()`
(`src/job_pipeline.py`), wraps `extract_text()` + `clean_text()` —
added after ChatGPT cross-review suggested it, so the route stays a
thin HTTP-to-domain translator (calling two individual transformation
functions directly from the route would have blurred that boundary)
and stays structurally symmetrical with `process_resume()`.

Status: Accepted.

------------------------------------------------------------------------

### Job title is a required user-provided field, not extracted

Reason: every extraction heuristic accepted so far in this project
(contact info, name, education/experience entries) was verified
against a real resume before shipping. No real sample Job Description
exists anywhere in this repo — unlike every prior extraction
milestone, there's no data to hand-trace a title-extraction heuristic
against. Guessing without evidence would repeat the exact mistake this
project has avoided at every previous decision point. `POST
/upload-job` requires `title: str` as a form field alongside the file
upload; FastAPI 422s automatically if it's missing.

Status: Accepted; revisit automatic extraction only once a real corpus
of JDs exists to validate a heuristic against.

------------------------------------------------------------------------

### No `ParsedJobDescription` domain model introduced

Reason: `extract_text()` + `clean_text()` run inline inside
`parse_job_description()`, returning a plain `str`, not a new domain
model. Considered a thin wrapper model (mirroring `ParsedResume`'s
shape) for naming cleanliness, but rejected for now — there's no
second consumer of a "parsed JD" concept yet (unlike `ContactInfo`/
`CandidateName`/`ResumeEntry`, each introduced only once something
actually produced *and* consumed them). Cross-reviewed with ChatGPT,
which raised a fair framing question — is this project modeling
*documents* or *pipelines*? — and, applying the project's own
established pattern (only introduce a model once multiple consumers
exist), agreed with not introducing one yet. Recorded here as a
conscious decision, not an omission.

Status: Accepted for this milestone; revisit if a second JD-processing
stage (e.g. requirement/skill extraction) is added and needs a stable
input contract.

------------------------------------------------------------------------

### Embeddings: build and verify only, defer persistence/wiring to `/rank`

Reason: no DB column exists to store a vector on `Resume`/`Job` (a
schema decision on par with every other persistence decision made
this project, none made casually), and the only thing that would ever
consume a stored embedding — `/rank` — doesn't exist yet. Computing
embeddings during `/upload-resume`/`/upload-job` now would mean
generating and discarding a vector on every upload, adding startup
latency and a new failure mode for zero user-visible benefit. Cross-
reviewed with ChatGPT, which independently reached the same
conclusion and added a concrete list of decisions that belong
together at the `/rank` milestone rather than split across sessions:
compute-on-demand vs. cache, whether to persist vectors, cache
invalidation if the model ever changes, and batch processing.

Status: Accepted.

------------------------------------------------------------------------

### Resume embedding text: `prepare_resume_embedding_text()` lives in `src/pipeline.py`, not in `src/embeddings/`

Reason: the Embeddings module's contract (`encode(text: str) -> vector`)
should stay completely domain-agnostic — it should not know what a
resume, a `SectionedResume`, or a `SectionType.HEADER` is. This
directly matches Section 7's pre-existing module responsibility,
written before this milestone: "Embeddings — Generate vectors only."
My first framing of this decision (Option A: embed raw_text, vs.
Option B: have Embeddings itself filter out HEADER) missed that this
was the real question — ChatGPT reframed it correctly: the resume-
specific decision of *what text represents a resume* belongs to
whichever module already understands resume structure, not to the
encoder. Implemented as `prepare_resume_embedding_text(SectionedResume) -> str`
in `src/pipeline.py` (sibling to `process_resume()`, not called by
it — it's for a future consumer like `/rank`, not part of ingestion).
It excludes the HEADER section (contact info carries no semantic
signal for matching against a JD) and joins the rest in document
order. Verified against the real sample resume: the email address is
confirmed absent from the embedded text, and a JD matching the
resume's actual domain (electronics/embedded systems) scored
meaningfully higher via cosine similarity than an unrelated JD
(pastry chef) — 0.169 vs. 0.019.

Status: Accepted.

------------------------------------------------------------------------

### Test strategy: `slow`-marked real-model tests, excluded from the default `pytest` run

Reason: the project's test suite had been ~1.2 sec for 85 tests with
zero network/model dependencies; a real, unmocked embedding test costs
roughly 15 sec (importing `sentence_transformers`/`torch`) plus ~6 sec
(loading model weights into memory) the first time it runs in a
process. Added `pytest.ini` registering a `slow` marker with
`addopts = -m "not slow"`, so the default `pytest` invocation everyone
has been running all project stays fast, and the real-model tests run
on demand via `pytest -m slow`.

A first attempt at a *fast, mocked* orchestration test file
(`test_encoder.py`, using `unittest.mock`/`monkeypatch` to fake
`SentenceTransformer`) was written, then **deleted after measuring
that it didn't work**: `encoder.py` does `from sentence_transformers
import SentenceTransformer` at module level, so merely importing
`src.embeddings.encoder` — required to monkeypatch anything inside
it — pays the full ~15s import cost regardless of mocking. Confirmed
by re-running the suite and watching the time stay at ~13-20s despite
the mocks; the fix wasn't a better mock, it was recognizing the
premise ("mocking makes this fast") was wrong and consolidating the
orchestration tests (e.g. "does `get_model()` cache across calls?")
into the same `slow`-marked, real-model file instead — since the
import cost is paid regardless, testing the real behavior there is
strictly more meaningful than a mock would have been anyway.

A separate, real bug also had to be fixed in the process: the first
version of the `slow`-marked integration test file imported `encode`
at module level too, which meant pytest paid the full import cost
during test *collection* even though the tests themselves were
deselected by the marker — 3 "deselected" tests still cost ~20s.
Fixed by moving `from src.embeddings.encoder import encode` inside
each test function body, so the import only executes when a test
actually runs.

Status: Accepted. Verified: default `pytest` is 95 tests in ~1.6 sec;
`pytest -m slow` is 4 tests in ~17 sec.

------------------------------------------------------------------------

### `/rank` bypasses `Scorer` and does not persist `Score` rows

Reason: `ScoreComponents` expects four signals (`semantic`, `skills`,
`experience`, `education`); only `semantic` is computable today —
nothing extracts a skills list to match against a JD, and nothing
scores experience/education relevance. Feeding `compute_score()` today
would mean fabricating three of four inputs (e.g. `0.0`), the exact
placeholder-data anti-pattern rejected at every prior decision point
in this project (unused `ParsedResume.status`/`.errors` removed in
Session 3; `Candidate.name` never faked when extraction fails;
`Job.title` required as real user input specifically because no
heuristic could be validated). Running one real signal through
weighting machinery built for four would just rescale the same number
while implying sophistication that doesn't exist. `/rank` ranks by raw
cosine similarity instead; `Scorer` stays unwired until skill/
experience/education scoring are real.

The `Score` table's four score columns are all `NOT NULL`, so
persisting a row today hits the identical fabrication problem at the
DB layer — same reasoning, not persisted this milestone. Considered
and rejected: making the three missing columns nullable now. Cross-
reviewed with ChatGPT, which argued this would be churn without
long-term benefit — those columns aren't optional by design, they're
incomplete because the feature isn't built yet, and the schema would
just get tightened again the moment real `Scorer` wiring lands.
Direct, accepted consequence: `/results` stays a stub too — there's
nothing persisted for it to retrieve.

Status: Accepted.

------------------------------------------------------------------------

### Embeddings computed on-demand at `/rank` time, not cached or persisted

Reason: this was explicitly deferred from the Embeddings milestone to
"whenever `/rank` gets built" — that's now. Realized as planned:
`rank_resumes_against_job()` calls `build_resume_embedding()`/
`build_job_embedding()` fresh on every `/rank` call. Reinforced by a
detail only fully visible once implementing this: ranking a *stored*
resume already requires reconstructing `SectionedResume` from
`Resume.raw_text` via `clean_text()` + `detect_sections()`, since only
the flat raw text was ever persisted (an earlier, separate decision).
Given that recomputation is already unavoidable, not caching the
embedding either is the consistent choice, not a shortcut — caching
would only eliminate one relatively cheap step while introducing real
open problems (cache invalidation if the model version ever changes,
a persistence format decision for a float vector) with no evidence
yet that `/rank` latency is a real problem worth solving.

Status: Accepted.

------------------------------------------------------------------------

### `/rank` compares a Job against every persisted `Resume`

Reason: no schema exists for applications, candidate pools, or
job-to-resume assignments — `Resume` rows aren't associated with any
particular `Job` at upload time. There is no principled way to define
a subset of resumes to rank without inventing a new business rule this
milestone doesn't need. Recorded explicitly (per ChatGPT cross-review)
so a future session doesn't wonder whether "rank everything" was
intentional or an oversight: **until an application/job-assignment
concept exists, `/rank` compares the selected `Job` against every
`Resume` stored in the system.**

Status: Accepted; revisit if/when a concept of "candidates applied to
this job" is introduced.

------------------------------------------------------------------------

### Shared `build_resume_embedding()`/`build_job_embedding()` helpers, to prevent pipeline divergence

Reason: `/rank` is the first feature with two independent code paths
that both prepare resume/JD text (upload-time preprocessing, and
rank-time re-derivation from stored `raw_text`). ChatGPT cross-review
flagged this as the biggest new risk in this milestone — not
embeddings or similarity, but "pipeline divergence": if the two paths
ever prepared text differently, semantic comparisons would become
silently inconsistent depending on where a resume entered the system.
Mitigated by making `build_resume_embedding()` (`src/pipeline.py`) and
`build_job_embedding()` (`src/job_pipeline.py`) the single shared path
each side goes through — `src/ranking.py` calls these rather than
re-implementing `clean_text` → `detect_sections` →
`prepare_resume_embedding_text` → `encode` itself. Kept in
`pipeline.py`/`job_pipeline.py`, not in `src/embeddings/`, for the
same domain-agnostic-encoder reasoning as `prepare_resume_embedding_text()`
(Section 11, Session 14).

Status: Accepted.

------------------------------------------------------------------------

### `sentence_transformers` import made lazy inside `get_model()`

Reason: found while implementing, not anticipated in the design brief.
Once `app/backend/api/routes.py` imports `src/ranking.py` (→
`src/pipeline.py` → `src/embeddings/encoder.py`), every API test using
the `client` fixture — including `/upload-resume`/`/upload-job` tests
that never touch `/rank` — would transitively import
`sentence_transformers`/`torch` merely by importing `app.backend.main`,
silently re-breaking the "fast by default" test suite property
established in Session 14, without any test actually calling
`encode()`. Fixed by moving `from sentence_transformers import
SentenceTransformer` inside `get_model()`'s body instead of
`encoder.py`'s module top level — importing the module is now cheap;
only an actual call to `get_model()`/`encode()` pays the real cost.
Verified: default `pytest` stayed at ~1.3-1.5 sec (102 tests) after
wiring the route in, confirmed by re-running the suite immediately
after each new import was added, not assumed. This also made mocking
`build_resume_embedding()`/`build_job_embedding()` in fast unit tests
actually work (unlike the failed mocking attempt in Session 14, where
`encoder.py`'s top-level import defeated it regardless of what was
mocked) — see Section 13.

Status: Accepted.

------------------------------------------------------------------------

### Skill matching: search the JD for the candidate's own extracted skills, not an independent JD skill list

Reason: two options were weighed. (A) a curated global skill
dictionary — rejected, since unlike the small, closed `ALIASES`
vocabulary for section headings, a "known skills" list has no natural
bound and would always be incomplete, with constant maintenance cost.
(B, chosen) search the JD's text for each of the candidate's own
extracted skills — no external vocabulary needed, since the search
terms come from what's already reliably extracted per-resume.
Cross-reviewed with ChatGPT, which agreed and specifically credited
Option B with keeping extraction (document-local) and scoring
(document-to-document comparison) as clean, separate responsibilities.

Honest limitation, documented rather than silently accepted: this
answers "what fraction of this candidate's declared skills appear in
the JD," not "what skills does the JD require that the candidate is
missing." The second question needs an independently extracted JD
skill list, which there is no real JD corpus to validate a heuristic
against (same constraint that blocked JD-title extraction in an
earlier session). Left for a future Feedback milestone, not attempted
without evidence.

`skill_score = 0.0` for a resume with no extracted skills (0/0
handled explicitly, not a `ZeroDivisionError`).

Status: Accepted.

------------------------------------------------------------------------

### Skill matching uses lookaround boundaries, not `\b` — verified empirically, not assumed

Reason: ChatGPT cross-review flagged that Python's `\b` is defined
around word characters (`[A-Za-z0-9_]`) and asked that punctuation-
heavy skills (`C++`, `C#`, `.NET`, `Node.js`, `Draw.io`) be verified
before relying on `\b` universally, rather than trusted on intuition.
Verified directly by running both approaches against real test cases:
```
skill      naive \b     lookaround   text
C++        False        True         'Familiar with C++ and Java'
C#         False        True         'Experience in C# and .NET'
.NET       False        True         'Experience in C# and .NET development'
Node.js    True         True         'Experience with Node.js development'
Draw.io    True         True         'Diagrams made with Draw.io'
Java       False        False        'Experience with JavaScript frameworks'
SQL        False        False        'Experience with PostgreSQL'
```
Naive `\b` silently fails on `C++`/`C#`/`.NET` — a real bug that would
have shipped if the concern had been dismissed as theoretical. Cause:
`\b` requires a word/non-word transition, and both the trailing `+` in
"C++ " and the following space are non-word characters, so no
transition exists. Fixed with lookaround assertions instead —
`(?<![A-Za-z0-9]){skill}(?![A-Za-z0-9])` — which only checks whether
the characters immediately outside the match are alphanumeric,
correctly handling all seven test cases including the two negative
controls (`Java` not matching inside `JavaScript`, `SQL` not matching
inside `PostgreSQL`).

Status: Accepted.

------------------------------------------------------------------------

### Alias/synonym matching (Git↔GitHub, SQL↔PostgreSQL) explicitly out of scope

Reason: current matching is exact token matching after normalization
(case-insensitive, boundary-matched). "Git" does not match "GitHub" in
a JD; "SQL" does not match "PostgreSQL". Technically consistent, but a
recruiter might reasonably expect otherwise. Per ChatGPT cross-review:
documented explicitly rather than solved now, since a synonym/alias
dictionary has the identical unbounded-vocabulary problem already
rejected for skill extraction itself (see the Option A/B decision
above) — building one would just relocate the same rejected approach
one level down.

Status: Accepted as a known, documented limitation; revisit only if a
concrete need forces it (echoing the project's long-standing pattern
for OCR, `phonenumbers`, generic heading detection, etc.).

------------------------------------------------------------------------

### `ALIASES` extended for "Positions of Responsibility" — a real bug found via real-data verification

Reason: manually verifying skill extraction against the real sample
resume (not just synthetic fixtures, per this project's standing
practice) surfaced a real, concrete bug: the resume's SKILLS section
was immediately followed by a "Positions of Responsibility"
subheading — not in `ALIASES` — so per Session 6's already-documented,
accepted behavior (an unrecognized heading bleeds into the currently-
open section), everything after it (job titles, club descriptions,
full sentences) got absorbed into SKILLS and then mis-split into 25+
garbage pseudo-skills by `skills_extractor.py`. This is not a new
extractor bug — `skills_extractor.py` behaved exactly as designed on
the text it was given; the text itself was wrong, due to a pre-existing
section-detection gap this milestone happened to be the first to
surface concretely.

Fixed the same way Session 6 established for exactly this situation:
extended the curated `ALIASES[SectionType.OTHER]` vocabulary with
"positions of responsibility" plus two closely related synonyms
("extracurricular activities" / "extra-curricular activities") —
not a generic heading-detection heuristic (already rejected in Session
6), just one more entry in the same trusted, closed mechanism. Verified
the fix directly: `build_resume_skills()` on the real resume now
returns exactly the 15 real skills, not 40. Added a regression test
(`test_positions_of_responsibility_does_not_leak_into_preceding_skills_section`)
reproducing the real layout, not just a synthetic case.

Status: Accepted.

------------------------------------------------------------------------

### `process_resume()` remains the single orchestration path for `/upload-resume`

Reason: an earlier proposal (from ChatGPT's initial review) suggested
inlining `extract_text` → `preprocess` → `detect_sections` →
`extract_contact_info` directly in the route instead of calling
`process_resume()`, specifically to avoid expanding `PipelineResult`
with fields only the route needs. Rejected after further review
(ChatGPT reversed its own position on this point): duplicating the
four-stage chain in the route would create two independently
maintained orchestration paths — one exercised by `process_resume()`'s
existing unit tests, one wired to the actual API — that would need to
be kept in perfect sync by hand. The route calls `process_resume()`
unchanged; `PipelineResult` was not expanded, since this milestone's
scope (`Upload`-only persistence) doesn't actually need anything
`PipelineResult` doesn't already provide.

Status: Accepted.

------------------------------------------------------------------------

# 12. Module Status

| Module | Status |
|---------|--------|
| Parser | Production (resumes only — see Job Description row) |
| Domain Models | Production |
| Preprocessing | Foundation Complete + Section Detection |
| Extraction | Contact Info + Name + Education/Experience entries + Skills list (structural fields only for entries — see Section 11) |
| Pipeline Orchestration | Wired live: `POST /upload-resume` calls `process_resume()` end-to-end |
| Job Description Ingestion | Live — `POST /upload-job` parses a JD PDF (reusing `extract_text`/`clean_text`, not resume section detection/extraction), persists `Job`/`Upload`, manually verified. Title is user-provided, not extracted (no real JD data exists to validate a heuristic against). |
| Embeddings | Hardened, verified, and now live — `encode()` is called for real by every `/rank` request via `build_resume_embedding()`/`build_job_embedding()`. `prepare_resume_embedding_text()` (resume-specific text prep) lives in `src/pipeline.py`, not in `src/embeddings/`, which stays domain-agnostic. |
| Similarity | Live — `cosine_similarity()` is called for real by every `/rank` request, verified against real data (scores in a sane range, correct relative ordering). |
| Scorer | `compute_skill_score()` is live and real (`src/scorer/skill_matcher.py`), called by every `/rank` request; `compute_score()`'s weighted blend is still unwired — 2 of 4 signals (experience/education) remain uncomputable, and `/rank` continues to expose `semantic_score`/`skill_score` as independent fields rather than a blended total (see Section 11). |
| Feedback | Scaffold — `generate_feedback()` exists, never called |
| Database | `Upload`, `Candidate`, `Resume` written by `/upload-resume`; `Upload`, `Job` written by `/upload-job` (both verified against real data); `Score` and `Feedback` remain entirely unpopulated — `/rank` deliberately does not write `Score` rows (see Section 11) |
| Backend | `POST /upload-resume`, `POST /upload-job`, and `POST /rank` are all live, tested, and manually verified against real data; `/results` and `/download` are still `raise NotImplementedError` stubs (`/results` has nothing persisted to retrieve yet — see Section 11) |
| Frontend | Scaffold — Streamlit UI renders upload widgets and a "Rank" button, but the handler just shows `"Ranking pipeline not implemented yet"`; no `src/` imports, no API calls |
| Export | **Not started.** No module exists despite being the final step in the Section 4 architecture diagram. |

**Honest summary**: resume ingestion, Job Description ingestion, and ranking now all work end-to-end through real, tested, manually-verified HTTP routes (`POST /upload-resume`, `POST /upload-job`, `POST /rank`), and `/rank` now exposes two genuine signals — semantic similarity and skill overlap — both verified on real data, including a real bug (garbage pseudo-skills from an unrecognized "Positions of Responsibility" heading bleeding into SKILLS) found and fixed via that verification, not just assumed correct. What's still missing: experience/education scoring don't exist, so `Scorer`'s weighted blend stays unwired and nothing is persisted to `Score`; `/results`/`/download` remain stubs; feedback generation doesn't exist; the frontend is still scaffold. Three end-to-end user flows are possible (upload a resume; upload a JD; rank all resumes against a JD, now with two real signals instead of one); nothing explains *why* a candidate ranked where they did yet — that's Feedback's job, still unbuilt.
------------------------------------------------------------------------

# 13. Testing Status

Current

✅ Parser tests passing

✅ Scorer tests passing

✅ Preprocessor tests passing

✅ Section detector tests passing

✅ Contact extractor tests passing

✅ Pipeline orchestration tests passing (real generated PDF, end-to-end)

✅ `/upload-resume` API tests passing (project's first `TestClient` tests: success path, `Upload` row persistence, 422 on `PDFParseError`)

✅ Name extractor tests passing

✅ `/upload-resume` persistence tests passing (`Candidate`/`Resume` creation, skip-on-no-name path, `raw_text` not leaked into the response)

✅ Entry extractor tests passing (including the real hand-traced EDUCATION/EXPERIENCE layouts as test cases, not just synthetic ones)

✅ Job Description ingestion tests passing (`parse_job_description()`, `/upload-job` persistence, required-title validation, 422 on unparseable PDF)

✅ `cosine_similarity()` tests passing (previously zero coverage despite being fully implemented)

✅ `prepare_resume_embedding_text()` tests passing (HEADER exclusion, section ordering, empty-input handling)

✅ Real-model embedding tests passing, run separately from the default suite (see Section 11's test-strategy decision): vector shape/dtype, similar-vs-unrelated semantic scoring, caching behavior

✅ `rank_resumes_against_job()` unit tests passing (fast — mocked embeddings, real `cosine_similarity()`): empty input, single resume, descending sort, identical-score stability, field mapping

✅ `/rank` API tests passing: 404 on nonexistent job, empty list when no resumes exist

✅ First genuine whole-system integration test passing (`pytest -m slow`): real resume + JD upload → real embeddings → real ranking, verified a domain-relevant candidate outranks an unrelated one; plus determinism-across-calls and score-range checks

✅ `extract_skills()` tests passing: real sample resume layout (hand-traced), flat comma list, trailing-period handling, case-insensitive dedup, empty section

✅ `compute_skill_score()` tests passing: exact/partial/zero matches, case-insensitivity, empty-skills 0.0, and the punctuation-heavy cases that empirically broke naive `\b` (C++, C#, .NET) plus the negative controls (Java≠JavaScript, SQL≠PostgreSQL)

✅ Section detector regression test passing, reproducing the real "Positions of Responsibility" bleed-through bug found via manual verification

✅ `/rank` end-to-end integration test extended to assert real `skill_score` values, not just `semantic_score`

Current Result

129 tests total — 123 / 123 passing by default (`pytest`, ~1.6-1.9 sec); 7 / 7 additional real-model tests passing on demand (`pytest -m slow`, ~17-24 sec)

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
-   `POST /upload-resume` manually verified against a live `uvicorn`
    server (not just `TestClient`) using the real
    `samples/Manish_ResumeDA01.pdf`: 200 response with correct
    sections/contact JSON, `Upload` row correctly persisted to the
    real SQLite DB, OpenAPI schema correctly documents both 200 and
    422 responses. Test artifacts (`data/app.db`, `data/uploads/`)
    cleaned up afterward — both are gitignored, not committed.
-   Name extraction manually verified against the real sample resume
    (`samples/Manish_ResumeDA01.pdf`) via `process_resume()`: correctly
    extracted "Manish Kumar Gupta", not just the synthetic "Jane Doe"
    test fixture.
-   `Resume`/`Candidate` persistence manually verified against a live
    `uvicorn` server with the real sample resume: response correctly
    returned `resume_id`/`candidate_id`, `raw_text` confirmed absent
    from the response body (`grep`-checked, not just asserted in a
    test), and the real SQLite DB correctly held one `Candidate` row
    (name + email) and one `Resume` row (linked by `candidate_id`,
    correct filename, 3511 chars of raw text).
-   Entry extraction manually verified against the real sample resume
    via `process_resume()` directly (not just the API): correctly
    recovered all 3 EDUCATION entries with correct title/dates/details
    split, and correctly produced the single honest fallback entry for
    EXPERIENCE (no dates present in that section on this resume).
    Re-verified via a live `uvicorn` server: `education`/`experience`
    correctly present in the JSON response, `raw_text` still absent.
-   Job Description ingestion manually verified against a live
    `uvicorn` server using a generated JD PDF containing the exact
    Education/Experience collision case identified during design
    review (a Requirements block with "Education" and "Experience" as
    short subheadings). Confirmed: 200 response with correct
    `job_id`/`title`/`created_at`, `description` absent from the
    response (`grep`-checked), and the real SQLite DB held the full,
    untouched description text — the JD's own "Education"/"Experience"
    subheadings stored as plain text, not reinterpreted as resume
    sections.
-   Embeddings manually verified against real data end-to-end: ran
    `process_resume()` on the real sample resume, fed the result
    through `prepare_resume_embedding_text()` (confirmed the email
    address is absent from the text passed to the encoder), then
    `encode()` + `cosine_similarity()` against two JD strings — one
    matching the resume's actual domain (electronics/embedded
    systems), one unrelated (pastry chef). Relevant JD scored 0.169,
    unrelated scored 0.019 — the relative ordering is meaningful even
    though absolute cosine-similarity values for MiniLM embeddings are
    not calibrated to a 0-1 "relevance" scale.
-   Test-suite speed verified directly, not assumed: default `pytest`
    confirmed at ~1.6 sec (95 tests), `pytest -m slow` confirmed at
    ~17 sec (4 tests) — including catching and fixing a real bug where
    an early version cost ~20 sec by default despite marker-based
    deselection (see Section 11).
-   `/rank` manually verified against a live `uvicorn` server with
    real data: uploaded the real sample resume (Manish Kumar Gupta,
    actual ECE/electronics background) alongside a synthetic,
    unrelated pastry-chef resume, uploaded a JD requesting an
    electronics engineer, called `/rank`. Correct result: the real
    resume scored 0.189 vs. the chef resume's 0.137 — meaningfully
    higher, correctly ordered. Also verified 404 on a nonexistent
    `job_id` live, not just in tests.
-   Confirmed by direct re-measurement (not assumed) that wiring
    `/rank` into the route did not regress the "fast by default" test
    suite property established in Session 14 — re-ran `pytest` after
    each new import was added while implementing, catching the
    transitive-import risk (see Section 11's lazy-import decision)
    before it could ship.
-   `\b` vs. lookaround boundary matching empirically compared before
    choosing, not decided from documentation alone: ran both against
    7 real test cases (C++, C#, .NET, Node.js, Draw.io, Java-vs-
    JavaScript, SQL-vs-PostgreSQL) and confirmed naive `\b` fails
    silently on the three symbol-suffixed skills. Table recorded in
    Section 11.
-   Skill extraction manually verified against the real sample
    resume — and this verification caught a real bug: the first run
    produced 40 "skills," most of them full sentences from a
    "Positions of Responsibility" section that bled into SKILLS.
    Fixed via an `ALIASES` extension, re-verified: exactly 15 real
    skills recovered, matching the hand-traced expectation. Re-ran
    the full test suite after the fix — no regressions.
-   Skill matching manually verified end-to-end against a live
    `uvicorn` server with the real sample resume and the same
    electronics JD used for the semantic-score verification:
    `skill_score: 0.0` — correctly, honestly reflecting that the
    resume's SKILLS section lists "Verilog" but the JD asks for
    "VHDL" (different strings, no alias awareness), even though
    `semantic_score: 0.189` correctly reflects the real underlying
    domain relevance. A concrete, real illustration of the documented
    exact-matching limitation (Section 11), not a hypothetical one.

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

## API Wiring (Session 9, Claude, cross-reviewed with ChatGPT)

### Achievements

- Committed and pushed all of Sessions 5–8's previously-uncommitted work (`feature/pipeline-orchestration`, PR #2, merged to `main`) before starting new work, closing out the Session 8 Git Note.
- Found and fixed a self-inflicted bug during that commit: a `git add <specific paths>` command omitted `src/models/resume_models.py`'s deletion, so the file's removal never got staged — it rode through the commit and the merge as a "tracked but physically absent" ghost file on `main`. Caught by checking `git status` after the merge rather than assuming it was clean; fixed with a follow-up commit (`f0d7e05`).
- Drafted the `/upload-resume` design (DB session dependency, file handling, HTTP error mapping, persistence scope) and cross-reviewed it with ChatGPT before writing code. ChatGPT's review surfaced a real design tension — whether to expand `PipelineResult` to carry `raw_text`, or duplicate the pipeline chain inline in the route to avoid touching `PipelineResult` — and, on further exchange, reversed its own initial suggestion once it recognized duplicating the chain would create two orchestration paths to keep in sync by hand. Both reviewers converged: `process_resume()` stays the single orchestration path, `PipelineResult` stays unexpanded, and the tension dissolved once we noticed this milestone's actual scope (`Upload`-table-only persistence) never needed `raw_text` in the first place.
- Replaced `get_session()` (plain factory, zero callers, no cleanup) with `get_db()`, a generator-based FastAPI `Depends` dependency.
- Wired `init_db()` into `app/backend/main.py` startup — it existed since the original scaffold but was never actually called anywhere, so no table (including the new `uploads` writes) would have existed at runtime without this.
- Implemented `POST /upload-resume`: saves the upload to `UPLOAD_DIR` under a collision-safe (`uuid4`-prefixed) filename, calls `process_resume()` unchanged, maps `PDFParseError` → HTTP 422, persists an `Upload` row only, returns `PipelineResult` (`sections` + `contact`) as the response body — FastAPI/Pydantic serialized the nested frozen dataclasses and the `SectionType` string Enum correctly with no extra schema layer needed.
- Added the project's first API test infrastructure (`tests/conftest.py`): an isolated in-memory SQLite test DB via `dependency_overrides`, and `UPLOAD_DIR` redirected to `pytest`'s `tmp_path` via `monkeypatch` so tests never touch the real `data/` directory.
- Added 3 API tests (54/54 total passing): success path (sections + contact in the JSON response), `Upload` row persistence, and 422 on an unparseable PDF.
- Manually verified against a live `uvicorn` server (not just `TestClient`) using the real `samples/Manish_ResumeDA01.pdf`: correct 200 response, correct `Upload` row in the real SQLite DB, and a correct OpenAPI schema (both 200 and 422 documented) via `/docs`. Cleaned up the resulting `data/app.db`/`data/uploads/` test artifacts afterward (both gitignored).

### Lessons

- `git add <specific file paths>` does not implicitly stage deletions of paths you didn't list — a deletion needs to be named explicitly (or use `git add -A`/`git rm`). Assuming "the deletion is captured automatically since the file is already gone from disk" was wrong and shipped a ghost tracked-but-missing file all the way to `main` before being caught.
- A second reviewer reversing its own earlier suggestion after more context (ChatGPT walking back the "inline the chain in the route" idea) is a sign the cross-review process is working as intended — the same pattern already seen in Session 6, just with the reviewer catching its own gap this time instead of an outside one.
- A design tension that looks like it needs a hard trade-off (expand `PipelineResult` vs. duplicate the orchestration chain) can sometimes dissolve entirely once you check the *actual* current-milestone scope — neither option was needed because this milestone doesn't persist `Resume` rows at all yet.
- `cmd.exe` and PowerShell are not interchangeable for multi-line git commands — a PowerShell here-string (`@'...'@`) fed to `cmd.exe` executes each line as a separate (failing) command rather than erroring cleanly; worth confirming which shell is actually in front of the user before handing over syntax.

## Name Extraction (Session 10, Claude)

### Achievements

- Designed the approach before coding (Step 2 review): weighed adding `name` directly to `ContactInfo` (one function, one pass over HEADER) against a standalone `CandidateName` model + `name_extractor.py` (mirrors the `ContactInfo`/`contact_extractor.py` precedent exactly). Chose the standalone model — a name isn't a contact channel, and bundling it in would have risked a future breaking rename across `PipelineResult`, tests, and the API response.
- Added `CandidateName` domain model (`src/models/candidate_name.py`) and `extract_name(SectionedResume) -> CandidateName` (`src/extraction/name_extractor.py`), reusing `contact_extractor.py`'s existing `EMAIL_PATTERN`/`PHONE_PATTERN` for a defensive check (don't misreport a contact line as a name if HEADER's first line happens to be an email/phone rather than a name).
- Heuristic: first non-empty line of the HEADER section is the name. No NLP dependency — consistent with every other extraction/detection decision in this project. Documented, accepted gap: a HEADER opening with something other than a name (address, objective line) will misextract; not guarded against since no real resume seen so far exhibits it.
- Wired `name: CandidateName` into `PipelineResult` and `process_resume()` — the same precedent as when `contact: ContactInfo` joined the bundle in Session 8, not a "convenience expansion" of the kind Section 11 argues against elsewhere.
- Added 7 unit tests for the extractor (first-line success, no HEADER, empty HEADER, email-first-line, phone-first-line, leading-blank-lines, immutability) plus one new assertion each in `test_pipeline.py` and `test_upload_resume_route.py` — 62/62 total passing.
- Manually verified against the real sample resume (not just synthetic "Jane Doe" fixtures) — correctly extracted "Manish Kumar Gupta".

### Lessons

- The "own narrow model per extracted concept" precedent from Session 7 held up under a second, different kind of test: this time the alternative (bundling into an existing model) wasn't a placeholder-fields problem like the original `ExtractedResume` rejection, but a semantic-purity one — the precedent still gave the right answer for a different reason, which is a decent sign it's a durable principle rather than a one-off fix for one bug.
- Reusing `contact_extractor.py`'s existing regexes for the defensive email/phone check avoided duplicating pattern definitions — worth doing whenever two extractors read the same section for related-but-distinct facts.

------------------------------------------------------------------------

## Resume/Candidate Persistence (Session 11, Claude)

### Achievements

- Surfaced four real design forks before writing code (Step 2 review): (1) how to source `Resume.raw_text` given `PipelineResult` didn't carry it, (2) whether to deduplicate `Candidate` rows on re-upload, (3) what to do when name extraction returns `None` but `Candidate.name` is `NOT NULL`, (4) whether the response should keep returning bare `PipelineResult` now that persistence produces real DB-generated IDs.
- Added `raw_text: str` to `PipelineResult` (sourced from `ParsedResume.raw_text`) rather than having the route parse the PDF a second time — one parse per request, at the cost of the field needing to be explicitly excluded from the API response.
- Introduced `app/backend/api/schemas.py` — the project's first route-local API schema (`UploadResumeResponse`), holding `resume_id`/`candidate_id`/`sections`/`contact`/`name` and deliberately omitting `raw_text`. First concrete step on the long-standing "No API schemas yet" tech debt item, introduced because a real need existed (hide a persistence-only field, expose real IDs) rather than speculatively.
- Wired `/upload-resume`: on a name present, creates `Candidate` + `Resume` (flushed to get real IDs before commit), always creates `Upload`; on `CandidateName.name is None`, skips `Candidate`/`Resume` entirely and persists `Upload` only, still returning 200.
- Decided against `Candidate` dedup this milestone — always insert a new row, consistent with the project's repeated "don't build speculative logic ahead of a real need" pattern (same reasoning as OCR, `phonenumbers`, generic heading detection).
- Added/updated tests for all four decisions (raw_text present on `PipelineResult`, `raw_text` absent from the API response, `Candidate`/`Resume` correctly persisted and linked, skip-path leaves `Candidate`/`Resume` empty but still persists `Upload`) — 66/66 total passing.
- Manually verified against a live server with the real sample resume: correct `resume_id`/`candidate_id` in the response, `raw_text` confirmed absent via `grep` (not just a test assertion), and correct `Candidate`/`Resume` rows in the real SQLite DB.

### Lessons

- A design fork that looks purely technical (where does `raw_text` come from?) turned out to have a real product-facing consequence (it would leak into the HTTP response) — worth tracing a decision's downstream effects before picking the "simpler" option.
- Introducing a schema/abstraction layer is fine the moment a concrete need exists for it (hiding one field, exposing real IDs) — the earlier "No API schemas yet" gap wasn't a mistake to fix reactively, it just hadn't hit a real need until persistence produced actual database IDs to expose.

------------------------------------------------------------------------

## Education/Experience Entry Extraction (Session 12, Claude, cross-reviewed with ChatGPT)

### Achievements

- Hand-traced two candidate segmentation heuristics against the real sample resume's actual EDUCATION/EXPERIENCE content before proposing a design — found blank-line segmentation fails completely (no blank lines between real entries) and that the real EXPERIENCE section has zero date lines at all, a genuine stress case for any date-anchored approach.
- Designed date-anchored segmentation (`re.fullmatch` against a month/year/range pattern, not `.search()`, to avoid a bullet mentioning a year creating a false boundary) with an honest zero-date fallback (whole section becomes one entry, `title=None, dates=None`) rather than guessing.
- Deliberately scoped `ResumeEntry` to structural fields only (`title`, `dates`, `details`) — explicitly narrower than the original TODO wording ("dates, companies, degrees" as three fields) — since no reliable text-only delimiter exists to split degree/GPA/location apart, confirmed by hand-tracing real entry content.
- Cross-reviewed the full design with ChatGPT before implementing (pasting the real hand-traced section content directly into the review, not just a description of it). ChatGPT approved the core approach and requested two refinements: describe "title = line before date" as an implementation rule rather than a claim about resumes in general, and document a known limitation (one date anchor assumed per logical entry — a sub-timeline within one job would over-segment). Both incorporated into the model/function docstrings and this document.
- Implemented `ResumeEntry` (`src/models/resume_entry.py`) and `extract_entries()` (`src/extraction/entry_extractor.py`), including a blank-line-aware title lookback discovered while implementing (a title-search that stopped exactly one line back would have failed on a blank-line-separated layout like `"Google\n\nJan 2020 – Present"`) — caught and fixed before shipping, not left as a latent gap.
- Wired `education`/`experience` fields into `PipelineResult` and `UploadResumeResponse`; explicitly deferred DB persistence (no `Education`/`Experience` tables exist), consistent with how contact/name extraction each preceded their own persistence milestone.
- Added 8 new extractor unit tests (including the real hand-traced EDUCATION/EXPERIENCE content as literal test cases, not just synthetic ones) plus new assertions in `test_pipeline.py` and `test_upload_resume_route.py` — 76/76 total passing.
- Manually verified against the real sample resume twice: directly via `process_resume()`, and again via a live `uvicorn` server — both correctly recovered all 3 EDUCATION entries and the single honest EXPERIENCE fallback.

### Lessons

- Hand-tracing against real data *before* proposing a design (not after) is what surfaced the EXPERIENCE zero-date case — if the design had been proposed first and tested second, this stress case might have been found only after implementation, when a fix is more disruptive.
- A second reviewer's most valuable contribution this round wasn't a different design — it was catching two places where the write-up *overclaimed* what the code actually guarantees ("title = institution" instead of "title = the line the extractor found"). Precision in documentation matters as much as correctness in code, since future-you (or an interviewer) will trust the written contract over re-reading the implementation.
- Implementing the approved design surfaced one more edge case neither reviewer traced (a blank line directly before a date line) — a reminder that cross-review catches a different class of issue than implementation-time testing; both are needed, neither substitutes for the other.

------------------------------------------------------------------------

## Job Description Ingestion (Session 13, Claude, cross-reviewed with ChatGPT)

### Achievements

- Actually researched before designing, per this document's own "least explored, start with research" note: read the frontend scaffold, the `/upload-job` route stub's existing signature, and the `Job` table schema to establish the format is PDF (not pasted text) — two independent scaffold artifacts agreed, and the schema wasn't actually a contradiction once compared directly to how `Resume.raw_text` already works.
- Read `section_detector.py`'s actual matching logic (not assumed) to identify a concrete, traceable risk: a JD's own "Education"/"Experience" requirement subheadings would exact-match the existing resume `ALIASES` table if `detect_sections()` were reused, silently mislabeling JD content as resume sections. This directly justified not reusing it.
- Designed `parse_job_description()` reusing `extract_text()`/`clean_text()` (both verified generic) while explicitly rejecting `detect_sections()`/any resume extraction stage.
- Decided job title is a required user-provided form field, not extracted — the one prior extraction milestone this differs sharply from: every earlier heuristic (contact, name, entries) was verified against a real resume before shipping, and no real JD sample exists anywhere in this repo to validate a title heuristic against.
- Decided against introducing a `ParsedJobDescription` domain model, consistent with the project's "only introduce a model once multiple consumers exist" pattern (no second JD-processing stage exists yet).
- Cross-reviewed the full design with ChatGPT (including the actual `detect_sections()` collision example) before implementing; ChatGPT's one substantive addition was the `parse_job_description()` orchestration-helper suggestion, adopted, plus a tech-debt note about `clean_text()`'s ownership (see Section 18).
- Implemented `src/job_pipeline.py`, `UploadJobResponse`, and `POST /upload-job` (`title: str = Form(...)` + `file: UploadFile`), persisting `Job` + `Upload`, mapping `PDFParseError` → 422, excluding the full `description` from the response (same reasoning as `raw_text` on `/upload-resume`).
- Added 9 new tests (`parse_job_description()` unit tests including the literal Education/Experience collision content as a test case; `/upload-job` API tests for success, missing-title 422, and empty-PDF 422) — 85/85 total passing.
- Manually verified against a live server using a generated JD PDF containing the exact collision case: confirmed the DB stored the JD's "Education"/"Experience" subheadings as plain, untouched text.

### Lessons

- This milestone needed real research before any design was possible — unlike the last three sessions, which extended an already-established resume pipeline, JD ingestion required checking assumptions against actual scaffold code (frontend widget, route stub, DB schema) that had sat untouched since Session 1.
- A risk found by reading actual matching logic (the `ALIASES` collision) is categorically stronger evidence than a risk reasoned about in the abstract — this is the same discipline Session 6 used when it insisted on running code rather than trusting a description of it.
- Not every extraction slice needs a heuristic — sometimes the right design is recognizing that no evidence exists to build one responsibly (job title), and asking for the data directly instead of guessing.

------------------------------------------------------------------------

## Embeddings Module (Session 14, Claude, cross-reviewed with ChatGPT)

### Achievements

- Measured the existing scaffold before proposing any design, rather than trusting the project's own documented "Embedding <1 sec" goal: found import (~15.6s) + first model load (~6.1s) vs. warm inference (~0.02s) are three completely different numbers that had been collapsed into one misleading claim.
- Cross-reviewed the design with ChatGPT: agreed on deferring persistence/wiring to a future `/rank` milestone; ChatGPT reframed my "Option A vs B" framing for resume embedding text into the more useful question of what the Embeddings module's *contract* should be, correctly citing Section 7's own pre-existing "Embeddings — Generate vectors only" line I hadn't checked against.
- Implemented `prepare_resume_embedding_text(SectionedResume) -> str` in `src/pipeline.py`, keeping `src/embeddings/` itself domain-agnostic; hardened `encoder.py` with a return-type annotation and a docstring recording the measured timings.
- Attempted a fast, mocked orchestration test file first, then **measured that it didn't achieve its goal and deleted it**: `encoder.py` imports `sentence_transformers` at module level, so importing the module to monkeypatch it pays the full ~15s cost regardless of mocking. Caught by re-running the suite and watching the time not improve, not by reasoning about it in the abstract.
- Also caught and fixed a second real bug in the same area: the `slow`-marked integration test file initially imported `encode` at module level, which meant pytest paid the import cost during test *collection* even for deselected tests — "3 deselected" tests still cost ~20 seconds. Fixed by deferring the import inside each test function.
- Added `pytest.ini` (`slow` marker, `addopts = -m "not slow"`) so the default `pytest` invocation — used ~15 times already this session — stays fast.
- Added tests for `cosine_similarity()` (previously zero coverage despite being a fully correct, already-implemented function) and `prepare_resume_embedding_text()` to the fast suite; consolidated all real-model tests (vector shape, similar-vs-unrelated semantic scoring, caching behavior) into one `slow`-marked file.
- Manually verified against real data twice: `prepare_resume_embedding_text()` confirmed to exclude the real sample resume's email; `encode()` + `cosine_similarity()` confirmed a JD matching the resume's actual domain scores meaningfully higher (0.169) than an unrelated one (0.019).
- Recorded, but did not implement, four future considerations ChatGPT raised: model version pinning, never hardcoding embedding dimensionality, keeping device (CPU/GPU) handling internal to the embedding layer, and not designing today's single-string `encode()` API in a way that would make future batch encoding a breaking change (see Section 18).

### Lessons

- A performance claim already sitting in the project's own documentation ("Embedding <1 sec") turned out to be wrong as stated the moment it was actually measured — the same "verify, don't trust the write-up" discipline from Session 4, just applied to this project's own prior documentation instead of someone else's.
- A test-isolation strategy can look correct in design and still fail in practice for a reason invisible until measured (mocking a module doesn't avoid that module's own top-level imports) — this is now the second time this session a design had to be corrected after implementation surfaced a wrong premise (the first being the blank-line title-lookback bug in Session 12), reinforcing that "cross-reviewed and approved" is not the same as "verified against running code."
- Deselected tests are not free — pytest still imports a test module during collection regardless of whether marker-based filtering will skip its tests, a subtlety that would have silently reintroduced the exact regression the `slow` marker was meant to prevent.

------------------------------------------------------------------------

## `/rank` Wiring (Session 15, Claude, cross-reviewed with ChatGPT)

### Achievements

- Identified two real gaps before designing: `ScoreComponents` needs four inputs but only `semantic` is computable (nothing extracts skills or scores experience/education), and `Score`'s four columns are all `NOT NULL` so persisting a row today would mean fabricating three of four values. Recommended bypassing `Scorer` and not persisting `Score` this milestone; ChatGPT independently agreed and specifically argued against a nullable-columns migration as churn without long-term benefit — the columns aren't optional by design, they're incomplete because the feature isn't built.
- Cross-reviewed the full design with ChatGPT, which flagged "pipeline divergence" as the milestone's biggest new risk — the first time two independent code paths (upload-time preprocessing, rank-time re-derivation from stored `raw_text`) both prepare resume/JD text for embedding, with real risk of silently drifting apart if not shared.
- Implemented shared `build_resume_embedding()` (`src/pipeline.py`) and `build_job_embedding()` (`src/job_pipeline.py`) per that concern, so `src/ranking.py` never re-implements text preparation itself.
- Implemented `src/ranking.py`'s `rank_resumes_against_job()` — DB-session-free, sorted descending by semantic similarity, `[]` for empty input, never raises.
- Found a real problem while implementing that neither the design brief nor ChatGPT's review anticipated: once `app/backend/api/routes.py` imports `src/ranking.py` → `src/pipeline.py` → `src/embeddings/encoder.py`, *every* API test using the `client` fixture — including `/upload-resume`/`/upload-job` tests that never touch `/rank` — would transitively import `sentence_transformers`/`torch` just from importing `app.backend.main`, silently re-breaking the fast-by-default test suite fixed in Session 14. Fixed by making the `sentence_transformers` import lazy inside `get_model()` rather than at `encoder.py`'s module top level. Verified immediately by re-running `pytest` after each new import was added, not assumed correct.
- That same fix, as a side effect, made mocking work for the first time in this area — Session 14's mocking attempt failed because `encoder.py`'s top-level import defeated it regardless of what was mocked; with the lazy import, `monkeypatch.setattr("src.ranking.build_resume_embedding", ...)` works cleanly, enabling genuinely fast unit tests for `rank_resumes_against_job()`'s sorting/orchestration logic.
- Wired `POST /rank`: 404 on a nonexistent `job_id`, joins `Resume`+`Candidate` (no ORM relationship exists between them, so an explicit join condition is used), returns results sorted descending.
- Added 10 new tests across three files (5 fast unit tests with mocked embeddings, 2 fast API tests, 3 slow real-model tests including the project's first genuine whole-system integration test — real upload, real embeddings, real ranking, composed together) — 109 total, 102 fast + 7 slow.
- Manually verified against a live server with real data: the actual sample resume (genuine ECE/electronics background) correctly outranked a synthetic, unrelated pastry-chef resume against an electronics-engineer JD (0.189 vs. 0.137).

### Lessons

- A risk ChatGPT correctly flagged in the abstract (pipeline divergence) and a risk found only by actually wiring the code together (transitive test-suite slowdown) are both real, and neither substitutes for the other — cross-review catches architectural risks; running the actual code catches implementation risks. This milestone needed both.
- The same lazy-import fix served two different purposes depending on when it mattered: preventing an unrelated import chain from paying a cost (the actual motivating problem here), and — as a side effect — finally making a mocking strategy work that had failed for an unrelated reason in Session 14. Worth remembering that fixing the root cause of one problem sometimes resolves a second, previously-abandoned approach for free.
- Re-running the fast test suite after every single new cross-module import, not just at the end of a milestone, caught the transitive-import regression before it could ship — the same "verify continuously, not just once at the end" discipline this project has leaned on all session, applied at finer granularity than usual.

------------------------------------------------------------------------

## Skill Matching (Session 16, Claude, cross-reviewed with ChatGPT)

### Achievements

- Hand-traced skill extraction against the real sample resume's SKILLS section before designing, same discipline as every extraction milestone this session; verified the "text after first colon, or whole line" heuristic against all three lines including the "Draw.io." trailing-period edge case.
- Weighed two designs for the JD-side matching signal: a curated global skill dictionary (rejected — unbounded vocabulary, same problem already rejected for section headings) vs. searching the JD for the candidate's own extracted skills (chosen — no external vocabulary needed). Cross-reviewed with ChatGPT, which agreed and credited the chosen design with keeping extraction (document-local) and scoring (document-to-document) as clean, separate responsibilities.
- Explicitly documented, rather than silently accepted, two honest limitations raised in cross-review: `skill_score` answers "what fraction of the candidate's skills are relevant here," not "what does the JD require that's missing" (needs independent JD-skill extraction with no real corpus to validate it against); and matching is exact-token only, no alias awareness (Git≠GitHub, SQL≠PostgreSQL) — an alias dictionary would just relocate the same unbounded-vocabulary problem one level down.
- ChatGPT asked that `\b` word-boundary behavior around punctuation-heavy skills (C++, C#, Node.js, Draw.io, .NET) be verified empirically before relying on it — ran both naive `\b` and a lookaround-based alternative against 7 real test cases and found naive `\b` **silently fails** on C++/C#/.NET (both characters bounding the match can be non-word, so no `\b` transition exists). Shipped the lookaround approach instead, verified against all 7 cases including the Java/JavaScript and SQL/PostgreSQL negative controls.
- Refactored `src/pipeline.py` to extract a shared `_reconstruct_sections()` helper before adding `build_resume_skills()`, so it and `build_resume_embedding()` both go through identical raw-text reconstruction — directly applying Session 15's "pipeline divergence" lesson to two rank-time helpers, not just upload-time vs. rank-time.
- Manually verified skill extraction against the real sample resume and found a real bug: 40 "skills" extracted instead of ~15, most of them full sentences. Root cause: a "Positions of Responsibility" subheading (not in `ALIASES`) bled its content into the preceding SKILLS section per Session 6's already-documented, accepted section-detection behavior — `skills_extractor.py` behaved correctly on the text it was given; the text itself was wrong. Fixed the same way Session 6 established for this exact situation: extended `ALIASES[SectionType.OTHER]`, not the extractor. Re-verified: exactly 15 real skills. Added a regression test reproducing the real layout.
- Wired `skill_score` into `RankedCandidate`/`/rank`'s response as an independent field alongside `semantic_score` — not blended, since `Scorer`'s weighted blend still needs experience/education to exist first. Sort order unchanged (still `semantic_score` only) — per ChatGPT, adding a field to the response isn't the same decision as using it to rank.
- Added 20 new tests across four files (extraction, matching, ranking-with-skills, integration) — 129 total, 123 fast + 7 slow (six of seven pre-existing slow tests unaffected; one integration test extended).
- Manually verified end-to-end against a live server with real data: `skill_score: 0.0` for the real resume against the electronics JD — an honest, correct result (SKILLS lists "Verilog," JD asks for "VHDL," different strings) that concretely illustrates the documented exact-matching limitation.

### Lessons

- A concern ChatGPT raised as "worth verifying" (not "this is definitely broken") turned out to be a real, silent bug — `\b` failing on C++/C#/.NET wouldn't have raised an exception or an obviously wrong result, it would have just silently under-counted matches forever. Treating "please verify this" requests as seriously as "this is broken" reports is worth continuing.
- The "Positions of Responsibility" bug is the clearest example yet in this project of a latent, already-documented limitation (Session 6's accepted heading-bleed gap) only becoming a *concrete* problem once a new consumer (skill extraction) started actually depending on section boundaries being clean. The original decision to accept the gap wasn't wrong — but accepting a gap doesn't mean it stops mattering once something new is built on top of it; real-data verification at each new milestone is what keeps catching this, not a one-time audit.
- Refactoring to share code (`_reconstruct_sections()`) before adding the second caller, rather than after, avoided ever having two independently-maintained reconstruction paths to begin with — cheaper than fixing divergence after the fact, and a direct, concrete application of a lesson from the immediately preceding session rather than an abstract principle.

------------------------------------------------------------------------

# 16. Current TODO

## High Priority

- Build real skill/experience/education scoring so `Scorer` can finally be wired — `/rank` is semantic-only today by deliberate, documented choice (Section 11), not because the other signals were forgotten
- Score experience/education so `Scorer`/`Score` persistence can finally be wired — 2 of 4 signals now real (`semantic_score`, `skill_score`); this is what's left
- Wire the remaining 2 stub routes (`/results`, `/download`) — `/results` needs `Score` persistence to exist first (still deferred, Section 11)
- Extend `ALIASES` for further common headings not yet recognized (e.g. Certifications synonyms, Summary synonyms) — same mechanism just used for "Positions of Responsibility"
- Export module — final architecture step (Section 4), doesn't exist yet

## Medium

- Non-NANP phone format support (revisit stdlib-vs-`phonenumbers` decision if needed)
- Additional Unicode normalization
- `MAX_UPLOAD_SIZE_MB` (in `app/backend/config.py`) is still defined but unenforced by `/upload-resume` — no size validation exists yet
- `UPLOAD_DIR` has no retention/cleanup policy — every upload is kept indefinitely under a `uuid4`-prefixed filename

## Low

- FAISS
- PostgreSQL
- MLflow
------------------------------------------------------------------------

# 17. Next Session

Goal

One clear recommendation: **experience/education scoring** — the last piece needed before `Scorer`/`Score` persistence can finally be wired. Two of four `ScoreComponents` signals are now real (`semantic_score`, `skill_score` — Session 16); this is what's left.

Tasks

- Design a heuristic for turning `ResumeEntry.dates` (already extracted, but only as an unparsed string like "Sep 2023 – 2027") into a comparable duration/recency signal — needs hand-tracing against the real sample resume's actual dates before committing to a parsing approach, same discipline as every prior extraction milestone.
- Decide what a JD's experience/education *requirement* looks like as extractable structure (e.g. "3+ years required," "Bachelor's degree required") — another JD-side gap, same category of problem `parse_job_description()` (JD has no section structure) and skill matching (JD has no independent skill list) each already navigated by sidestepping independent JD extraction. Consider whether the same sidestep applies here (e.g., check for the candidate's own experience duration/degree level appearing in JD-recognizable patterns) rather than assuming a full JD-side parser is needed.
- Add comprehensive unit tests; verify against real data (the sample resume's actual EDUCATION/EXPERIENCE entries).

Once experience/education scoring is real, revisit wiring `Scorer`/`ScoreComponents` and persisting `Score` rows — both deliberately deferred since Session 15 (Section 11), not abandoned. At that point also reconsider whether `/rank`'s response should gain an aggregate score field (explicitly avoided so far per ChatGPT's "don't imply a complete ranking methodology before one exists" reasoning) now that all four signals would finally be real.
------------------------------------------------------------------------

# 18. Known Technical Debt

-   Parser catches generic Exception for the fitz.open/get_text block
-   API schemas now exist (`app/backend/api/schemas.py`: `UploadResumeResponse`,
    `UploadJobResponse`, `RankResponse`) but only cover the 3 live
    routes; `/results`/`/download` will need their own once built.
-   No relationships in SQLAlchemy models — `/rank`'s `Resume`-to-`Candidate`
    join uses an explicit join condition (`Resume.candidate_id == Candidate.id`)
    rather than an ORM relationship, since none is configured
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
-   `/upload-resume` now persists `Upload`/`Candidate`/`Resume`, but
    `Score` and `Feedback` remain entirely unpopulated — nothing
    computes a score yet, so nothing has a score/feedback to persist.
-   `Candidate` rows are never deduplicated — re-uploading the same
    person's resume creates a new `Candidate` (and `Resume`) row every
    time. Accepted for now (Section 11); revisit once a concrete
    requirement needs "one candidate, many resumes" semantics.
-   When name extraction returns `None`, `/upload-resume` silently
    skips `Candidate`/`Resume` persistence (`Upload` only) — a user
    uploading such a resume gets a 200 with `resume_id`/`candidate_id`
    both `None` and no visible error explaining why nothing was saved.
    Accepted as correct behavior (Section 11) but worth noting as a
    UX gap once there's a frontend to surface it in.
-   `ResumeEntry` extracts structural fields only (`title`/`dates`/
    `details`) — degree, GPA, institution vs. company, and location
    are not decomposed and remain embedded in `details` as raw text.
    Accepted (Section 11): no reliable text-only delimiter exists to
    split them without guessing. Revisit only if a dedicated semantic
    parsing stage is deliberately introduced later (ChatGPT's
    suggested future direction: `ResumeEntry` → `EducationRecord`/
    `ExperienceRecord`, a separate pipeline stage, not a fatter
    `ResumeEntry`).
-   Entry segmentation assumes one date anchor per logical entry — a
    single entry containing more than one standalone date-shaped line
    (e.g. a sub-timeline within one job) will be over-segmented into
    multiple `ResumeEntry` objects. Not observed in the one real
    resume available; logged as a known, plausible gap rather than
    guarded against without evidence.
-   No `Education`/`Experience` DB tables exist — extracted entries
    are returned in the API response but never persisted, same
    extraction-before-persistence sequencing already used for contact
    info and name.
-   `clean_text()` is currently an inner implementation detail of
    `src/preprocess/preprocessor.py`, but now has two consumers
    (`preprocess()` for resumes, `parse_job_description()` for JDs via
    direct import). Tolerated for now (per ChatGPT cross-review) —
    two consumers doesn't yet justify moving it. Revisit trigger: if a
    third document type needing the same text hygiene appears (e.g.
    cover letters), promote `clean_text()` into a shared, generic text
    normalization utility module instead of leaving it inside a
    resume-specific file.
-   `Job.title` is a required, unvalidated free-text field — no
    minimum length, no uniqueness constraint, no attempt to detect a
    near-duplicate job posting. Accepted for this milestone (Section
    11); no requirement yet forces more than "the user typed
    something."
-   No `ParsedJobDescription` domain model exists — `parse_job_description()`
    returns a plain `str`. Accepted (Section 11); revisit if a second
    JD-processing stage needs a stable, richer input contract.
-   Name extraction (`src/extraction/name_extractor.py`) assumes the
    first non-empty HEADER line is the name. A resume whose HEADER
    opens with an address, objective statement, or anything else
    before the name will misextract (returns that line, or — if it
    happens to look like an email/phone — `None`). No real resume
    seen so far exhibits this; documented as an accepted gap, not
    fixed with an untuned heuristic (e.g. a word-count cap).
-   The remaining 2 routes (`/results`, `/download`) are still
    `raise NotImplementedError` stubs — `/results` needs `Score`
    persistence to exist first, which is itself deliberately deferred
    (see Section 11).
-   `/rank` exposes `semantic_score`/`skill_score` as independent
    fields, still sorts by `semantic_score` only — `skill_score` isn't
    yet used for ordering, just returned. `Scorer`/`ScoreComponents`'s
    weighted blend remains unwired (experience/education still aren't
    real), and no `Score` row is ever persisted. All deliberate,
    documented decisions (Section 11), not oversights; revisit once
    experience/education scoring exist (see Section 17).
-   Skill matching is exact-token only — no alias/synonym awareness
    (Git≠GitHub, SQL≠PostgreSQL, JS≠JavaScript). Accepted (Section 11):
    an alias dictionary has the same unbounded-vocabulary problem
    already rejected for skill extraction itself. Revisit only if a
    concrete need forces it.
-   `compute_skill_score()` only answers "what fraction of the
    candidate's declared skills are relevant to this JD" — not "what
    skills does the JD require that the candidate is missing," which
    needs independent JD-skill extraction with no real JD corpus to
    validate a heuristic against. Left for a future Feedback milestone
    (Section 11).
-   `skills_extractor.py`'s heuristic doesn't handle a bullet-per-line
    SKILLS layout ("• Python\n• SQL") — only category-prefixed and
    flat comma-separated lists, the only formats seen in the one real
    resume available. Documented gap, not guessed at without evidence.
-   No candidate-pool/application concept exists in the schema —
    `/rank` compares a `Job` against every `Resume` row in the system.
    Deliberate (Section 11); revisit if "candidates applied to this
    job" ever becomes a real requirement.
-   Embeddings have no persistence — every `/rank` call recomputes
    both the JD embedding and every resume embedding from scratch,
    including re-deriving each resume's `SectionedResume` from stored
    `raw_text`. Deliberate (Section 11: recomputation was already
    unavoidable given `SectionedResume` itself is never persisted);
    revisit if `/rank` latency becomes a demonstrated problem at
    realistic resume-count scale.
-   Embedding model version is unpinned beyond the string
    `"all-MiniLM-L6-v2"` — if that identifier's resolved weights ever
    change upstream, embeddings could shift subtly with no local
    signal that it happened. Not solved now (per ChatGPT cross-review);
    revisit if reproducibility across environments/time becomes a
    real requirement.
-   Embedding dimensionality is deliberately never hardcoded anywhere
    in the codebase (tests assert `shape[0] > 0`, not `== 384`) so a
    future model swap doesn't require hunting down a magic number.
-   Device (CPU/GPU) handling is entirely implicit — `SentenceTransformer`
    auto-selects today. If GPU support is ever added, that logic
    should stay internal to `src/embeddings/encoder.py`; nothing
    outside that module should need to know or care which device ran
    the model.
-   `encode(text: str)` only exercises single-string input today; the
    underlying `SentenceTransformer.encode()` already accepts
    `list[str]` and returns a 2D array for batch input, so this isn't
    blocked, just not implemented. `/rank` calls `encode()` once per
    resume sequentially (N model invocations, not batched) — accepted
    for now given measured warm inference (~20ms/call) makes even 50
    resumes ≈1 second; revisit only if resume counts at realistic
    scale demonstrate this as an actual bottleneck.
-   No request-size validation on `/upload-resume` — `MAX_UPLOAD_SIZE_MB`
    is defined in config but not enforced. No cleanup/retention policy
    on `UPLOAD_DIR` — every uploaded file is kept indefinitely.
-   `PipelineResult` (`src/pipeline.py`) is a flat bundle of exactly two
    fields (`sections`, `contact`) with one caller (`/upload-resume`).
    ChatGPT's cross-review flagged that as more pipeline stages arrive
    (embeddings, similarity, scoring, feedback) a flat result type may
    stop being the right orchestration contract, and a dedicated
    application-level Pipeline Orchestrator might become more
    appropriate. Not an action item — a revisit trigger for whenever a
    second caller or a third+ stage actually needs it.
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

Embedding — corrected Session 14; the original "<1 sec" collapsed
three fundamentally different events into one misleading number.
Measured, not assumed:

| Event | Time | Frequency |
|---|---|---|
| First-ever model download (network) | ~37 sec | once per environment, ever |
| Cold process startup (import `sentence_transformers`/`torch` + load cached weights) | ~22 sec (~15.6s import + ~6.1s load) | once per process lifetime |
| Warm inference (model already resident via `lru_cache`) | ~20 ms | every call after the first, within that process |

The "<1 sec" goal is met, but only for warm inference — which is what
actually matters in a long-lived server process (the cold cost is
paid once at/near startup, not per request). Not yet meaningful for
API latency since nothing calls `encode()` from a route yet.

Similarity \<200 ms (met: pure numpy, effectively instant — no
dedicated benchmark run, cost is negligible relative to embedding)

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
-   Why `get_db()` (a generator) replaced `get_session()` (a plain factory), and why that's the idiomatic FastAPI pattern
-   Why `PDFParseError` maps to HTTP 422 instead of 400
-   Why `/upload-resume` persists to the `Upload` table only, and doesn't invent a placeholder `Candidate.name` to populate the rest of the schema today
-   Why `Resume.raw_text` is defined as `ParsedResume.raw_text` (canonical parser output) rather than `StructuredResume.normalized_text` (a derived artifact)
-   Why the route calls `process_resume()` unchanged instead of inlining the four-stage chain, even though that would have avoided a hypothetical `PipelineResult` expansion
-   Why a `git add <paths>` that omits a deleted file's path won't stage that deletion
-   Why `CandidateName` is a separate model from `ContactInfo` instead of a third field on it
-   Why name extraction uses a first-HEADER-line heuristic, and what real-world resume layout would break it
-   Why `PipelineResult` gaining a `name` field isn't the "expansion for convenience" the project otherwise avoids
-   Why `PipelineResult` gained a `raw_text` field, but the API response deliberately doesn't return it
-   Why `UploadResumeResponse` (`app/backend/api/schemas.py`) exists as a route-local schema instead of returning `PipelineResult` directly, and why introducing it now isn't the same as the "no schemas yet" gap being a mistake
-   Why `Candidate` rows aren't deduplicated on re-upload, and what would change that decision
-   Why `/upload-resume` skips `Resume`/`Candidate` persistence entirely (rather than writing a partial row) when name extraction finds nothing
-   Why entry segmentation anchors on standalone date lines (`re.fullmatch`) instead of blank lines, and what real resume content proved blank-line segmentation wrong
-   Why `ResumeEntry` doesn't have separate `degree`/`company`/`location`/`GPA` fields, and what evidence justifies that boundary
-   Why the extractor returns one honest fallback entry (not zero, not a guess) when a section has no date lines at all
-   Why "the line before the date becomes the title" is documented as an implementation rule rather than a claim about how resumes are generally structured
-   Why Job Description ingestion reuses `extract_text()`/`clean_text()` but not `detect_sections()`, and the concrete collision case that proves the risk
-   Why a job title is a required user input rather than extracted, in contrast to a resume's name
-   Why no `ParsedJobDescription` domain model exists, and what would justify introducing one
-   Why `clean_text()` still lives inside `preprocessor.py` despite having two consumers now, and what would justify moving it
-   Why Embeddings persistence and route wiring were deferred to a future `/rank` milestone instead of built alongside the encoder
-   Why `prepare_resume_embedding_text()` lives in `src/pipeline.py` rather than `src/embeddings/`, and how that decision traces back to a module responsibility ("Embeddings — Generate vectors only") written before this milestone even started
-   Why the HEADER section is excluded from the text fed to the embedding model
-   Why a "fast, mocked" test strategy for the encoder was abandoned after implementation, and what that reveals about mocking a module with heavy top-level imports
-   Why marker-based test deselection alone didn't prevent a ~20 second regression, and what the actual fix was
-   Why embedding dimensionality is never hardcoded anywhere in the codebase
-   Why `/rank` bypasses `Scorer` and ranks on raw cosine similarity instead of a weighted blend
-   Why no `Score` row is persisted, and why a nullable-columns migration was considered and rejected rather than adopted as a quick fix
-   Why `/rank` compares a Job against every `Resume` in the system, and what would change that
-   Why embeddings are computed fresh on every `/rank` call instead of cached, and how that decision connects to an earlier one (only `Resume.raw_text` is persisted, not `SectionedResume`)
-   Why `build_resume_embedding()`/`build_job_embedding()` exist as shared helpers instead of `src/ranking.py` preparing text itself, and what risk that prevents
-   Why making `sentence_transformers`'s import lazy was necessary once `/rank` existed, even though nothing about `/rank` itself required it directly
-   Why skill matching searches the JD for the candidate's own extracted skills, rather than maintaining a curated global skills dictionary
-   Why `skill_score` measures "relevant skills" rather than "missing skills," and what would be needed to answer the second question
-   Why `\b` was empirically tested rather than trusted, what it got wrong for `C++`/`C#`/`.NET`, and how the lookaround fix differs
-   Why the "Positions of Responsibility" bug wasn't actually a bug in the new skills extractor, and what that says about how bugs can hide in already-accepted, already-documented limitations until something new depends on them
-   Why the `ALIASES` extension (not a code change to `skills_extractor.py`) was the correct fix, and how that traces back to a Session 6 precedent

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

Completed (Session 9)

- Committed and pushed all previously-uncommitted Session 5–8 work (`feature/pipeline-orchestration`, PR #2, merged to `main`); found and fixed a stale-tracked-deletion bug (`resume_models.py`) introduced during that commit.
- Designed `/upload-resume` wiring and cross-reviewed the design with ChatGPT to convergence, including ChatGPT reversing an initial suggestion after further exchange (keep `process_resume()` as the single orchestration path; don't expand `PipelineResult`; the apparent trade-off between the two dissolved once this milestone's actual persistence scope was checked).
- Replaced `get_session()` with a generator-based `get_db()` `Depends` dependency; wired the previously-never-called `init_db()` into FastAPI startup.
- Implemented `POST /upload-resume`: save → `process_resume()` → 422 on `PDFParseError` → persist `Upload` row only → return `sections` + `contact`.
- Added the project's first API test infrastructure (`tests/conftest.py`, isolated in-memory DB, `TestClient`) and 3 new tests — 54/54 total passing.
- Manually verified against a live `uvicorn` server with the real sample resume PDF (200 response, correct `Upload` row, correct OpenAPI schema); cleaned up test artifacts afterward.
- PROJECT_BIBLE synced with repository (version, module status, testing status, verification checklist, new design decisions, tech debt, session log, TODO/next session, interview talking points).

Completed (Session 10)

- Reviewed the design (Option A: standalone `CandidateName` model + `name_extractor.py`, vs. Option B: extend `ContactInfo`) before coding; chose Option A for semantic clarity and to avoid a future breaking rename.
- Added `CandidateName` domain model and `extract_name()`, reusing `contact_extractor.py`'s existing email/phone regexes for a defensive check.
- Wired `name: CandidateName` into `PipelineResult`/`process_resume()`.
- Added 7 new extractor unit tests plus assertions in the existing pipeline and API tests — 62/62 total passing.
- Manually verified against the real sample resume — correctly extracted "Manish Kumar Gupta".
- PROJECT_BIBLE synced with repository (version, domain models, design decisions, module status, testing status, verification checklist, session log, TODO/next session, tech debt, interview talking points).

Completed (Session 11)

- Surfaced and resolved four design forks before coding: `raw_text` sourcing, `Candidate` dedup, the `None`-name persistence path, and API response shape.
- Added `raw_text` to `PipelineResult`; introduced `app/backend/api/schemas.py`'s `UploadResumeResponse` (first concrete API schema) to keep it out of the HTTP response while exposing new `resume_id`/`candidate_id` fields.
- Wired `Candidate`/`Resume` persistence into `/upload-resume`, conditional on name extraction succeeding; `Upload` always persists.
- Added/updated tests for all four decisions — 66/66 total passing.
- Manually verified against a live server with the real sample resume: correct IDs returned, `raw_text` absence confirmed via `grep`, correct rows in the real DB.
- PROJECT_BIBLE synced with repository (version, design decisions, module status, testing status, verification checklist, session log, TODO/next session, tech debt, interview talking points).

Completed (Session 12)

- Hand-traced candidate heuristics against the real sample resume before designing — found blank-line segmentation fails entirely, and the real EXPERIENCE section has zero date lines (a genuine stress case).
- Designed and cross-reviewed date-anchored segmentation with ChatGPT, incorporating two requested wording/documentation refinements (implementation-rule framing, one-date-per-entry limitation).
- Implemented `ResumeEntry` + `extract_entries()`, catching a blank-line-before-date edge case during implementation that neither hand-trace nor cross-review had covered.
- Wired `education`/`experience` into `PipelineResult`/`UploadResumeResponse`; deferred DB persistence (no tables exist yet).
- Added 8 new extractor tests (using real hand-traced content as literal test cases) plus new pipeline/API test assertions — 76/76 total passing.
- Manually verified against the real sample resume twice (direct pipeline call, live server) — correct 3-entry EDUCATION segmentation and honest 1-entry EXPERIENCE fallback both times.
- PROJECT_BIBLE synced with repository (version, domain models, design decisions, module status, testing status, verification checklist, session log, TODO/next session, tech debt, interview talking points).

Completed (Session 13)

- Researched before designing: read the frontend scaffold, route stub, and `Job` schema to establish PDF-not-text; read `section_detector.py`'s actual matching logic to find a concrete Education/Experience collision risk with reusing `detect_sections()` on JD content.
- Cross-reviewed the design with ChatGPT (including the collision example); adopted its `parse_job_description()` orchestration-helper suggestion and logged its `clean_text()`-ownership tech debt note.
- Implemented `src/job_pipeline.py`, `UploadJobResponse`, and `POST /upload-job` — persists `Job`+`Upload`, required user-provided title, `PDFParseError` → 422, `description` excluded from the response.
- Added 9 new tests, including the literal collision-case content as a test case — 85/85 total passing.
- Manually verified against a live server with a generated JD PDF containing the exact collision case: confirmed the DB stored "Education"/"Experience" as plain text, not resume sections.
- PROJECT_BIBLE synced with repository (version, design decisions, module status, testing status, verification checklist, session log, TODO/next session, tech debt, interview talking points).

Completed (Session 14)

- Measured the existing Embeddings scaffold before designing — found the project's own "Embedding <1 sec" performance goal was wrong as stated (cold ~22s one-time, warm ~20ms).
- Cross-reviewed with ChatGPT: agreed to defer persistence/route wiring to a future `/rank` milestone; adopted ChatGPT's reframing of resume-embedding-text as a module-boundary question, keeping `src/embeddings/` domain-agnostic.
- Implemented `prepare_resume_embedding_text()` in `src/pipeline.py`, hardened `encoder.py` (return type, docstring with measured timings).
- Attempted a mocked fast-test strategy for the encoder, measured that it didn't work (module-level `sentence_transformers` import defeats mocking), deleted it, and consolidated real-model tests into one `slow`-marked file instead — also caught and fixed a second bug where deselected slow tests still cost ~20s due to a module-level import during collection.
- Added `pytest.ini` (`slow` marker, fast by default); added missing `cosine_similarity()` coverage; added `prepare_resume_embedding_text()` coverage.
- Manually verified against real data: real sample resume's email confirmed absent from embedding text; a domain-matching JD scored meaningfully higher (0.169) than an unrelated one (0.019) via real `encode()` + `cosine_similarity()`.
- PROJECT_BIBLE synced with repository (version, design decisions, module status, testing status, verification checklist, session log, TODO/next session, tech debt, interview talking points, corrected performance table).

Completed (Session 15)

- Identified two real gaps before designing: `ScoreComponents` needs four inputs but only `semantic` is computable; `Score`'s columns are all `NOT NULL` so persisting today would mean fabricating three values. Cross-reviewed with ChatGPT, which agreed on both and specifically argued against a nullable-columns migration as unnecessary churn.
- Implemented shared `build_resume_embedding()`/`build_job_embedding()` helpers per ChatGPT's "pipeline divergence" concern, so `/rank` and any future caller prepare text identically rather than via two independently-maintained paths.
- Implemented `src/ranking.py` (`rank_resumes_against_job()`) and wired `POST /rank`: 404 on missing job, ranks every persisted resume by semantic similarity, sorted descending.
- Found and fixed a real problem neither the design brief nor ChatGPT's review anticipated: wiring `/rank` in would have transitively broken the fast-by-default test suite (Session 14) for tests that never touch `/rank`, since `app.backend.main` now imports the whole embeddings chain. Fixed by making `sentence_transformers`'s import lazy inside `get_model()`.
- Added 10 new tests (109 total: 102 fast, 7 slow) including the project's first genuine whole-system integration test — real upload, real embeddings, real ranking, all composed together.
- Manually verified against a live server with real data: the actual sample resume (genuine ECE background) correctly outranked an unrelated synthetic resume against an electronics-engineer JD (0.189 vs. 0.137); 404 verified live too.
- PROJECT_BIBLE synced with repository (version, design decisions, module status, testing status, verification checklist, session log, TODO/next session, tech debt, interview talking points) — also caught and fixed several stale entries from before this session (outdated route counts, a "No API schemas yet" line that was no longer true).

Completed (Session 16)

- Hand-traced skill extraction against the real sample resume's SKILLS section; chose searching the JD for the candidate's own skills over a curated global dictionary, cross-reviewed and agreed with ChatGPT.
- Empirically verified `\b` vs. lookaround boundary matching against 7 real test cases per ChatGPT's request — found naive `\b` silently fails on C++/C#/.NET, shipped the lookaround fix instead.
- Refactored `src/pipeline.py` to share reconstruction logic (`_reconstruct_sections()`) before adding a second consumer, directly applying Session 15's pipeline-divergence lesson.
- Manually verified against the real sample resume and found a real bug (40 garbage "skills" from an unrecognized "Positions of Responsibility" heading bleeding into SKILLS); fixed via the same `ALIASES` extension mechanism Session 6 established, not a change to the new extractor.
- Wired `skill_score` into `/rank` as an independent field alongside `semantic_score` — not blended, sort order unchanged.
- Added 20 new tests (129 total: 123 fast, 7 slow), including a regression test for the real bug found.
- Manually verified end-to-end against a live server: `skill_score: 0.0` for the real resume against the electronics JD, correctly and honestly reflecting the exact-matching limitation (Verilog≠VHDL) even as `semantic_score` correctly captured the real domain relevance.
- PROJECT_BIBLE synced with repository (version, domain models, design decisions, module responsibilities, module status, testing status, verification checklist, session log, TODO/next session, tech debt, interview talking points) — also corrected a Git Note error caught before it was written (mistakenly assumed a PR had been merged without checking `git log` first).
