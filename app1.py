import streamlit as st
from groq import Groq
import time

# Page config
st.set_page_config(page_title="Genz_AI", layout="wide")

# 🎨 UI Styling
st.markdown("""
<style>
.stApp {
    background-color: #0b0b0b;
    color: white;
}

/* Hide header/footer */
header, footer {
    visibility: hidden;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #111;
    border-right: 1px solid #222;
}

/* Chat bubbles */
.user {
    background: #1f1f1f;
    padding: 12px;
    border-radius: 10px;
    margin: 8px 0;
    text-align: right;
}

.bot {
    background: #141414;
    padding: 12px;
    border-radius: 10px;
    margin: 8px 0;
    border-left: 3px solid red;
}

/* Input */
.stTextInput input {
    background-color: #111 !important;
    color: white !important;
    border-radius: 10px;
}

/* Buttons */
.stButton button {
    background-color: red;
    color: white;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# API
client = Groq(api_key=st.secrets["app2"])

# Session state
if "chat" not in st.session_state:
    st.session_state.chat = []

if "history" not in st.session_state:
    st.session_state.history = []

# =====================
# SIDEBAR
# =====================
with st.sidebar:
    st.title("⚡ Genz_AI")

    if st.button("➕ New Chat"):
        st.session_state.chat = []

    st.markdown("### Modes")
    mode = st.radio("", ["Marketing", "Study", "Project"])

    st.markdown("### History")
    for item in st.session_state.history[-5:]:
        st.caption("• " + item)

    st.markdown("---")
    st.button("⚙️ Account")

# =====================
# TOP BAR
# =====================
col1, col2, col3 = st.columns([8,1,1])

with col2:
    st.button("🔗 Share")

with col3:
    st.button("⋮")

# =====================
# MAIN CHAT
# =====================
st.title("⚡ Genz_AI")

user_input = st.text_input("Ask anything...")

if st.button("Generate"):
    if user_input:

        # Prompt
        if mode == "Marketing":
            prompt = f"Write marketing content for: {user_input}"
        elif mode == "Study":
            prompt = f"Explain this simply: {user_input}"
        else:
            prompt = f"Help me build a project: {user_input}"

        st.session_state.chat.append(("user", user_input))
        st.session_state.history.append(user_input)

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )

        reply = response.choices[0].message.content

        # Typing animation
        typed = ""
        placeholder = st.empty()
        for char in reply:
            typed += char
            placeholder.markdown(f"<div class='bot'>{typed}</div>", unsafe_allow_html=True)
            time.sleep(0.003)

        st.session_state.chat.append(("bot", reply))

# Show chat
for role, msg in st.session_state.chat:
    if role == "user":
        st.markdown(f"<div class='user'>{msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot'>{msg}</div>", unsafe_allow_html=True)
