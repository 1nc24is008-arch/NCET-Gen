import streamlit as st
import replicate
import os

# Page Config
st.set_page_config(page_title="Genz Image AI", layout="centered")

st.title("🖼️ Genz – AI Image Generator")

# Set Replicate API Key
os.environ["REPLICATE_API_TOKEN"] = st.secrets["app2"]

# Input prompt
prompt = st.text_area("Enter your image prompt")

# Generate Image Function
def generate_image(prompt):
    output = replicate.run(
        "stability-ai/sdxl:latest",
        input={
            "prompt": prompt,
            "width": 1024,
            "height": 1024
        }
    )
    return output[0]   # returns image URL

# Button
if st.button("Generate Image"):
    if prompt:
        with st.spinner("Generating image... 🎨"):
            try:
                img_url = generate_image(prompt)

                st.image(img_url, caption="Generated Image", use_column_width=True)

                # Save in session
                st.session_state.image = img_url

                st.success("Image generated successfully ✅")

            except Exception as e:
                st.error("Error generating image ❌")
                st.exception(e)
    else:
        st.warning("Please enter a prompt")

# Download option
if "image" in st.session_state:
    st.markdown("### Download Image")

    st.markdown(f"[Click here to download]({st.session_state.image})")
