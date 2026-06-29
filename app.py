import streamlit as st
from google import genai
from google.genai import types
import datetime

# 1. EMPOWERED PAGE CONFIGURATION & METADATA
st.set_page_config(
    layout="centered", 
    page_title="Xyzan AI — Elite Coding Workspace", 
    page_icon="🔮",
    initial_sidebar_state="expanded"
)

# 2. THEME STATES AND SESSION CACHING
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {} # Format: { "Title (Date)": [messages] }
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "New Chat"
if "workspace_code" not in st.session_state:
    st.session_state.workspace_code = ""
if "ai_latest_code" not in st.session_state:
    st.session_state.ai_latest_code = ""
if "user_likes" not in st.session_state:
    st.session_state.user_likes = "Clean, high-performance logic. Interactive layouts, full-scale custom builds."
if "user_hates" not in st.session_state:
    st.session_state.user_hates = "Messy boilerplates, redundant explanations, slow execution paths."
if "app_theme" not in st.session_state:
    st.session_state.app_theme = "Cyber Purple"
if "honesty_level" not in st.session_state:
    st.session_state.honesty_level = "Brutally Honest"

# Define Elite Color Schemes
theme_styles = {
    "Cyber Purple": {
        "bg_gradient": "linear-gradient(135deg, #090514 0%, #110722 100%)",
        "primary": "#8a2be2",
        "secondary": "#c77dff",
        "text": "#e0d5f5",
        "card_bg": "rgba(23, 13, 38, 0.65)",
        "accent_glow": "rgba(138, 43, 226, 0.35)",
        "border": "rgba(138, 43, 226, 0.2)"
    },
    "Dark Red": {
        "bg_gradient": "linear-gradient(135deg, #0f0404 0%, #1c0505 100%)",
        "primary": "#d90429",
        "secondary": "#ef233c",
        "text": "#f5d6d6",
        "card_bg": "rgba(35, 12, 12, 0.65)",
        "accent_glow": "rgba(217, 4, 41, 0.35)",
        "border": "rgba(217, 4, 41, 0.2)"
    }
}

active_theme = theme_styles.get(st.session_state.app_theme, theme_styles["Cyber Purple"])

# 3. HIGH-END DESIGN GLOW-UP (Injecting Glassmorphism & Animations)
st.markdown(f"""
    <style>
    /* Premium Application Shell */
    .stApp {{
        background: {active_theme['bg_gradient']} !important;
        color: {active_theme['text']} !important;
        animation: smoothIntro 0.7s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    @keyframes smoothIntro {{
        from {{ opacity: 0; transform: translateY(12px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    /* Clean custom sidebar tweak */
    section[data-testid="stSidebar"] {{
        background-color: rgba(10, 8, 16, 0.3) !important;
        border-right: 1px solid {active_theme['border']};
    }}
    
    /* Elegant code boxes */
    textarea {{
        background-color: {active_theme['card_bg']} !important;
        color: #ffffff !important;
        border-radius: 14px !important;
        border: 1px solid {active_theme['border']} !important;
        font-family: 'Courier New', Courier, monospace !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }}
    textarea:focus {{
        border-color: {active_theme['primary']} !important;
        box-shadow: 0 0 16px {active_theme['accent_glow']} !important;
    }}
    
    /* Premium Chat Layout */
    .chat-bubble {{
        padding: 1rem 1.25rem;
        border-radius: 16px;
        margin-bottom: 0.75rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
        line-height: 1.5;
    }}
    .user-bubble {{
        background-color: rgba(255, 255, 255, 0.05);
    }}
    .ai-bubble {{
        background-color: {active_theme['card_bg']};
        border-left: 3px solid {active_theme['primary']};
    }}
    
    /* Animated Buttons */
    button {{
        border-radius: 12px !important;
        background: linear-gradient(90deg, {active_theme['primary']} 0%, {active_theme['secondary']} 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        transition: transform 0.1s ease, box-shadow 0.2s ease !important;
    }}
    button:active {{
        transform: scale(0.97);
    }}
    </style>
""", unsafe_allow_html=True)

