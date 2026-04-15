import streamlit as st
from groq import Groq

st.set_page_config(page_title="PragyanAI Content Generator", layout="wide")
st.title("PragyanAI – Content Generator")
st.image("The_ghost.jfif")

# Get GROQ API Key
client = Groq(api_key=st.secrets.get("First_project"))

# Get Product Name and Audience for That Product
product = st.text_input("Product")
audience = st.text_input("Audience")

# Button to Generate Content
if st.button("Generate Content"):
    prompt = f"Write marketing content for {product} targeting {audience}."
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.choices[0].message.content
    st.session_state.text = text
    st.write(text)
  
# After Content Create - Download The File
if "text" in st.session_state:
    content = st.text_area("Generated Content", st.session_state.text, height=300)
    st.download_button(
            label="⬇️ Download as TXT",
            data=content,
            file_name="marketing_copy.txt",
            mime="text/plain"
        )
else:
        st.info("Generate content first")
