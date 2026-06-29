import streamlit as st
from groq import Groq
import re
import json
from datetime import datetime

st.set_page_config(page_title="Xyzan AI", page_icon="⚡", layout="wide")

MODELS = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "openai/gpt-oss-120b",
    "qwen/qwen3-32b"
]

THEMES = {
    "ChatGPT Dark": {
        "bg": "#0b0f19",
        "panel": "#111827",
        "card": "#171f2f",
        "text": "#f8fafc",
        "muted": "#94a3b8",
        "accent": "#10a37f",
        "accent2": "#22c55e"
    },
    "Gemini Glow": {
        "bg": "#050816",
        "panel": "#0f172a",
        "card": "#151b33",
        "text": "#ffffff",
        "muted": "#a5b4fc",
        "accent": "#7c3aed",
        "accent2": "#38bdf8"
    },
    "Grok Black": {
        "bg": "#000000",
        "panel": "#09090b",
        "card": "#18181b",
        "text": "#fafafa",
        "muted": "#a1a1aa",
        "accent": "#ffffff",
        "accent2": "#71717a"
    },
    "DeepSeek Blue": {
        "bg": "#020617",
        "panel": "#0f172a",
        "card": "#172554",
        "text": "#eff6ff",
        "muted": "#93c5fd",
        "accent": "#2563eb",
        "accent2": "#60a5fa"
    },
    "Neon Purple": {
        "bg": "#12001f",
        "panel": "#1e0633",
        "card": "#2d0b4e",
        "text": "#ffffff",
        "muted": "#d8b4fe",
        "accent": "#a855f7",
        "accent2": "#22d3ee"
    }
}

if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "messages" not in st.session_state:
    st.session_state.messages = []
if "workspace" not in st.session_state:
    st.session_state.workspace = ""
if "latest_code" not in st.session_state:
    st.session_state.latest_code = ""
if "theme" not in st.session_state:
    st.session_state.theme = "Gemini Glow"
if "system_mode" not in st.session_state:
    st.session_state.system_mode = "Normal Chat"

theme_name = st.sidebar.selectbox("Theme", list(THEMES.keys()), index=list(THEMES.keys()).index(st.session_state.theme))
st.session_state.theme = theme_name
T = THEMES[theme_name]

st.markdown(f"""
<style>
@keyframes fadeUp {{
  from {{opacity: 0; transform: translateY(18px);}}
  to {{opacity: 1; transform: translateY(0);}}
}}

@keyframes pulseGlow {{
  0% {{box-shadow: 0 0 20px {T["accent"]}44;}}
  50% {{box-shadow: 0 0 45px {T["accent2"]}66;}}
  100% {{box-shadow: 0 0 20px {T["accent"]}44;}}
}}

.stApp {{
  background:
    radial-gradient(circle at 10% 5%, {T["accent"]}35, transparent 28%),
    radial-gradient(circle at 90% 20%, {T["accent2"]}25, transparent 30%),
    linear-gradient(135deg, {T["bg"]}, #020617);
  color: {T["text"]};
}}

.block-container {{
  padding-top: 1.2rem;
  max-width: 1300px;
  animation: fadeUp .55s ease;
}}

[data-testid="stSidebar"] {{
  background: rgba(0,0,0,.58);
  backdrop-filter: blur(22px);
  border-right: 1px solid rgba(255,255,255,.10);
}}

.hero {{
  border-radius: 32px;
  padding: 28px;
  background: linear-gradient(135deg, {T["panel"]}ee, {T["card"]}cc);
  border: 1px solid rgba(255,255,255,.12);
  animation: pulseGlow 5s infinite ease-in-out;
}}

.logo {{
  font-size: 58px;
  font-weight: 1000;
  letter-spacing: -2px;
  background: linear-gradient(90deg, {T["accent2"]}, {T["accent"]});
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}}

.sub {{
  color: {T["muted"]};
  font-size: 18px;
}}

.panel {{
  margin-top: 18px;
  padding: 20px;
  border-radius: 28px;
  background: rgba(255,255,255,.075);
  border: 1px solid rgba(255,255,255,.12);
  backdrop-filter: blur(18px);
}}

.mode-pill {{
  display: inline-block;
  padding: 8px 13px;
  border-radius: 999px;
  background: {T["accent"]}22;
  border: 1px solid {T["accent"]}66;
  color: {T["text"]};
  margin-right: 8px;
  margin-bottom: 8px;
  font-size: 13px;
}}

textarea, input {{
  border-radius: 18px !important;
}}

.stButton button {{
  border-radius: 18px;
  font-weight: 800;
  border: 1px solid rgba(255,255,255,.14);
  background: linear-gradient(90deg, {T["accent"]}, {T["accent2"]});
  color: white;
}}

.stButton button:hover {{
  transform: translateY(-1px) scale(1.01);
  box-shadow: 0 0 25px {T["accent2"]}77;
}}

[data-testid="stChatMessage"] {{
  background: rgba(255,255,255,.06);
  border: 1px solid rgba(255,255,255,.10);
  border-radius: 20px;
  padding: 10px;
}}

@media (max-width: 768px) {{
  .logo {{font-size: 42px;}}
  .hero {{padding: 22px; border-radius: 24px;}}
}}
</style>
""", unsafe_allow_html=True)

def extract_code(text):
    patterns = [
        r"```python\s*(.*?)```",
        r"```\s*(.*?)```"
    ]
    for p in patterns:
        m = re.search(p, text, re.DOTALL)
        if m:
            return m.group(1).strip()
    return ""

