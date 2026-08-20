import os
import streamlit as st
from PIL import Image
from google import genai

# 1. Page Configuration
st.set_page_config(page_title="A/L Science Master Tutor", layout="wide", page_icon="🎓")

# 2. API Key එක ආරක්ෂිතව සඟවා ලබා ගැනීම (Secrets/Environment Variables)
API_KEY = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    st.error("⚠️ GEMINI_API_KEY එක හමු නොවීය! Streamlit Cloud Secrets හෝ environment variables පරීක්ෂා කරන්න.")
    st.stop()

client = genai.Client(api_key=API_KEY)

# 3. Sidebar - Settings & Developer Details
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Language Selector
    language = st.radio("Language / භාෂාව තෝරන්න:", ["Sinhala", "English"])
    
    # Language අනුව Labels වෙනස් කිරීම
    if language == "Sinhala":
        subj_label = "විෂය තෝරන්න:"
        input_label = "ප්‍රශ්නය ලබාදෙන ආකාරය:"
        opt_text = "Text (ලියන්න)"
        opt_photo = "Photo Upload (ඡායාරූපයක්)"
    else:
        subj_label = "Select Subject:"
        input_label = "Select Input Type:"
        opt_text = "Text"
        opt_photo = "Photo Upload"

    subject = st.selectbox(subj_label, ["Combined Mathematics", "Physics", "Chemistry"])
    input_type = st.radio(input_label, [opt_text, opt_photo])

    # Created By - Sidebar Info
    st.markdown("---")
    st.markdown("### 👨‍💻 Developed by")
    st.write("**Janidu Kaveesha**")

# 4. Web App Title
if language == "Sinhala":
    st.title("🎓 A/L Master Tutor (Maths | Physics | Chemistry)")
    st.write("අතින් ලියන නිවැරදි ගණිතමය සංකේත (LaTeX Math) සහ පැහැදිලි විසඳුම් සමඟින්")
else:
    st.title("🎓 A/L Master Tutor (Maths | Physics | Chemistry)")
    st.write("Step-by-step explanations with LaTeX Math formatting")

# 5. Input Handling
user_image = None
user_text = ""

if "Photo Upload" in input_type:
    prompt_img_label = "ප්‍රශ්නයේ Photo එක Upload කරන්න" if language == "Sinhala" else "Upload Question Photo"
    uploaded_file = st.file_uploader(prompt_img_label, type=["jpg", "jpeg", "png"])
    if uploaded_file:
        user_image = Image.open(uploaded_file)
        st.image(user_image, caption="Uploaded Image", use_column_width=True)

prompt_txt_label = "ඔබගේ ප්‍රශ්නය මෙහි ටයිප් කරන්න:" if language == "Sinhala" else "Type your question here:"
user_text = st.text_area(prompt_txt_label)

# 6. AI Prompt Setup
system_instruction = f"""
You are an expert Sri Lankan G.C.E. A/L Science stream tutor in {subject}.
Answer the user's question clearly step-by-step.

IMPORTANT LANGUAGE INSTRUCTIONS:
- Explain everything strictly in {language} language.
- If Language is 'Sinhala', use clear Sri Lankan A/L Sinhala technical terms combined with LaTeX ($...$ or $$...$$) for mathematical/physics equations.
- If Language is 'English', use pure English explanation with LaTeX for mathematical equations.
"""

btn_label = "පිළිතුර ලබාගන්න 🚀" if language == "Sinhala" else "Get Answer 🚀"

# 7. Button Action & AI Response Generation
if st.button(btn_label):
    if user_text or user_image:
        with st.spinner("Analyzing and generating answer..."):
            try:
                contents = [system_instruction]
                if user_text:
                    contents.append(user_text)
                if user_image:
                    contents.append(user_image)

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contents
                )
                
                st.markdown("### Answer / පිළිතුර:")
                st.write(response.text)
            except Exception as e:
                st.error(f"දෝෂයක් සිදු විය (Error): {str(e)}")
    else:
        warn_msg = "කරුණාකර ප්‍රශ්නයක් ටයිප් කරන්න නැතහොත් Photo එකක් Upload කරන්න!" if language == "Sinhala" else "Please enter a question or upload an image!"
        st.warning(warn_msg)

# 8. Footer (Created By)
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; padding: 10px;">
        <p>Created with ❤️ by <b>Janidu Kaveesha</b> | Powered by <b>Gemini AI</b> 🤖</p>
    </div>
    """,
    unsafe_allow_html=True
)