import streamlit as st

st.set_page_config(page_title="Resume Intelligence Platform", layout="wide")
st.title("Resume Intelligence Platform")

job_description = st.file_uploader("Job description (PDF)", type="pdf")
resumes = st.file_uploader("Resumes (PDF)", type="pdf", accept_multiple_files=True)

if st.button("Rank candidates", disabled=not (job_description and resumes)):
    st.info("Ranking pipeline not implemented yet.")

st.subheader("Results")
st.write("No results yet.")
