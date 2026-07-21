from dataclasses import dataclass

from src.models import ResumeEntry, ResumeSkills
from src.scorer.education_matcher import describe_education_match
from src.scorer.experience_matcher import describe_experience_match
from src.scorer.skill_matcher import matched_skills


@dataclass(frozen=True)
class GeneratedFeedback:
    """
    Human-readable explanation of one candidate's match against one
    job — the output of generate_feedback().

    Named GeneratedFeedback, not Feedback, to avoid colliding with
    src/database/models.py's Feedback (the persistence model) — the
    two need to coexist wherever both are imported (Session 22).

    missing_skills is None, not [], whenever it hasn't been computed
    (currently: always) — an empty list would assert "checked, found
    nothing missing," which isn't true; None honestly means "not
    computed." Answering it for real needs independent JD-skill
    extraction, which this project has no real JD corpus to validate
    a heuristic against (same constraint that blocked JD title
    extraction and JD section detection). See PROJECT_BIBLE.md
    Section 11/18.
    """

    strengths: list[str]
    weaknesses: list[str]
    missing_skills: list[str] | None
    recommendation: str


def generate_feedback(
    resume_skills: ResumeSkills,
    education_entries: tuple[ResumeEntry, ...],
    experience_entries: tuple[ResumeEntry, ...],
    job_description: str,
) -> GeneratedFeedback:
    """
    Explain one candidate's match against one job description.

    Pairwise and pure, deliberately mirroring compute_skill_score()/
    compute_education_score()/compute_experience_score()'s own shape
    (resume-side data + job_description in, one result out) — feedback
    for one candidate never depends on any other candidate's data, so
    there's no reason for its signature to look like rank_resumes_
    against_job()'s. Not called from there either: ranking and
    explanation are different responsibilities (Section 7), kept
    separate. Never raises.

    strengths/weaknesses are built from the same intermediate detail
    the scorer modules already compute internally but previously
    discarded (describe_education_match(), describe_experience_match(),
    matched_skills()) — reused here rather than reimplemented, so
    there's exactly one matching implementation per signal, not two
    that could silently drift apart (Section 11).

    recommendation is not a new, separately-calibrated signal: it's a
    plain-language sentence composed from the same facts strengths/
    weaknesses are built from. Deliberately not a rank-position or
    score-threshold label — both were considered and rejected during
    design (Section 11): absolute thresholds have no real calibration
    data behind them, and rank position among a candidate pool
    discards score magnitude (a near-tie and a landslide can produce
    the same "#1 of 2").
    """

    strengths: list[str] = []
    weaknesses: list[str] = []
    recommendation_parts: list[str] = []

    candidate_level, required_level = describe_education_match(
        education_entries, job_description
    )
    if candidate_level > 0 and required_level > 0:
        if candidate_level >= required_level:
            msg = "Meets the stated education requirement."
            strengths.append(msg)
            recommendation_parts.append(msg)
        else:
            msg = "Education level is below the JD's stated requirement."
            weaknesses.append(msg)
            recommendation_parts.append(msg)
    elif required_level > 0 and candidate_level == 0:
        msg = "No recognized degree found in the Education section."
        weaknesses.append(msg)
        recommendation_parts.append(
            "Education requirement could not be confirmed: no recognized degree found."
        )

    total_years, required_years, any_parseable_dates = describe_experience_match(
        experience_entries, job_description
    )
    if required_years > 0:
        if not any_parseable_dates:
            msg = (
                "The Experience section doesn't include date ranges we could parse, "
                "so experience duration couldn't be verified."
            )
            weaknesses.append(msg)
            recommendation_parts.append("Experience duration could not be verified.")
        elif total_years >= required_years:
            msg = f"Meets the stated experience requirement ({total_years:g}+ years found)."
            strengths.append(msg)
            recommendation_parts.append(msg)
        else:
            msg = f"{total_years:g} years of experience found vs. {required_years} required."
            weaknesses.append(msg)
            recommendation_parts.append(msg)

    matched = matched_skills(resume_skills, job_description)
    if matched:
        msg = f"Matches skills mentioned in the job description: {', '.join(matched)}."
        strengths.append(msg)
        recommendation_parts.append(f"Matches {len(matched)} skill(s) from the JD.")

    recommendation = (
        " ".join(recommendation_parts)
        if recommendation_parts
        else "No comparable requirements were found in the job description to assess."
    )

    return GeneratedFeedback(
        strengths=strengths,
        weaknesses=weaknesses,
        missing_skills=None,
        recommendation=recommendation,
    )
