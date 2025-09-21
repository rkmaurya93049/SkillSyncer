import streamlit as st

def render_header():
    st.markdown("""
        <style>
        .app-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #1f1f2e;
            padding: 15px 30px;
            border-radius: 8px;
            color: white;
            font-family: 'Segoe UI', sans-serif;
            margin-bottom: 20px;
        }
        .app-bar h1 {
            margin: 0;
            font-size: 24px;
        }
        .app-bar .nav-links a {
            margin-left: 20px;
            color: #9ca3af;
            text-decoration: none;
            font-weight: bold;
        }
        .app-bar .nav-links a:hover {
            color: #ffffff;
        }
        </style>

        <div class="app-bar">
            <h1>🚀 SkillSyncer Dashboard — Team Solo Leveler</h1>
            <div class="nav-links">
                <a href="https://www.linkedin.com/in/raushan-kumar-74209b253/" target="_blank">LinkedIn</a>
                <a href="https://github.com/rkmaurya93049" target="_blank">GitHub</a>
                <a href="https://www.kaggle.com/rkmaurya93" target="_blank">Kaggle</a>
            </div>
        </div>
    """, unsafe_allow_html=True)