def get_client():
    key = st.session_state.api_key.strip()
    if not key:
        try:
            key = st.secrets.get("GROQ_API_KEY", "")
        except Exception:
            key = ""
    if not key:
        return None
    return Groq(api_key=key)

st.sidebar.title("⚡ Xyzan")
st.session_state.api_key = st.sidebar.text_input(
    "Groq API Key",
    value=st.session_state.api_key,
    type="password",
    placeholder="Paste gsk_ key here"
)

model = st.sidebar.selectbox("Model", MODELS, index=0)

st.session_state.system_mode = st.sidebar.radio(
    "Mode",
    ["Normal Chat", "Coding Sandbox", "Developer Mode"]
)

action = st.sidebar.selectbox(
    "AI Tool",
    [
        "Answer normally",
        "Fix bugs",
        "Optimize code",
        "Explain code",
        "Make UI modern",
        "Add feature",
        "Security check",
        "Full app upgrade"
    ]
)

temperature = st.sidebar.slider("Creativity", 0.0, 1.0, 0.45)

client = get_client()

if client:
    st.sidebar.success("Groq connected")
else:
    st.sidebar.warning("Paste API key")

if st.sidebar.button("Clear chat"):
    st.session_state.messages = []
    st.rerun()

if st.sidebar.button("Clear workspace"):
    st.session_state.workspace = ""
    st.session_state.latest_code = ""
    st.rerun()

st.markdown(f"""
<div class="hero">
  <div class="logo">⚡ Xyzan AI</div>
  <div class="sub">Modern AI workspace inspired by ChatGPT, Gemini, Grok, and DeepSeek — but branded as your own.</div>
  <br>
  <span class="mode-pill">Chat</span>
  <span class="mode-pill">Code</span>
  <span class="mode-pill">Developer Mode</span>
  <span class="mode-pill">Themes</span>
  <span class="mode-pill">Apply AI Code</span>
</div>
""", unsafe_allow_html=True)

left, right = st.columns([1.08, 1])

with left:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("🧠 Chat")

    for msg in st.session_state.messages[-12:]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_msg = st.chat_input("Message Xyzan...")

    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("💻 Workspace")

    st.session_state.workspace = st.text_area(
        "Code editor",
        value=st.session_state.workspace,
        height=410,
        placeholder="Paste your app.py or code here..."
    )

    c1, c2 = st.columns(2)

    run_code_ai = c1.button("🚀 Improve Code", use_container_width=True)

    if c2.button("⚡ Apply Last Code", use_container_width=True):
        if st.session_state.latest_code:
            st.session_state.workspace = st.session_state.latest_code
            st.success("Applied.")
            st.rerun()
        else:
            st.warning("No AI code yet.")

    if st.session_state.latest_code:
        with st.expander("Preview extracted AI code"):
            st.code(st.session_state.latest_code, language="python")

    st.markdown("</div>", unsafe_allow_html=True)

if run_code_ai:
    user_msg = f"{action}. Return the full upgraded code."

if user_msg:
    if not client:
        st.error("Paste Groq API key in sidebar first.")
    else:
        if st.session_state.system_mode == "Normal Chat":
            final_prompt = user_msg
        else:
            final_prompt = f"""
You are Xyzan AI, a modern premium AI assistant for coding.

Style:
- Clean like ChatGPT.
- Fast like Groq.
- Helpful like Gemini.
- Direct like Grok.
- Technical like DeepSeek.
Do not copy branding or names. Use Xyzan branding.

Mode: {st.session_state.system_mode}
Action: {action}

Workspace code:
{st.session_state.workspace}

User message:
{user_msg}

Rules:
- Be useful and direct.
- For code tasks, return COMPLETE working code.
- If returning code, use ONE Python code block.
- Do not use deprecated Groq models.
- Make Streamlit UI modern, mobile-friendly, and clean.
"""

        st.session_state.messages.append({"role": "user", "content": user_msg})

        try:
            with st.spinner("Xyzan thinking..."):
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are Xyzan AI, a premium AI assistant for chat, coding, UI design, and developer productivity."
                        },
                        *st.session_state.messages[-8:],
                        {
                            "role": "user",
                            "content": final_prompt
                        }
                    ],
                    temperature=temperature,
                    max_tokens=4096
                )

            ai_text = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": ai_text})

            code = extract_code(ai_text)
            if code:
                st.session_state.latest_code = code

            st.rerun()

        except Exception as e:
            st.error(f"Groq error: {e}")

if st.session_state.system_mode == "Developer Mode":
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("🛠 Developer Console")
    st.json({
        "model": model,
        "theme": theme_name,
        "mode": st.session_state.system_mode,
        "messages": len(st.session_state.messages),
        "workspace_characters": len(st.session_state.workspace),
        "has_extracted_code": bool(st.session_state.latest_code),
        "time": str(datetime.now())
    })
    st.markdown("</div>", unsafe_allow_html=True)

export_data = {
    "workspace": st.session_state.workspace,
    "messages": st.session_state.messages,
    "theme": theme_name,
    "model": model,
    "saved_at": str(datetime.now())
}

st.download_button(
    "📦 Export Project",
    data=json.dumps(export_data, indent=2),
    file_name="xyzan_project.json",
    mime="application/json"
)

st.caption("Xyzan AI v4")