# 4. SIDEBAR SETTINGS AND HISTORICAL LOGS
with st.sidebar:
    st.title("🔮 Xyzan Workspace")
    
    # Secure API Access & Fallback Mode
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    
    if not api_key:
        api_key_input = st.text_input("🔑 Gemini API Key:", type="password", help="Providing your key allows real-time execution. Leave empty to use Playground Simulator Mode!")
        if api_key_input:
            api_key = api_key_input

    # Dynamic Theme Picker
    st.session_state.app_theme = st.selectbox(
        "⚡ Choose Theme:",
        ["Cyber Purple", "Dark Red"],
        index=0 if st.session_state.app_theme == "Cyber Purple" else 1
    )
    
    # Self-Adapting Memory Profiles
    st.subheader("🧠 Memory Profile")
    st.session_state.user_likes = st.text_area("What I Like:", st.session_state.user_likes, height=75)
    st.session_state.user_hates = st.text_area("What I Hate:", st.session_state.user_hates, height=75)
    
    # Extra settings parameters
    st.session_state.honesty_level = st.select_slider(
        "🔥 Brutal Honesty Index:",
        options=["Polite Helper", "Constructive Critic", "Brutally Honest"],
        value=st.session_state.honesty_level
    )
    
    st.write("---")
    st.subheader("💬 Active Conversations")
    
    # Clear / Reset Action (Like ChatGPT style)
    if st.button("➕ Start New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_chat = "New Chat"
        st.rerun()
        
    # Loaded conversations timeline
    chat_titles = ["New Chat"] + list(st.session_state.chat_history.keys())
    selected_chat = st.selectbox("Select Session History:", chat_titles)
    
    if selected_chat != st.session_state.current_chat:
        st.session_state.current_chat = selected_chat
        if selected_chat == "New Chat":
            st.session_state.messages = []
        else:
            st.session_state.messages = st.session_state.chat_history[selected_chat]
        st.rerun()
        
    if st.session_state.current_chat != "New Chat":
        if st.button("❌ Close Selected Chat", use_container_width=True):
            if st.session_state.current_chat in st.session_state.chat_history:
                del st.session_state.chat_history[st.session_state.current_chat]
            st.session_state.messages = []
            st.session_state.current_chat = "New Chat"
            st.rerun()

# Client instantiation
client = None
if api_key:
    client = genai.Client(api_key=api_key)

# 5. CORE WORKSPACE ENVIRONMENT
st.subheader("💻 1. Creative Sandbox")

def sync_workspace():
    st.session_state.workspace_code = st.session_state.workspace_box_id

# Editable code window panel
current_code = st.text_area(
    "Development Editor Input",
    value=st.session_state.workspace_code,
    height=250,
    key="workspace_box_id",
    on_change=sync_workspace,
    label_visibility="collapsed",
    placeholder="// Paste your Python script, HTML/JS, or Minecraft code to analyze..."
)

# Workspace Action Utilities Toolbar
col1, col2, col3 = st.columns(3)
with col1:
    # Instant File Exporter
    if current_code.strip():
        st.download_button(
            label="💾 Export Local File",
            data=current_code,
            file_name=f"xyzan_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py",
            mime="text/plain",
            use_container_width=True
        )
    else:
        st.button("💾 Export Local File", disabled=True, use_container_width=True)

with col2:
    if st.button("🧹 Wipe Workspace", use_container_width=True):
        st.session_state.workspace_code = ""
        st.rerun()

with col3:
    # Action Preset Generator Prompt Helper
    st.write("") # Center spacer

# Instant application swap controller
if st.session_state.ai_latest_code:
    if st.button("🚀 Apply Fixed AI Code Direct to Workspace", use_container_width=True):
        st.session_state.workspace_code = st.session_state.ai_latest_code
        st.session_state.ai_latest_code = ""
        st.rerun()

st.write("---")
st.subheader("💬 2. Talk to Xyzan AI")

# Streamlined dialogue bubbles
for msg in st.session_state.messages:
    bubble_class = "user-bubble" if msg["role"] == "user" else "ai-bubble"
    st.markdown(f"""
        <div class="chat-bubble {bubble_class}">
            <strong>{"👤 User" if msg["role"] == "user" else "🔮 Xyzan AI"}:</strong><br>
            {msg["content"]}
        </div>
    """, unsafe_allow_html=True)

# Preset Library Prompt Injection Bar
st.caption("⚡ Quick Actions Helper Preset:")
preset_col1, preset_col2, preset_col3 = st.columns(3)
preset_selection = ""
with preset_col1:
    if st.button("🔍 Find Bugs & Glitches", use_container_width=True):
        preset_selection = "Find all bugs, memory leaks, and compilation errors inside this code and repair them instantly."
with preset_col2:
    if st.button("📈 Optimize Performance", use_container_width=True):
        preset_selection = "Identify performance bottlenecks, simplify logic, and optimize this code for speed."
with preset_col3:
    if st.button("🎨 Make Interactive UI", use_container_width=True):
        preset_selection = "Enhance the styling of this file. Use a gorgeous modern color palette, clean curves, and premium spacing."

# Input chat logic processing
prompt = st.chat_input("Prompt Xyzan AI...")

# Trigger preset selection if clicked
if preset_selection:
    prompt = preset_selection

if prompt:
    # Add User message instantly
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 6. PIPELINE ROUTING: REAL EXECUTION VS PLAYGROUND SIMULATOR
    if not client:
        # Smart Playground Mode (No API keys configured)
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"⚙️ **[PLAYGROUND SIMULATION MODE]**\n\nI can see you haven't linked your Gemini Key yet. Your prompt is perfectly received: \n\n*\"{prompt}\"*\n\nTo make me functional, simply plug your Gemini API key in the sidebar dashboard option or your Streamlit Secrets Panel! Once loaded, I will read this workspace and write pristine production scripts for you."
        })
        st.rerun()
    else:
        # Configure Honesty settings variables
        honesty_instructions = {
            "Polite Helper": "Format responses with a supportive tone, gently pointing out issues.",
            "Constructive Critic": "Directly address weaknesses in the user's code, focusing on building optimal structures.",
            "Brutally Honest": "Do not sugarcoat anything. If logic is garbage, tell the user directly with humorous, sharp, and elite critique, then show the flawless fix."
        }
        
        system_instruction = f"""
        Your name is Xyzan AI, an elite programmer specializing in custom applications, full video games, and web design.
        
        CRITICAL PERSONALITY RULES:
        1. Honesty Tuning: {honesty_instructions[st.session_state.honesty_level]}
        2. Do NOT explain how the code works unless the user explicitly uses the word 'explain' or asks a conceptual question.
        3. If the user asks for updates, rewrites, or fixes, always output the complete updated script neatly formatted in standard markdown code blocks.
        
        User Personalization Context:
        - Things the user likes: {st.session_state.user_likes}
        - Things the user hates: {st.session_state.user_hates}
        """

        compiled_prompt = f"Workspace Code Context:\n

```

