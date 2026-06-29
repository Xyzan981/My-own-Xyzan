import streamlit as st
from groq import Groq
import re
import json
from datetime import datetime

st.set_page_config(page_title="Xyzan AI", page_icon="⚡", layout="wide")

THEMES = {
    "Neon Purple": ["#080014", "#16002b", "#7c3aed", "#22d3ee"],
    "Cyber Blue": ["#020617", "#0f172a", "#2563eb", "#38bdf8"],
    "Matrix Green": ["#020b05", "#052e16", "#22c55e", "#86efac"],
    "Fire Red": ["#140202", "#2b0505", "#ef4444", "#f97316"],
    "Ice White": ["#e5e7eb", "#f8fafc", "#2563eb", "#0f172a"],
}

if "messages" not in st.session_state:
    st.session_state.messages = []
if "workspace_code" not in st.session_state:
    st.session_state.workspace_code = ""
if "ai_latest_code" not in st.session_state:
    st.session_state.ai_latest_code = ""
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "dev_mode" not in st.session_state:
    st.session_state.dev_mode = False

st.sidebar.title("⚡ Xyzan Control")

api_input = st.sidebar.text_input(
    "Groq API Key",
    type="password",
    placeholder="Paste gsk_ key here"
)

if api_input:
    st.session_state.api_key = api_input

theme_name = st.sidebar.selectbox("Theme", list(THEMES.keys()))
bg1, bg2, accent, glow = THEMES[theme_name]

mode = st.sidebar.selectbox("Mode", ["Normal Chat", "Coding Sandbox", "Developer Mode"])
st.session_state.dev_mode = mode == "Developer Mode"

model_preset = st.sidebar.selectbox(
    "Model",
    [
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
        "Custom"
    ]
)

custom_model = st.sidebar.text_input("Custom model name", placeholder="Only if Custom selected")
model = custom_model if model_preset == "Custom" and custom_model else model_preset

temperature = st.sidebar.slider("Creativity", 0.0, 1.2, 0.45)

action = st.sidebar.selectbox(
    "Coding Action",
    [
        "Fix bugs",
        "Optimize code",
        "Explain code",
        "Add new feature",
        "Improve UI",
        "Make it cleaner",
        "Find security issues",
        "Full upgrade"
    ]
)

st.markdown(f"""
<style>
@keyframes float {{
    0% {{ transform: translateY(0px); }}
    50% {{ transform: translateY(-10px); }}
    100% {{ transform: translateY(0px); }}
}}

@keyframes glow {{
    0% {{ box-shadow: 0 0 18px {accent}; }}
    50% {{ box-shadow: 0 0 40px {glow}; }}
    100% {{ box-shadow: 0 0 18px {accent}; }}
}}

@keyframes fade {{
    from {{ opacity: 0; transform: translateY(15px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

.stApp {{
    background:
        radial-gradient(circle at top left, {accent}55, transparent 30%),
        linear-gradient(135deg, {bg1}, {bg2});
    color: white;
}}

.block-container {{
    padding-top: 2rem;
    animation: fade 0.6s ease-in-out;
}}

[data-testid="stSidebar"] {{
    background: rgba(0,0,0,0.55);
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255,255,255,0.12);
}}

.hero {{
    padding: 28px;
    border-radius: 28px;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.18);
    backdrop-filter: blur(18px);
    animation: glow 4s infinite ease-in-out;
}}

.title {{
    font-size: 52px;
    font-weight: 950;
    background: linear-gradient(90deg, {glow}, {accent});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

.card {{
    padding: 22px;
    border-radius: 24px;
    background: rgba(255,255,255,0.075);
    border: 1px solid rgba(255,255,255,0.16);
    backdrop-filter: blur(18px);
    animation: fade 0.7s ease-in-out;
}}

textarea, input {{
    border-radius: 18px !important;
}}

.stButton button {{
    border-radius: 18px;
    background: linear-gradient(90deg, {accent}, {glow});
    color: white;
    font-weight: 800;
    border: none;
    transition: 0.2s;
}}

.stButton button:hover {{
    transform: scale(1.03);
    box-shadow: 0 0 25px {glow};
}}
</style>
""", unsafe_allow_html=True)

