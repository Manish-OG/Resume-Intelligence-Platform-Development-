import httpx
import streamlit as st

from app.frontend.config import BACKEND_URL

UPLOAD_TIMEOUT_SECONDS = 30.0
# Generous: a fresh backend process's first /rank call pays a one-time
# ~22s cold model-load cost (measured, see PROJECT_BIBLE.md Section 19)
# on top of actual ranking work.
RANK_TIMEOUT_SECONDS = 120.0


class APIError(Exception):
    """Raised when the backend returns a non-2xx response."""

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"{status_code}: {detail}")


def _raise_for_status(response: httpx.Response) -> None:
    if response.is_success:
        return
    try:
        detail = response.json().get("detail", response.text)
    except ValueError:
        detail = response.text
    raise APIError(response.status_code, detail)


def upload_job(client: httpx.Client, title: str, file_name: str, file_bytes: bytes) -> dict:
    response = client.post(
        "/upload-job",
        data={"title": title},
        files={"file": (file_name, file_bytes, "application/pdf")},
    )
    _raise_for_status(response)
    return response.json()


def upload_resume(client: httpx.Client, file_name: str, file_bytes: bytes) -> dict:
    response = client.post(
        "/upload-resume",
        files={"file": (file_name, file_bytes, "application/pdf")},
    )
    _raise_for_status(response)
    return response.json()


def rank(client: httpx.Client, job_id: int) -> dict:
    response = client.post("/rank", params={"job_id": job_id})
    _raise_for_status(response)
    return response.json()


def _render_candidate(assessment: dict) -> None:
    ranking = assessment["ranking"]
    feedback = assessment["feedback"]

    with st.container(border=True):
        name_col, score_col = st.columns([3, 1])
        name_col.markdown(f"**{ranking['candidate_name'] or 'Unnamed candidate'}**")
        score_col.metric("Final Score", f"{ranking['final_score']:.2f}")

        with st.expander("Details"):
            st.write(feedback["recommendation"])

            score_cols = st.columns(4)
            score_cols[0].metric("Semantic", f"{ranking['semantic_score']:.2f}")
            score_cols[1].metric("Skill", f"{ranking['skill_score']:.2f}")
            score_cols[2].metric("Experience", f"{ranking['experience_score']:.2f}")
            score_cols[3].metric("Education", f"{ranking['education_score']:.2f}")

            if feedback["strengths"]:
                st.markdown("**Strengths**")
                for item in feedback["strengths"]:
                    st.markdown(f"- {item}")

            if feedback["weaknesses"]:
                st.markdown("**Weaknesses**")
                for item in feedback["weaknesses"]:
                    st.markdown(f"- {item}")

            # None means "not computed" (Section 11) — distinct from an
            # empty list, which would claim "checked, nothing missing".
            if feedback["missing_skills"] is not None:
                st.markdown("**Missing skills**")
                for item in feedback["missing_skills"]:
                    st.markdown(f"- {item}")


def _render_results(rank_response: dict | None) -> None:
    if not rank_response or not rank_response["candidates"]:
        st.write("No results yet.")
        return

    for assessment in rank_response["candidates"]:
        _render_candidate(assessment)


def render() -> None:
    st.set_page_config(page_title="Resume Intelligence Platform", layout="wide")
    st.title("Resume Intelligence Platform")

    st.session_state.setdefault("job_id", None)
    st.session_state.setdefault("uploaded_resumes", [])
    st.session_state.setdefault("rank_response", None)

    job_title = st.text_input("Job title")
    job_description = st.file_uploader("Job description (PDF)", type="pdf")
    resumes = st.file_uploader("Resumes (PDF)", type="pdf", accept_multiple_files=True)

    upload_disabled = not (job_title and job_description and resumes)
    if st.button("Upload", disabled=upload_disabled):
        with httpx.Client(base_url=BACKEND_URL, timeout=UPLOAD_TIMEOUT_SECONDS) as client:
            try:
                job_result = upload_job(
                    client, job_title, job_description.name, job_description.getvalue()
                )
            except APIError as exc:
                st.error(f"Job upload failed: {exc.detail}")
            else:
                st.session_state.job_id = job_result["job_id"]
                st.session_state.rank_response = None
                uploaded, failures = [], []

                for resume_file in resumes:
                    try:
                        resume_result = upload_resume(
                            client, resume_file.name, resume_file.getvalue()
                        )
                    except APIError as exc:
                        failures.append((resume_file.name, exc.detail))
                    else:
                        uploaded.append(resume_result)

                st.session_state.uploaded_resumes = uploaded
                st.success(
                    f'Uploaded job "{job_result["title"]}" and '
                    f"{len(uploaded)} of {len(resumes)} resume(s)."
                )
                for file_name, detail in failures:
                    st.warning(f"Skipped {file_name}: {detail}")

    if st.session_state.job_id is not None:
        st.caption(
            f"Job ID {st.session_state.job_id} — "
            f"{len(st.session_state.uploaded_resumes)} resume(s) uploaded and ready to rank."
        )

    st.subheader("Ranking")
    st.caption(
        "The first ranking after a backend restart can take 20-30 seconds while the "
        "AI model loads. Rankings after that are fast."
    )
    rank_disabled = not (st.session_state.job_id and st.session_state.uploaded_resumes)
    if st.button("Rank candidates", disabled=rank_disabled):
        with st.spinner(
            "Ranking candidates — this may take up to 30 seconds on the first "
            "run while the AI model loads..."
        ):
            with httpx.Client(base_url=BACKEND_URL, timeout=RANK_TIMEOUT_SECONDS) as client:
                try:
                    st.session_state.rank_response = rank(client, st.session_state.job_id)
                except APIError as exc:
                    st.error(f"Ranking failed: {exc.detail}")

    st.subheader("Results")
    _render_results(st.session_state.rank_response)


if __name__ == "__main__":
    render()
