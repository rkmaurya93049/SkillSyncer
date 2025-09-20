import streamlit as st

def render_footer():
    st.markdown("""
        <hr style="margin-top: 40px;">
        <div style="text-align: center; font-size: 14px; color: gray;">
            Built with ❤️ by Team Solo Leveler | <a href="https://github.com/rkmaurya93049" target="_blank">GitHub</a>
        </div>
    """, unsafe_allow_html=True)