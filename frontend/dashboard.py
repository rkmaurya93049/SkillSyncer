import os

import pandas as pd
import requests
import streamlit as st

from components.footer import render_footer
from components.header import render_header

st.set_page_config(page_title="Resume Relevance Checker", layout="wide", page_icon="📄")
render_header()

tab = st.selectbox("🔀 Switch View", ["🎓 Student Portal", "🧑‍💼 Recruiter Dashboard"])

BASE_URL = os.getenv(
    "SKILLSYNCER_API_URL",
    "https://skillsyncer-rkmaurya.hf.space",
).rstrip("/")
REQUEST_TIMEOUT = 90


def _request_json(method: str, path: str, **kwargs):
    try:
        response = requests.request(
            method,
            f"{BASE_URL}{path}",
            timeout=REQUEST_TIMEOUT,
            **kwargs,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        st.error(f"❌ Backend request failed: {exc}")
        return None
    except ValueError:
        st.error("❌ Backend returned a non-JSON response.")
        return None


def analyze_resume(jd_text, jd_file, resume_file):
    files = {
        "resume_file": (resume_file.name, resume_file.getvalue(), resume_file.type),
    }
    if jd_file:
        files["jd_file"] = (jd_file.name, jd_file.getvalue(), jd_file.type)
    else:
        files["jd_file"] = ("jd.txt", (jd_text or "").encode("utf-8"), "text/plain")

    return _request_json("POST", "/evaluate/", files=files)


def fetch_history(params=None):
    return _request_json("GET", "/evaluate/history", params=params) or []


def fetch_detail(result_id):
    return _request_json("GET", f"/evaluate/{result_id}") or {}


if "Student" in tab:
    st.subheader("📄 Resume Relevance Checker")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='upload-box'>📁 Upload Your Resume</div>", unsafe_allow_html=True)
        resume_file = st.file_uploader(
            "",
            type=["pdf", "docx"],
            label_visibility="collapsed",
            key="resume_upload",
        )

    with col2:
        st.markdown("<div class='upload-box'>📝 Job Description</div>", unsafe_allow_html=True)
        jd_mode = st.radio(
            "Choose input method",
            ["Upload JD file", "Paste JD manually"],
            horizontal=True,
        )

        if jd_mode == "Upload JD file":
            jd_file = st.file_uploader(
                "",
                type=["pdf", "docx"],
                label_visibility="collapsed",
                key="jd_upload",
            )
            jd_text = None
        else:
            jd_file = None
            jd_text = st.text_area(
                "Paste JD here",
                height=200,
                placeholder="Paste job description text...",
                key="jd_text",
            )

    if st.button("🚀 Evaluate Resume"):
        if resume_file and (jd_file or (jd_text and jd_text.strip())):
            result = analyze_resume(jd_text, jd_file, resume_file)
            if result:
                st.success(f"✅ Evaluation Complete for {resume_file.name}")
                st.progress(result["score"] / 100, text=f"Score: {result['score']}%")

                verdict = result["verdict"]
                if verdict == "High":
                    st.success("Verdict: High Suitability 👍")
                elif verdict == "Medium":
                    st.warning("Verdict: Medium Suitability 🤔")
                else:
                    st.error("Verdict: Low Suitability 👎")

                suggestions = result.get("suggestions", {})
                st.markdown("### 🔧 Suggestions")
                st.markdown("**Resume Fixes:**")
                for fix in suggestions.get("resume_fixes", []):
                    st.markdown(f"- {fix}")

                st.markdown("**Skills to Add:**")
                for skill in suggestions.get("skills_to_add", []):
                    st.markdown(f"- {skill}")

                st.markdown("**Experience Suggestions:**")
                for exp in suggestions.get("experience_suggestions", []):
                    st.markdown(f"- {exp}")

                if suggestions.get("error"):
                    st.caption("AI suggestions used a fallback because the Gemini service was unavailable.")
        else:
            st.error("Please upload both resume and JD (file or text).")

elif "Recruiter" in tab:
    st.subheader("📊 Recruiter Dashboard")
    st.markdown("View and filter past evaluations.")

    all_data = fetch_history()
    df = pd.DataFrame(all_data)

    if not df.empty:
        search = st.text_input("🔍 Search Resume Filename")
        if search:
            df = df[df["resume_filename"].str.contains(search, case=False, na=False)]

        col1, col2, col3 = st.columns(3)
        with col1:
            verdict = st.selectbox("Verdict", ["All"] + sorted(df["verdict"].dropna().unique()))
        with col2:
            min_score, max_score = st.slider("Score Range", 0, 100, (0, 100))
        with col3:
            jd_title = st.selectbox("JD Title", ["All"] + sorted(df["jd_title"].dropna().unique()))

        filtered = df[df["score"].between(min_score, max_score)]
        if verdict != "All":
            filtered = filtered[filtered["verdict"] == verdict]
        if jd_title != "All":
            filtered = filtered[filtered["jd_title"] == jd_title]

        def verdict_color(val):
            if val == "High":
                return "background-color: #d1fae5; color: #065f46"
            if val == "Medium":
                return "background-color: #fef3c7; color: #92400e"
            if val == "Low":
                return "background-color: #fee2e2; color: #991b1b"
            return ""

        styled_df = filtered.style.applymap(verdict_color, subset=["verdict"])

        st.markdown("### 📁 Filtered Evaluations")
        st.dataframe(styled_df, use_container_width=True)

        if not filtered.empty:
            st.markdown("### 🔍 Detailed Evaluation")
            selected_id = st.selectbox("Select Evaluation ID", filtered["id"].tolist())
            if selected_id is not None:
                detail = fetch_detail(selected_id)
                if detail:
                    st.metric("Score", f"{detail['score']}%", delta=f"{detail['verdict']} Fit")

                    st.markdown("**Missing Must-Have Skills:**")
                    for skill in detail.get("missing_skills", []):
                        st.markdown(f"- {skill}")

                    st.markdown("**Suggestions:**")
                    feedback = detail.get("feedback", "")
                    if feedback:
                        for fix in feedback.split("\n"):
                            if fix.strip():
                                st.markdown(f"- {fix}")
                    else:
                        st.info("No detailed resume-fix suggestions were stored for this evaluation.")
        else:
            st.info("No evaluations match the selected filters.")
    else:
        st.info("No evaluations found.")

render_footer()