def extract_code(text):
    match = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else ""

def get_client():
    key = st.session_state.api_key or st.secrets.get("GROQ_API_KEY", "")
    if not key:
        return None
    return Groq(api_key=key)

client = get_client()

st.markdown("""
<div class="hero">
    <div class="title">⚡ Xyzan AI</div>
    <h3>Modern AI coding dashboard</h3>
    <p>Chat, code, debug, upgrade UI, and apply AI-generated code instantly.</p>
</div>
""", unsafe_allow_html=True)

st.write("")

if client:
    st.success("Groq connected.")
else:
    st.warning("Paste your Groq API key in the sidebar.")

col1, col2 = st.columns([1.15, 1])

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📝 Workspace")

    st.session_state.workspace_code = st.text_area(
        "Code editor",
        value=st.session_state.workspace_code,
        height=520,
        placeholder="Paste your app.py here..."
    )

    c1, c2, c3 = st.columns(3)

    run_ai = c1.button("🚀 Run AI", use_container_width=True)

    if c2.button("⚡ Apply AI Code", use_container_width=True):
        if st.session_state.ai_latest_code:
            st.session_state.workspace_code = st.session_state.ai_latest_code
            st.rerun()
        else:
            st.warning("No code to apply yet.")

    if c3.button("🧹 Clear", use_container_width=True):
        st.session_state.workspace_code = ""
        st.session_state.ai_latest_code = ""
        st.session_state.messages = []
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("💬 Chat")

    user_msg = st.chat_input("Talk to Xyzan...")

    if run_ai:
        user_msg = f"{action} this code."

    if user_msg:
        if not client:
            st.error("Add your Groq API key first.")
        else:
            if mode == "Normal Chat":
                prompt = user_msg
            else:
                prompt = f"""
You are Xyzan AI, a premium coding assistant.

Mode: {mode}
Action: {action}

Current code:
{st.session_state.workspace_code}

User message:
{user_msg}

Rules:
Return modern, clean, working answers.
If giving code, return the complete code inside one Python code block.
Developer Mode should be more technical and direct.
"""

            st.session_state.messages.append({"role": "user", "content": user_msg})

            with st.spinner("Xyzan is thinking..."):
                try:
                    response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are Xyzan AI, a modern AI assistant for coding, design, and developer productivity."
                            },
                            *st.session_state.messages[-10:],
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        temperature=temperature,
                        max_tokens=4096
                    )

                    ai_text = response.choices[0].message.content
                    st.session_state.messages.append({"role": "assistant", "content": ai_text})

                    code = extract_code(ai_text)
                    if code:
                        st.session_state.ai_latest_code = code

                except Exception as e:
                    st.error(f"Groq error: {e}")

    for msg in st.session_state.messages[-10:]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.dev_mode:
    st.divider()
    st.subheader("🛠 Developer Mode")
    st.json({
        "model": model,
        "theme": theme_name,
        "messages": len(st.session_state.messages),
        "workspace_chars": len(st.session_state.workspace_code),
        "has_ai_code": bool(st.session_state.ai_latest_code),
        "time": str(datetime.now())
    })

st.divider()

export = {
    "workspace_code": st.session_state.workspace_code,
    "messages": st.session_state.messages,
    "theme": theme_name,
    "model": model,
    "saved_at": str(datetime.now())
}

st.download_button(
    "📦 Export Xyzan Project",
    data=json.dumps(export, indent=2),
    file_name="xyzan_project.json",
    mime="application/json"
)

st.caption("Xyzan AI v3 — modern Streamlit + Groq")
