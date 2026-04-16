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

# ---------------- PROFESSIONAL CSS ----------------
st.markdown("""
<style>

/* MAIN */
.stApp {
    background-color: #F9FAFB;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827, #0B0F19);
    padding: 20px 12px;
    border-right: 1px solid rgba(255,255,255,0.05);
}

/* TITLE */
[data-testid="stSidebar"] h1 {
    font-size: 20px;
    font-weight: 600;
    color: #F9FAFB;
}

/* SECTION */
[data-testid="stSidebar"] h3 {
    font-size: 12px;
    color: #9CA3AF;
    text-transform: uppercase;
}

/* BUTTON */
.stButton > button {
    width: 100%;
    border-radius: 10px;
    background: #1F2937;
    color: #E5E7EB;
    border: none;
    padding: 10px;
    text-align: left;
    transition: 0.2s;
}

.stButton > button:hover {
    background: #374151;
    transform: translateX(2px);
}

/* NEW CHAT BUTTON */
.stButton:first-child > button {
    background: linear-gradient(135deg, #2563EB, #1D4ED8);
    color: white;
    text-align: center;
}

.stButton:first-child > button:hover {
    background: linear-gradient(135deg, #1D4ED8, #1E40AF);
}

/* CHAT AREA */
.block-container {
    max-width: 900px;
    margin: auto;
    padding-bottom: 120px;
}

/* INPUT */
section[data-testid="stChatInput"] {
    position: fixed;
    bottom: 10px;
    left: 300px;
    right: 20px;
    background: white;
    padding: 10px;
    border-radius: 12px;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.1);
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
    st.markdown("### 🤖 Genz_AI")
    st.caption("Your AI Assistant")

    if st.button("➕ New Chat"):
        chat_id = str(uuid.uuid4())
        st.session_state.chats[chat_id] = {"name": "New Chat", "messages": []}
        st.session_state.current_chat = chat_id
        save_chats(st.session_state.chats)
        st.rerun()

    st.markdown("### Your Chats")

    for chat_id, chat_data in list(st.session_state.chats.items()):
        col1, col2, col3 = st.columns([6,1,1])

        # SELECT
        with col1:
            if st.button(chat_data["name"], key=f"chat_{chat_id}"):
                st.session_state.current_chat = chat_id
                st.rerun()

        # RENAME FIX
        if f"rename_{chat_id}" not in st.session_state:
            st.session_state[f"rename_{chat_id}"] = False

        with col2:
            if st.button("✏️", key=f"rename_btn_{chat_id}"):
                st.session_state[f"rename_{chat_id}"] = True

        with col3:
            if st.button("❌", key=f"del_{chat_id}"):
                del st.session_state.chats[chat_id]
                save_chats(st.session_state.chats)
                st.rerun()

        if st.session_state[f"rename_{chat_id}"]:
            new_name = st.text_input("Rename", key=f"text_{chat_id}")
            if st.button("Save", key=f"save_{chat_id}"):
                if new_name:
                    st.session_state.chats[chat_id]["name"] = new_name
                    st.session_state[f"rename_{chat_id}"] = False
                    save_chats(st.session_state.chats)
                    st.rerun()

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
user_input = st.chat_input("Type your message...")

SYSTEM_PROMPT = {
    "role": "system",
    "content": "You are Genz_AI, a smart and helpful assistant."
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
                # MEMORY LIMIT
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
