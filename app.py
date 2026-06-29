import streamlit as st
from google import genai
from google.genai import types
import datetime

# 1. PAGE & THEME CONFIGURATION
st.set_page_config(layout="centered", page_title="Xyzan AI", page_icon="🔮")

# Initialize Session States
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {} # Format: { "Date - Title": [messages] }
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "New Chat"
if "workspace_code" not in st.session_state:
    st.session_state.workspace_code = ""
if "ai_latest_code" not in st.session_state:
    st.session_state.ai_latest_code = ""
if "user_likes" not in st.session_state:
    st.session_state.user_likes = "Prefers clean, high-performance code. Wants games, custom programs, and websites."
if "user_hates" not in st.session_state:
    st.session_state.user_hates = "Hates over-complicated logic and useless filler explanations."
if "app_theme" not in st.session_state:
    st.session_state.app_theme = "Cyber Purple"

# Apply Custom Themes via Injecting CSS
themes = {
    "Cyber Purple": {"bg": "#120c1f", "text": "#e0d5f5", "accent": "#8a2be2"},
    "Dark Red": {"bg": "#1a0808", "text": "#f5dada", "accent": "#b30000"},
    "Default Dark": {"bg": "#111111", "text": "#ffffff", "accent": "#0084ff"},
    "Light Mode": {"bg": "#ffffff", "text": "#111111", "accent": "#0084ff"}
}
active_theme = themes[st.session_state.app_theme]

st.markdown(f"""
    <style>
    .stApp {{ background-color: {active_theme['bg']}; color: {active_theme['text']}; }}
    h1, h2, h3 {{ color: {active_theme['accent']} !important; }}
    </style>
""", unsafe_allow_html=True)

st.title("🔮 Xyzan AI")

# 2. SIDEBAR: SETTINGS & HISTORY
with st.sidebar:
    st.header("⚙️ Settings & Control")
    api_key = st.text_input("Gemini API Key:", type="password")
    
    # Theme Selection
    st.session_state.app_theme = st.selectbox(
        "Select Theme:", 
        ["Cyber Purple", "Dark Red", "Default Dark", "Light Mode"],
        index=list(themes.keys()).index(st.session_state.app_theme)
    )
    
    st.write("---")
    st.header("🧠 Smart Memory Profile")
    st.session_state.user_likes = st.text_area("What I Like:", st.session_state.user_likes, height=70)
    st.session_state.user_hates = st.text_area("What I Hate:", st.session_state.user_hates, height=70)
    st.caption("Xyzan AI uses this profile context to become smarter and adapt to you over time.")
    
    st.write("---")
    st.header("📅 Chat History")
    
    # Manage Chats
    chat_titles = ["New Chat"] + list(st.session_state.chat_history.keys())
    st.session_state.current_chat = st.selectbox("Select Conversation:", chat_titles)
    
    if st.session_state.current_chat != "New Chat":
        st.caption(f"Active Chat Context")
        if st.button("❌ Delete Current Chat", use_container_width=True):
            del st.session_state.chat_history[st.session_state.current_chat]
            st.session_state.messages = []
            st.session_state.current_chat = "New Chat"
            st.rerun()

# Sync active messages with history selection
if st.session_state.current_chat != "New Chat":
    st.session_state.messages = st.session_state.chat_history[st.session_state.current_chat]

client = None
if api_key:
    client = genai.Client(api_key=api_key)

# 3. INTERFACE WORKSPACE
st.subheader("1. Code Workspace")

# Callback to update workspace state smoothly
def update_code():
    st.session_state.workspace_code = st.session_state.new_code_input

current_code = st.text_area(
    "Paste your program, game script, or website code here:", 
    value=st.session_state.workspace_code,
    height=250, 
    key="new_code_input",
    on_change=update_code,
    placeholder="// Ready to build games, tools, websites..."
)

# Apply Code Feature
if st.session_state.ai_latest_code:
    if st.button("🚀 Apply Fixed AI Code to Workspace", use_container_width=True):
        st.session_state.workspace_code = st.session_state.ai_latest_code
        st.session_state.ai_latest_code = "" # Clear temporary swap holder
        st.rerun()

st.write("---")
st.subheader("2. Talk to Xyzan AI")

# Print Chat History Stream
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 4. CHAT INPUT LOGIC
if prompt := st.chat_input("Ask Xyzan to modify, debug, or write new systems..."):
    if not client:
        st.error("Please insert your Gemini API Key in the left sidebar settings first!")
    else:
        # Append User Message
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Build System Personality with memory tracking
        system_instruction = f"""
        Your name is Xyzan AI, an elite programmer specializing in custom applications, full video games, and web design.
        CRITICAL PERSONALITY INSTRUCTIONS:
        1. Be completely brutally honest. If code is terrible, tell the user directly, then show them the perfect fix.
        2. Do NOT explain how the code works unless the user explicitly uses the word 'explain' or asks a conceptual question.
        3. If the user asks for updates, rewrites, or fixes, always output the complete updated script neatly formatted in standard markdown code blocks.
        
        User Personalization Context (Adapt to this):
        - Things the user likes: {st.session_state.user_likes}
        - Things the user hates: {st.session_state.user_hates}
        """

        full_prompt = f"Workspace Code:\n```\n{current_code}\n```\n\nInstructions/Request: {prompt}"

        with chat_container:
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                try:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=full_prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction
                        )
                    )
                    ai_text = response.text
                    response_placeholder.markdown(ai_text)
                    st.session_state.messages.append({"role": "assistant", "content": ai_text})
                    
                    # Logic to catch the raw code for the 'Apply Code' mechanism
                    if "```" in ai_text:
                        try:
                            # Extract code inside the markdown blocks
                            extracted = ai_text.split("```")[1]
                            # Drop the language identifier line if it exists
                            if "\n" in extracted:
                                extracted = extracted.split("\n", 1)[1]
                            st.session_state.ai_latest_code = extracted
                        except:
                            pass

                    # Handle Chat History auto-saving with Timestamp names
                    if st.session_state.current_chat == "New Chat":
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                        chat_title = f"{timestamp} - {prompt[:15]}..."
                        st.session_state.chat_history[chat_title] = st.session_state.messages
                        st.session_state.current_chat = chat_title
                    else:
                        st.session_state.chat_history[st.session_state.current_chat] = st.session_state.messages
                    
                    st.rerun()

                except Exception as e:
                    st.error(f"API Error: {e}")
                  
