import streamlit as st
from groq import Groq
import time
import uuid
import json
import os

# ---------------- FILE ----------------
CHAT_FILE = "chats.json"

# ---------------- LOAD/SAVE ----------------
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

# ---------------- STYLE ----------------
st.markdown("""
<style>
.stApp {
    background-color: #F7F7F8;
}
[data-testid="stSidebar"] {
    background-color: #202123;
    padding: 20px 10px;
}

[data-testid="stSidebar"] h1 {
    color: #FFFFFF;
}

.stButton>button {
    width: 100%;
    border-radius: 8px;
    background-color: #2A2B32;
    color: white;
    border: none;
    padding: 10px;
    transition: 0.3s;
}

.stButton>button:hover {
    background-color: #FF6A00;
    color: white;
}
.active-chat {
    background-color: #FF6A00 !important;
    color: white !important;
}

textarea {
    border-radius: 10px !important;
    border: 1px solid #ddd !important;
}

.chat-title {
    font-size: 22px;
    font-weight: bold;
    color: #111;
    margin-bottom: 10px;
}


[data-testid="stChatMessage"] {
    border-radius: 10px;
    padding: 10px;
}

[data-testid="stChatMessage"][data-testid*="user"] {
    background-color: #E8E8E8;
}

[data-testid="stChatMessage"][data-testid*="assistant"] {
    background-color: #FFFFFF;
}

::-webkit-scrollbar {
    width: 6px;
}
::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- INIT ----------------
client = Groq(api_key=st.secrets["app2"])

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
    st.title("🤖 Genz_AI")

    # New Chat
    if st.button("➕ New Chat"):
        chat_id = str(uuid.uuid4())
        st.session_state.chats[chat_id] = {"name": "New Chat", "messages": []}
        st.session_state.current_chat = chat_id
        save_chats(st.session_state.chats)
        st.rerun()

    st.markdown("---")

    # Chat List
    for chat_id, chat_data in list(st.session_state.chats.items()):
        col1, col2, col3 = st.columns([3,1,1])

        # Select Chat
        with col1:
            if st.button(chat_data["name"], key=f"chat_{chat_id}"):
                st.session_state.current_chat = chat_id
                st.rerun()

        # Rename
        with col2:
            if st.button("✏️", key=f"rename_{chat_id}"):
                new_name = st.text_input("Rename chat", key=f"input_{chat_id}")
                if new_name:
                    st.session_state.chats[chat_id]["name"] = new_name
                    save_chats(st.session_state.chats)
                    st.rerun()

        # Delete
        with col3:
            if st.button("❌", key=f"del_{chat_id}"):
                del st.session_state.chats[chat_id]
                if not st.session_state.chats:
                    new_chat = str(uuid.uuid4())
                    st.session_state.chats[new_chat] = {"name": "New Chat", "messages": []}
                    st.session_state.current_chat = new_chat
                else:
                    st.session_state.current_chat = list(st.session_state.chats.keys())[0]
                save_chats(st.session_state.chats)
                st.rerun()

# ---------------- MAIN ----------------
current_chat = st.session_state.current_chat
chat_data = st.session_state.chats[current_chat]
messages = chat_data["messages"]

st.markdown(f"<div class='chat-title'>💬 {chat_data['name']}</div>", unsafe_allow_html=True)

# ---------------- DISPLAY ----------------
for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------- INPUT ----------------
user_input = st.chat_input("Type your message...")

if user_input:
    # Rename chat automatically
    if chat_data["name"] == "New Chat":
        chat_data["name"] = user_input[:30]

    messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
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
