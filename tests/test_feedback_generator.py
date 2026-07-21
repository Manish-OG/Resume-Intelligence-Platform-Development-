from src.feedback.generator import GeneratedFeedback, generate_feedback
from src.models import ResumeEntry, ResumeSkills


def _entry(title, dates, details):
    return ResumeEntry(title=title, dates=dates, details=details)


def test_generate_feedback_missing_skills_is_none_not_empty_list():
    fb = generate_feedback(ResumeSkills(skills=()), (), (), "anything")

    assert fb.missing_skills is None


def test_generate_feedback_education_strength_when_requirement_met():
    education = (_entry("State University", "2015 - 2019", "Bachelor of Science"),)
    fb = generate_feedback(ResumeSkills(skills=()), education, (), "Bachelor's degree required")

    assert "Meets the stated education requirement." in fb.strengths
    assert fb.weaknesses == []


def test_generate_feedback_education_weakness_when_no_degree_found():
    education = (_entry("Central High School", "2018", "Senior Secondary (CBSE)"),)
    fb = generate_feedback(ResumeSkills(skills=()), education, (), "Bachelor's degree required")

    assert any("No recognized degree" in w for w in fb.weaknesses)
    assert fb.strengths == []


def test_generate_feedback_no_education_claim_when_jd_states_no_requirement():
    education = (_entry("State University", "2015 - 2019", "Bachelor of Science"),)
    fb = generate_feedback(ResumeSkills(skills=()), education, (), "Looking for a great engineer")

    assert fb.strengths == []
    assert fb.weaknesses == []


def test_generate_feedback_experience_weakness_honestly_says_unparseable_not_insufficient():
    # The real sample resume's actual EXPERIENCE case (Session 18):
    # zero standalone date lines. The text must not claim "insufficient
    # experience" — that overclaims what the data actually shows.
    experience = (ResumeEntry(title=None, dates=None, details="Did some work."),)
    fb = generate_feedback(
        ResumeSkills(skills=()), (), experience, "3+ years of experience required"
    )

    assert any("date ranges we could parse" in w for w in fb.weaknesses)
    assert not any("insufficient" in w.lower() for w in fb.weaknesses)


def test_generate_feedback_experience_strength_when_requirement_met():
    experience = (_entry("Acme Corp", "2015 - 2023", "Built things."),)
    fb = generate_feedback(
        ResumeSkills(skills=()), (), experience, "3+ years of experience required"
    )

    assert any("Meets the stated experience requirement" in s for s in fb.strengths)


def test_generate_feedback_experience_weakness_quantified_when_below_requirement():
    experience = (_entry("Acme Corp", "2021 - 2023", "Built things."),)
    fb = generate_feedback(
        ResumeSkills(skills=()), (), experience, "5 years of experience required"
    )

    assert any("2 years of experience found vs. 5 required" in w for w in fb.weaknesses)


def test_generate_feedback_skill_strength_lists_matched_skills():
    skills = ResumeSkills(skills=("Python", "SQL", "COBOL"))
    fb = generate_feedback(skills, (), (), "Looking for a Python and SQL developer")

    assert any("Python" in s and "SQL" in s for s in fb.strengths)


def test_generate_feedback_no_skill_claim_when_nothing_matches():
    skills = ResumeSkills(skills=("COBOL",))
    fb = generate_feedback(skills, (), (), "Looking for a Python developer")

    assert fb.strengths == []


def test_generate_feedback_recommendation_composed_from_same_facts_not_a_new_claim():
    education = (_entry("State University", "2015 - 2019", "Bachelor of Science"),)
    fb = generate_feedback(ResumeSkills(skills=()), education, (), "Bachelor's degree required")

    assert "Meets the stated education requirement." in fb.recommendation


def test_generate_feedback_recommendation_honest_default_when_nothing_comparable():
    fb = generate_feedback(ResumeSkills(skills=()), (), (), "Looking for a great engineer")

    assert fb.strengths == []
    assert fb.weaknesses == []
    assert fb.recommendation != ""


def test_generate_feedback_real_sample_resume_against_real_electronics_jd():
    # Hand-traced against the real sample resume, the same JD used in
    # every prior session's live-server verification.
    from src.extraction.skills_extractor import extract_skills
    from src.models import SectionType
    from src.pipeline import process_resume

    result = process_resume("samples/Manish_ResumeDA01.pdf")
    skills_section = next(
        s for s in result.sections.sections if s.section_type == SectionType.SKILLS
    )
    resume_skills = extract_skills(skills_section)
    jd = (
        "Looking for an electronics engineer with 2+ years of experience. "
        "Bachelor degree in Electronics or related field required."
    )

    fb = generate_feedback(resume_skills, result.education, result.experience, jd)

    assert fb.strengths == ["Meets the stated education requirement."]
    assert len(fb.weaknesses) == 1
    assert "date ranges we could parse" in fb.weaknesses[0]
    assert "insufficient" not in fb.weaknesses[0].lower()
    assert fb.missing_skills is None


def test_generated_feedback_is_frozen():
    fb = generate_feedback(ResumeSkills(skills=()), (), (), "anything")

    try:
        fb.recommendation = "changed"
        assert False, "GeneratedFeedback should be immutable"
    except AttributeError:
        pass


def test_generated_feedback_type_name():
    assert GeneratedFeedback.__name__ == "GeneratedFeedback"
