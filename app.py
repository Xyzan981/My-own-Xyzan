import streamlit as st
from groq import Groq
import re
import json
from datetime import datetime

st.set_page_config(
    page_title="Xyzan AI",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #020617, #0f172a, #111827);
    color: white;
}
.block-container {
    padding-top: 2rem;
}
[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.97);
}
textarea {
    border-radius: 18px !important;
}
.big-title {
    font-size: 44px;
    font-weight: 900;
}
.card {
    padding: 20px;
    border-radius: 24px;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.15);
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "workspace_code" not in st.session_state:
    st.session_state.workspace_code = ""

if "ai_latest_code" not in st.session_state:
    st.session_state.ai_latest_code = ""

if "project_name" not in st.session_state:
    st.session_state.project_name = "Xyzan Project"

def extract_code(text):
    match = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

def get_client():
    try:
        return Groq(api_key=st.secrets["GROQ_API_KEY"])
    except Exception:
        return None

client = get_client()

st.markdown('<div class="big-title">⚡ Xyzan AI Dashboard</div>', unsafe_allow_html=True)
st.caption("AI coding sandbox powered by Groq")

st.sidebar.title("⚙️ Settings")

st.session_state.project_name = st.sidebar.text_input(
    "Project Name",
    st.session_state.project_name
)

model = st.sidebar.selectbox(
    "Model",
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
        "Create new feature",
        "Make full app better"
    ]
)

temperature = st.sidebar.slider("Creativity", 0.0, 1.0, 0.35)

if client:
    st.sidebar.success("Groq Live Mode: ON")
else:
    st.sidebar.error("Missing GROQ_API_KEY")

st.sidebar.divider()

if st.sidebar.button("🧹 Reset Everything"):
    st.session_state.messages = []
    st.session_state.workspace_code = ""
    st.session_state.ai_latest_code = ""
    st.rerun()

export_data = {
    "project_name": st.session_state.project_name,
    "workspace_code": st.session_state.workspace_code,
    "messages": st.session_state.messages,
    "saved_at": str(datetime.now())
}

st.sidebar.download_button(
    "📦 Export Project JSON",
    data=json.dumps(export_data, indent=2),
    file_name="xyzan_project.json",
    mime="application/json"
)

col1, col2 = st.columns([1.15, 1])

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📝 Creative Sandbox")

    st.session_state.workspace_code = st.text_area(
        "Code Editor",
        value=st.session_state.workspace_code,
        height=520,
        placeholder="Paste your Python / Streamlit code here..."
    )

    user_request = st.text_input(
        "Ask Xyzan",
        placeholder="Example: fix this and make the UI look premium"
    )

    b1, b2, b3 = st.columns(3)

    run_ai = b1.button("🚀 Run AI", use_container_width=True)

    apply_code = b2.button("⚡ Apply Code", use_container_width=True)

    clear_code = b3.button("🧹 Clear", use_container_width=True)

    if apply_code:
        if st.session_state.ai_latest_code:
            st.session_state.workspace_code = st.session_state.ai_latest_code
            st.success("AI code applied to workspace.")
            st.rerun()
        else:
            st.warning("No AI code found yet.")

    if clear_code:
        st.session_state.workspace_code = ""
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🤖 Xyzan AI Output")

    if run_ai:
        if not client:
            st.error("Add GROQ_API_KEY in Streamlit Secrets first.")
        else:
            if not user_request.strip():
                user_request = "Analyze, fix, and improve this code."

            full_prompt = f"""
You are Xyzan AI, a senior software architect and elite coding assistant.

Project name: {st.session_state.project_name}

Selected action: {action}

Current code:
{st.session_state.workspace_code}

User request:
{user_request}

Rules:
- Be direct.
- Improve the code professionally.
- If code is needed, return the COMPLETE fixed app.py inside ONE Python code block.
- Do not leave missing parts.
- Do not use fake imports.
- Make it Streamlit compatible.
"""

            with st.spinner("Xyzan AI is thinking..."):
                try:
                    response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are Xyzan AI, a professional coding assistant."
                            },
                            {
                                "role": "user",
                                "content": full_prompt
                            }
                        ],
                        temperature=temperature,
                        max_tokens=4096
                    )

                    ai_text = response.choices[0].message.content

                    st.session_state.messages.append(("user", user_request))
                    st.session_state.messages.append(("assistant", ai_text))

                    extracted = extract_code(ai_text)
                    if extracted:
                        st.session_state.ai_latest_code = extracted

                except Exception as e:
                    st.error(f"Groq error: {e}")

    if st.session_state.messages:
        for role, msg in st.session_state.messages[-8:]:
            with st.chat_message(role):
                st.markdown(msg)
    else:
        st.info("Ask Xyzan to fix, optimize, or create code.")

    st.markdown("</div>", unsafe_allow_html=True)

st.divider()
st.caption("Xyzan AI v2 — Streamlit + Groq")
