import streamlit as st
from groq import Groq

st.set_page_config(page_title="Xyzan AI", page_icon="⚡", layout="wide")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #020617, #0f172a, #111827);
    color: white;
}
.block-container {
    padding-top: 2rem;
}
textarea {
    border-radius: 18px !important;
}
[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.95);
}
.big-title {
    font-size: 42px;
    font-weight: 900;
}
.glass {
    padding: 18px;
    border-radius: 22px;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.15);
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">⚡ Xyzan AI Dashboard</div>', unsafe_allow_html=True)
st.caption("Your own AI coding sandbox powered by Groq")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "workspace_code" not in st.session_state:
    st.session_state.workspace_code = ""

if "ai_latest_code" not in st.session_state:
    st.session_state.ai_latest_code = ""

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    api_ready = True
except Exception:
    client = None
    api_ready = False

st.sidebar.title("⚙️ Settings")

model = st.sidebar.selectbox(
    "AI Model",
    [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant"
    ]
)

action = st.sidebar.selectbox(
    "AI Action",
    [
        "Fix bugs",
        "Optimize code",
        "Explain code",
        "Improve UI",
        "Add comments",
        "Find security issues",
        "Rewrite cleaner",
        "Create new feature"
    ]
)

temperature = st.sidebar.slider("Creativity", 0.0, 1.0, 0.35)

if api_ready:
    st.sidebar.success("Groq Live Mode: ON")
else:
    st.sidebar.error("Add GROQ_API_KEY in Streamlit Secrets")

col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("📝 Creative Sandbox")

    st.session_state.workspace_code = st.text_area(
        "Paste or write your code here",
        value=st.session_state.workspace_code,
        height=500
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        run_ai = st.button("🚀 Run Xyzan AI", use_container_width=True)

    with c2:
        if st.button("⚡ Apply AI Code", use_container_width=True):
            if st.session_state.ai_latest_code:
                st.session_state.workspace_code = st.session_state.ai_latest_code
                st.rerun()
            else:
                st.warning("No AI code found yet.")

    with c3:
        if st.button("🧹 Clear", use_container_width=True):
            st.session_state.workspace_code = ""
            st.session_state.messages = []
            st.session_state.ai_latest_code = ""
            st.rerun()

    user_request = st.text_input("Ask Xyzan what to do", placeholder="Example: fix this code and make it cleaner")

with col2:
    st.subheader("🤖 AI Output")

    if run_ai:
        if not api_ready:
            st.error("You need to add your Groq API key in Streamlit Secrets.")
        else:
            if not user_request:
                user_request = "Analyze this code and improve it."

            full_prompt = f"""
You are Xyzan AI, a senior software architect and elite coding assistant.

Your job:
- Help build a professional developer productivity SaaS.
- Give clean, working code.
- If fixing code, return the full improved code.
- If you provide code, put it in ONE python code block.
- Keep explanations short and useful.

Action selected: {action}

Current workspace code:
```python
{st.session_state.workspace_code}
