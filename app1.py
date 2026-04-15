import streamlit as st
from groq import Groq
import time

# ======================
# PAGE CONFIG
# ======================
st.set_page_config(page_title="Genz_AI", layout="wide")

# ======================
# SESSION STATE
# ======================
if "chat" not in st.session_state:
    st.session_state.chat = []

if "history" not in st.session_state:
    st.session_state.history = []

if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = True

if "menu_open" not in st.session_state:
    st.session_state.menu_open = False

# ======================
# 🎨 PREMIUM UI
# ======================
st.markdown("""
<style>

/* Background */
.stApp {
    background: radial-gradient(circle at top, #0f172a, #020617);
    color: #e2e8f0;
}

/* Hide header/footer */
header, footer {
    visibility: hidden;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(2,6,23,0.9);
    backdrop-filter: blur(10px);
    border-right: 1px solid #1e293b;
}

/* Title */
h1 {
    text-align: center;
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Chat bubbles */
.user {
    background: #1e293b;
    padding: 12px;
    border-radius: 12px;
    margin: 8px 0;
    text-align: right;
}

.bot {
    background: rgba(15,23,42,0.8);
    padding: 12px;
    border-radius: 12px;
    margin: 8px 0;
    border-left: 3px solid #6366f1;
}

/* Input */
.stTextInput input {
    background: rgba(2,6,23,0.8) !important;
    border: 1px solid #334155 !important;
    border-radius: 12px;
    color: white !important;
    padding: 12px;
}

/* Buttons */
.stButton button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    border-radius: 10px;
    border: none;
    transition: 0.3s;
}

.stButton button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 15px rgba(99,102,241,0.6);
}

</style>
""", unsafe_allow_html=True)

# ======================
# 🔑 API
# ======================
client = Groq(api_key=st.secrets["app2"])

# ======================
# ☰ SIDEBAR TOGGLE BUTTON
# ======================
colA, colB = st.columns([1, 10])

with colA:
    if st.button("☰"):
        st.session_state.sidebar_open = not st.session_state.sidebar_open

# ======================
# 📌 SIDEBAR
# ======================
if st.session_state.sidebar_open:
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
else:
    mode = "Marketing"

# ======================
# 🔝 TOP BAR
# ======================
col1, col2, col3 = st.columns([8,1,1])

with col2:
    st.button("🔗 Share")

with col3:
    if st.button("⋮"):
        st.session_state.menu_open = not st.session_state.menu_open

# ======================
# ⚙️ 3-DOT MENU
# ======================
if st.session_state.menu_open:
    st.markdown("### ⚙️ Menu")

    if st.button("📄 New Chat (Menu)"):
        st.session_state.chat = []

    if st.button("💾 Save Chat"):
        st.success("Saved!")

    if st.button("📤 Export Chat"):
        st.download_button("Download", str(st.session_state.chat))

    if st.button("⚙️ Settings"):
        st.info("Coming soon")

# ======================
# 💬 MAIN CHAT
# ======================
st.markdown("<h1>⚡ Genz_AI</h1>", unsafe_allow_html=True)

user_input = st.text_input("Ask anything...")

if st.button("Generate"):
    if user_input:

        if mode == "Marketing":
            prompt = f"Write marketing content for: {user_input}"
        elif mode == "Study":
            prompt = f"Explain this simply: {user_input}"
        else:
            prompt = f"Help me build a project: {user_input}"

        st.session_state.chat.append(("user", user_input))
        st.session_state.history.append(user_input)

        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )

            reply = response.choices[0].message.content

            # Typing effect
            typed = ""
            placeholder = st.empty()
            for char in reply:
                typed += char
                placeholder.markdown(
                    f"<div class='bot'>{typed}</div>",
                    unsafe_allow_html=True
                )
                time.sleep(0.002)

            st.session_state.chat.append(("bot", reply))

# ======================
# 📜 CHAT DISPLAY
# ======================
for role, msg in st.session_state.chat:
    if role == "user":
        st.markdown(f"<div class='user'>{msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot'>{msg}</div>", unsafe_allow_html=True)
