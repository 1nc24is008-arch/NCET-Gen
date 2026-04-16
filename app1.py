import streamlit as st
from groq import Groq
import time
import uuid
import json
import os

# ---------------- FILE ----------------
CHAT_FILE = "chats.json"

def load_chats():
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r") as f:
            return json.load(f)
    return {}

def save_chats(chats):
    with open(CHAT_FILE, "w") as f:
        json.dump(chats, f)

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Genz_AI", layout="wide")

# ---------------- CHATGPT STYLE CSS ----------------
st.markdown("""
<style>

/* MAIN BACKGROUND */
.stApp {
    background-color: #343541;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background-color: #202123;
    padding: 15px;
}

/* BUTTONS */
.stButton > button {
    background: transparent;
    color: #ECECF1;
    border: none;
    text-align: left;
    padding: 10px;
    border-radius: 8px;
    font-size: 14px;
}

/* HOVER */
.stButton > button:hover {
    background-color: #2A2B32;
}

/* ACTIVE CHAT */
.stButton > button:focus {
    background-color: #343541 !important;
}

/* INPUT BOX */
input {
    background-color: #2A2B32 !important;
    color: white !important;
    border-radius: 8px !important;
}

/* HEADINGS */
h2, h3 {
    color: #9CA3AF !important;
}

/* CHAT AREA */
.block-container {
    max-width: 900px;
    margin: auto;
    padding-bottom: 120px;
}

/* INPUT FIX */
section[data-testid="stChatInput"] {
    position: fixed;
    bottom: 10px;
    left: 280px;
    right: 20px;
    background: #40414F;
    padding: 10px;
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- INIT ----------------
api_key = st.secrets.get("app2") or os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("API key missing!")
    st.stop()

client = Groq(api_key=api_key)

if "chats" not in st.session_state:
    st.session_state.chats = load_chats()

if "current_chat" not in st.session_state:
    if st.session_state.chats:
        st.session_state.current_chat = list(st.session_state.chats.keys())[0]
    else:
        chat_id = str(uuid.uuid4())
        st.session_state.chats[chat_id] = {"name": "New Chat", "messages": []}
        st.session_state.current_chat = chat_id
        save_chats(st.session_state.chats)

# ---------------- SIDEBAR ----------------
with st.sidebar:

    st.markdown("## 🤖 Genz_AI")

    # NEW CHAT
    if st.button("➕ New chat", use_container_width=True):
        chat_id = str(uuid.uuid4())
        st.session_state.chats[chat_id] = {"name": "New Chat", "messages": []}
        st.session_state.current_chat = chat_id
        save_chats(st.session_state.chats)
        st.rerun()

    # SEARCH
    st.markdown("### 🔍 Search chats")
    search = st.text_input("", placeholder="Search...", label_visibility="collapsed")

    st.markdown("---")
    st.markdown("### Recents")

    # CHAT LIST
    for chat_id, chat_data in st.session_state.chats.items():

        if search and search.lower() not in chat_data["name"].lower():
            continue

        if st.button(chat_data["name"], key=f"chat_{chat_id}", use_container_width=True):
            st.session_state.current_chat = chat_id
            st.rerun()

    st.markdown("---")

    # PROFILE
    st.markdown("### 👤 Profile")
    st.markdown("**CHANDAN KUMAR**")
    st.caption("Free Plan")

    st.button("⚙️ Settings", use_container_width=True)

# ---------------- MAIN ----------------
current_chat = st.session_state.current_chat
chat_data = st.session_state.chats[current_chat]
messages = chat_data["messages"]

st.markdown(f"### 💬 {chat_data['name']}")

# ---------------- DISPLAY ----------------
for msg in messages:
    avatar = "🧑" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ---------------- INPUT ----------------
user_input = st.chat_input("Ask anything...")

SYSTEM_PROMPT = {
    "role": "system",
    "content": "You are Genz_AI, a helpful and smart assistant."
}

if user_input:
    if chat_data["name"] == "New Chat":
        chat_data["name"] = user_input[:30]

    messages.append({"role": "user", "content": user_input})

    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):

            placeholder = st.empty()
            full_response = ""

            try:
                # LIMIT MEMORY
                MAX_MESSAGES = 15
                limited_messages = messages[-MAX_MESSAGES:]

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[SYSTEM_PROMPT] + limited_messages,
                    stream=True
                )

                for chunk in response:
                    content = chunk.choices[0].delta.content or ""
                    full_response += content
                    placeholder.markdown(full_response + "▌")
                    time.sleep(0.01)

                placeholder.markdown(full_response)

            except Exception as e:
                full_response = "⚠️ Error generating response"
                st.error(e)

    messages.append({"role": "assistant", "content": full_response})

    st.session_state.chats[current_chat]["messages"] = messages
    save_chats(st.session_state.chats)
