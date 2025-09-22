import streamlit as st
import pandas as pd
import requests
from components.header import render_header
from components.footer import render_footer

# --- Page Setup ---
st.set_page_config(page_title="Resume Relevance Checker", layout="wide", page_icon="📄")

# --- Branding ---
render_header()

# --- Logo + Tagline ---


# --- View Selector ---
tab = st.selectbox("🔀 Switch View", ["🎓 Student Portal", "🧑‍💼 Recruiter Dashboard"])

# --- Backend URL ---
BBASE_URL = "http://0.0.0.0:7860"




def analyze_resume(jd_text, jd_file, resume_file):
    files = {
        "resume_file": (resume_file.name, resume_file.getvalue(), resume_file.type)
    }
    if jd_file:
        files["jd_file"] = (jd_file.name, jd_file.getvalue(), jd_file.type)
    else:
        files["jd_file"] = ("jd.txt", jd_text.encode("utf-8"), "text/plain")
    return requests.post(f"{BASE_URL}/evaluate/", files=files).json()

def fetch_history(params=None):
    return requests.get(f"{BASE_URL}/evaluate/history", params=params).json()

def fetch_detail(result_id):
    return requests.get(f"{BASE_URL}/evaluate/{result_id}").json()

def fetch_history(params=None):
    try:
        response = requests.get(f"{BASE_URL}/history", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"❌ Failed to fetch history: {e}")
        return []

def fetch_detail(result_id):
    try:
        response = requests.get(f"{BASE_URL}/{result_id}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"❌ Failed to fetch detail: {e}")
        return {}

# --- Student Portal ---
if "Student" in tab:
    st.subheader("📄 Resume Relevance Checker")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='upload-box'>📁 Upload Your Resume</div>", unsafe_allow_html=True)
        resume_file = st.file_uploader("", type=["pdf", "docx"], label_visibility="collapsed", key="resume_upload")

    with col2:
        st.markdown("<div class='upload-box'>📝 Job Description</div>", unsafe_allow_html=True)
        jd_mode = st.radio("Choose input method", ["Upload JD file", "Paste JD manually"], horizontal=True)

        if jd_mode == "Upload JD file":
            jd_file = st.file_uploader("", type=["pdf", "docx"], label_visibility="collapsed", key="jd_upload")
            jd_text = None
        else:
            jd_file = None
            jd_text = st.text_area("Paste JD here", height=200, placeholder="Paste job description text...", key="jd_text")

    if st.button("🚀 Evaluate Resume"):
        if resume_file and (jd_file or jd_text):
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

                st.markdown("### 🔧 Suggestions")
                st.markdown("**Resume Fixes:**")
                for fix in result["suggestions"]["resume_fixes"]:
                    st.markdown(f"- {fix}")
                st.markdown("**Skills to Add:**")
                for skill in result["suggestions"]["skills_to_add"]:
                    st.markdown(f"- {skill}")
                st.markdown("**Experience Suggestions:**")
                for exp in result["suggestions"]["experience_suggestions"]:
                    st.markdown(f"- {exp}")
        else:
            st.error("Please upload both resume and JD (file or text).")

# --- Recruiter Dashboard ---
elif "Recruiter" in tab:
    st.subheader("📊 Recruiter Dashboard")
    st.markdown("View and filter past evaluations.")

    all_data = fetch_history()
    df = pd.DataFrame(all_data)

    if not df.empty:
        search = st.text_input("🔍 Search Resume Filename")
        if search:
            df = df[df["resume_filename"].str.contains(search, case=False)]

        col1, col2, col3 = st.columns(3)
        with col1:
            verdict = st.selectbox("Verdict", ["All"] + sorted(df["verdict"].unique()))
        with col2:
            min_score, max_score = st.slider("Score Range", 0, 100, (0, 100))
        with col3:
            jd_title = st.selectbox("JD Title", ["All"] + sorted(df["jd_title"].unique()))

        filtered = df[
            df["score"].between(min_score, max_score) &
            (df["verdict"] == verdict if verdict != "All" else True) &
            (df["jd_title"] == jd_title if jd_title != "All" else True)
        ]

        def verdict_color(val):
            if val == "High":
                return "background-color: #d1fae5; color: #065f46"
            elif val == "Medium":
                return "background-color: #fef3c7; color: #92400e"
            elif val == "Low":
                return "background-color: #fee2e2; color: #991b1b"
            return ""

        styled_df = filtered.style.applymap(verdict_color, subset=["verdict"]) \
            .set_properties(**{
                "background-color": "#f3f4f6",
                "color": "#1f2937",
                "border": "1px solid #ddd"
            })

        st.markdown("### 📁 Filtered Evaluations")
        st.dataframe(styled_df, use_container_width=True)

        st.markdown("### 🔍 Detailed Evaluation")
        selected_id = st.selectbox("Select Evaluation ID", filtered["id"])
        if selected_id:
            detail = fetch_detail(selected_id)
            st.metric("Score", f"{detail['score']}%", delta=f"{detail['verdict']} Fit")

            st.markdown("**Missing Must-Have Skills:**")
            for skill in detail["missing_skills"]:
                st.markdown(f"- {skill}")

            st.markdown("**Suggestions:**")
            for fix in detail["feedback"].split("\n"):
                st.markdown(f"- {fix}")
    else:
        st.info("No evaluations found.")

# --- Footer ---
render_footer()






