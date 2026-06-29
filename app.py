import streamlit as st
from google import genai
from google.genai import types
import datetime

st.set_page_config(layout="centered", page_title="Xyzan AI — Elite Coding Workspace", page_icon="🔮", initial_sidebar_state="expanded")

if "messages" not in st.session_state: st.session_state.messages = []
if "chat_history" not in st.session_state: st.session_state.chat_history = {}
if "current_chat" not in st.session_state: st.session_state.current_chat = "New Chat"
if "workspace_code" not in st.session_state: st.session_state.workspace_code = ""
if "ai_latest_code" not in st.session_state: st.session_state.ai_latest_code = ""
if "user_likes" not in st.session_state: st.session_state.user_likes = "Clean code, interactive UI."
if "user_hates" not in st.session_state: st.session_state.user_hates = "Redundant filler."

with st.sidebar:
    st.title("🔮 Xyzan Workspace")
    api_key = st.text_input("🔑 Gemini API Key:", type="password")
    if st.button("➕ Start New Chat"):
        st.session_state.messages = []
        st.rerun()

client = genai.Client(api_key=api_key) if api_key else None

st.subheader("💻 Creative Sandbox")
st.session_state.workspace_code = st.text_area("Development Editor", value=st.session_state.workspace_code, height=200)

if st.button("🚀 Apply Fixed Code"):
    st.session_state.workspace_code = st.session_state.ai_latest_code

st.subheader("💬 Talk to Xyzan AI")
for msg in st.session_state.messages:
    st.markdown(f"**{msg['role']}:** {msg['content']}")

prompt = st.chat_input("Ask Xyzan...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    if client:
        context = f"Code: {st.session_state.workspace_code}. Request: {prompt}"
        response = client.models.generate_content(model='gemini-2.0-flash', contents=context)
        ai_text = response.text
        st.session_state.messages.append({"role": "assistant", "content": ai_text})
        if "```" in ai_text:
            try:
                st.session_state.ai_latest_code = ai_text.split("```")[1].split("\n", 1)[1]
            except: pass
        st.rerun()
    else:
        st.warning("Please enter your Gemini API Key in the sidebar to start!")
