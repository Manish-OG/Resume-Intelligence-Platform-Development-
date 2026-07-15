from dataclasses import dataclass, field


@dataclass
class Feedback:
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    recommendation: str = ""


def generate_feedback(matched_skills: list[str], missing_skills: list[str], score: float) -> Feedback:
    strengths = [f"Matches required skill: {s}" for s in matched_skills]
    weaknesses = [f"Missing skill: {s}" for s in missing_skills]
    if score >= 0.75:
        recommendation = "Strong match"
    elif score >= 0.5:
        recommendation = "Possible match"
    else:
        recommendation = "Weak match"
    return Feedback(strengths, weaknesses, missing_skills, recommendation)
