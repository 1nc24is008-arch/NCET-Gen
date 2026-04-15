import streamlit as st
from groq import Groq

# Page Config
st.set_page_config(page_title="PragyanAI Content Generator", layout="wide")

# Title & Image
st.title("PragyanAI – Content Generator")
st.image("The_ghost.jfif")

# Initialize Groq Client (API key from Streamlit Secrets)
client = Groq(api_key=st.secrets["First_project"])

# Inputs
product = st.text_input("Product")
audience = st.text_input("Audience")

# Generate Content
if st.button("Generate Content"):
    if product and audience:
        with st.spinner("Generating content... ⏳"):
            prompt = f"Write marketing content for {product} targeting {audience}."

            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )

                text = response.choices[0].message.content
                st.session_state.text = text
                st.success("Content generated successfully ✅")
                st.write(text)

            except Exception as e:
                st.error("Error generating content ❌")
                st.exception(e)
    else:
        st.warning("Please enter both Product and Audience ⚠️")

# Show & Download Content
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
