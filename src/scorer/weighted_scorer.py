from dataclasses import dataclass

DEFAULT_WEIGHTS = {"semantic": 0.5, "skills": 0.3, "experience": 0.1, "education": 0.1}


@dataclass
class ScoreComponents:
    semantic: float
    skills: float
    experience: float
    education: float


def compute_score(components: ScoreComponents, weights: dict = None) -> float:
    weights = weights or DEFAULT_WEIGHTS
    return (
        components.semantic * weights["semantic"]
        + components.skills * weights["skills"]
        + components.experience * weights["experience"]
        + components.education * weights["education"]
    )
