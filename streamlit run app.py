import os
import requests
import streamlit as st
from PIL import Image
from google import genai

# 1. Page Configuration
st.set_page_config(page_title="A/L Science Master Tutor", layout="wide", page_icon="🎓")

# 2. CSS & Custom Styling
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@700;800&family=Orbitron:wght@800&display=swap');

    #bg-video {
        position: fixed;
        right: 0;
        bottom: 0;
        min-width: 100%;
        min-height: 100%;
        width: auto;
        height: auto;
        z-index: -1;
        object-fit: cover;
        opacity: 0.35;
    }
    .stApp {
        background: transparent !important;
    }

    .custom-title {
        font-family: 'Orbitron', 'Poppins', sans-serif;
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ff8a00, #e52e71, #00c6ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 0px 15px rgba(255, 255, 255, 0.2);
        margin-bottom: 5px;
    }

    .custom-subtitle {
        font-family: 'Poppins', sans-serif;
        color: #e0e0e0;
        font-size: 1.1rem;
        margin-bottom: 25px;
    }
    </style>
    
    <video autoplay muted loop id="bg-video">
      <source src="https://assets.mixkit.co/videos/preview/mixkit-stars-in-space-1610-large.mp4" type="video/mp4">
    </video>
    """,
    unsafe_allow_html=True
)

# 3. Lottie Animation Helper
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        return None
    return None

try:
    from streamlit_lottie import st_lottie
    lottie_anim = load_lottieurl("https://assets2.lottiefiles.com/packages/lf20_DMgB15.json")
except ImportError:
    st_lottie = None
    lottie_anim = None

# 4. API Key Verification
API_KEY = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

# 5. Sidebar - Settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    language = st.radio("Language / භාෂාව තෝරන්න:", ["Sinhala", "English"])
    
    if language == "Sinhala":
        subj_label = "විෂය තෝරන්න:"
        input_label = "ප්‍රශ්නය ලබාදෙන ආකාරය:"
        opt_text = "✍️ Text (ලියන්න)"
        opt_photo = "📷 Photo Upload (ඡායාරූපයක්)"
    else:
        subj_label = "Select Subject:"
        input_label = "Select Input Type:"
        opt_text = "✍️ Text"
        opt_photo = "📷 Photo Upload"

    subject = st.selectbox(subj_label, ["Combined Mathematics", "Physics", "Chemistry"])
    input_type = st.radio(input_label, [opt_text, opt_photo])

    st.markdown("---")
    st.markdown("### 👨‍💻 Developed by")
    st.write("**Janidu Kaveesha**")

# 6. Title Header
col1, col2 = st.columns([2, 1])

with col1:
    if language == "Sinhala":
        st.markdown('<h1 class="custom-title">🎓 A/L MASTER TUTOR</h1>', unsafe_allow_html=True)
        st.markdown('<p class="custom-subtitle">Combined Maths | Physics | Chemistry — LaTeX Math විසඳුම් සමඟින්</p>', unsafe_allow_html=True)
    else:
        st.markdown('<h1 class="custom-title">🎓 A/L MASTER TUTOR</h1>', unsafe_allow_html=True)
        st.markdown('<p class="custom-subtitle">Combined Maths | Physics | Chemistry — Step-by-Step LaTeX Solutions</p>', unsafe_allow_html=True)

with col2:
    if st_lottie and lottie_anim:
        st_lottie(lottie_anim, height=150, key="tutor_anim")

# 7. Inputs
user_image = None
user_text = ""

if opt_photo in input_type:
    prompt_img_label = "ප්‍රශ්නයේ Photo එක Upload කරන්න:" if language == "Sinhala" else "Upload Question Photo:"
    uploaded_file = st.file_uploader(prompt_img_label, type=["jpg", "jpeg", "png"])
    if uploaded_file:
        user_image = Image.open(uploaded_file)
        st.image(user_image, caption="Uploaded Image", use_column_width=True)

prompt_txt_label = "ඔබගේ ප්‍රශ්නය මෙහි ටයිප් කරන්න:" if language == "Sinhala" else "Type your question here:"
user_text = st.text_area(prompt_txt_label, height=120)

# 8. Session State Setup (පිළිතුර අතුරුදහන් වීම වැළැක්වීමට)
if "ai_response" not in st.session_state:
    st.session_state.ai_response = None

btn_label = "පිළිතුර ලබාගන්න 🚀" if language == "Sinhala" else "Get Answer 🚀"

if st.button(btn_label):
    if not API_KEY:
        st.error("⚠️ Gemini API Key එක හමු නොවීය! Streamlit Cloud හි Settings -> Secrets වල GEMINI_API_KEY එකතු කර ඇත්දැයි පරීක්ෂා කරන්න.")
    elif not user_text and not user_image:
        warn_msg = "කරුණාකර ප්‍රශ්නයක් ටයිප් කරන්න නැතහොත් Photo එකක් Upload කරන්න!" if language == "Sinhala" else "Please enter a question or upload an image!"
        st.warning(warn_msg)
    else:
        with st.spinner("Gemini AI මගින් විසඳුම සකස් කරමින් පවතී... / Generating solution..."):
            try:
                client = genai.Client(api_key=API_KEY)

                system_prompt = f"""
                You are an expert Sri Lankan G.C.E. A/L Science stream tutor in {subject}.
                Solve the student's question clearly step-by-step strictly in {language} language.
                Always use standard LaTeX formatting ($...$ for inline math and $$...$$ for block math equations) for all variables, formulas, and math expressions.
                """

                contents = [system_prompt]
                if user_text:
                    contents.append(f"Question: {user_text}")
                if user_image:
                    contents.append(user_image)

                # API Call
                res = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=contents
                )
                
                # State එකට පිළිතුර Save කිරීම
                st.session_state.ai_response = res.text

            except Exception as e:
                st.error(f"දෝෂයක් සිදු විය (Error): {str(e)}")

# 9. Output Area (Session State එකෙන් Display කිරීම)
if st.session_state.ai_response:
    st.success("විසඳුම සාර්ථකව සකස් කරන ලදී!" if language == "Sinhala" else "Solution generated successfully!")
    st.markdown("---")
    st.markdown("### 💡 විසඳුම (Solution):")
    st.markdown(st.session_state.ai_response)

# 10. Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #ffffff; padding: 10px;">
        <p>Created with ❤️ by <b>Janidu Kaveesha</b> | Powered by <b>Gemini AI</b> 🤖</p>
    </div>
    """,
    unsafe_allow_html=True
)