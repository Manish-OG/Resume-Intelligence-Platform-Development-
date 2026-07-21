import csv
import io

from src.export.csv_exporter import export_ranked_candidates_to_csv
from src.ranking import RankedCandidate


def _candidate(**overrides):
    defaults = dict(
        resume_id=1,
        candidate_id=1,
        candidate_name="Jane Doe",
        semantic_score=0.5,
        skill_score=0.5,
        experience_score=0.5,
        education_score=0.5,
        final_score=0.5,
    )
    defaults.update(overrides)
    return RankedCandidate(**defaults)


def test_export_empty_list_returns_header_only_csv():
    text = export_ranked_candidates_to_csv([])

    reader = csv.DictReader(io.StringIO(text))
    assert reader.fieldnames == [
        "resume_id",
        "candidate_id",
        "candidate_name",
        "semantic_score",
        "skill_score",
        "experience_score",
        "education_score",
        "final_score",
    ]
    assert list(reader) == []


def test_export_known_input_round_trips_correctly():
    candidates = [_candidate(candidate_name="Jane Doe", final_score=0.9)]

    text = export_ranked_candidates_to_csv(candidates)

    rows = list(csv.DictReader(io.StringIO(text)))
    assert len(rows) == 1
    assert rows[0]["candidate_name"] == "Jane Doe"
    assert rows[0]["final_score"] == "0.9"
    assert rows[0]["resume_id"] == "1"


def test_export_preserves_row_order():
    candidates = [
        _candidate(candidate_name="First", final_score=0.9),
        _candidate(candidate_name="Second", final_score=0.1),
    ]

    text = export_ranked_candidates_to_csv(candidates)

    rows = list(csv.DictReader(io.StringIO(text)))
    assert [r["candidate_name"] for r in rows] == ["First", "Second"]


def test_export_extra_columns_applied_to_every_row_and_placed_first():
    candidates = [_candidate(candidate_name="A"), _candidate(candidate_name="B")]

    text = export_ranked_candidates_to_csv(candidates, extra_columns={"job_id": 42})

    reader = csv.DictReader(io.StringIO(text))
    assert reader.fieldnames[0] == "job_id"
    rows = list(reader)
    assert rows[0]["job_id"] == "42"
    assert rows[1]["job_id"] == "42"


def test_export_no_extra_columns_omits_job_id_field_entirely():
    text = export_ranked_candidates_to_csv([_candidate()])

    reader = csv.DictReader(io.StringIO(text))
    assert "job_id" not in reader.fieldnames
