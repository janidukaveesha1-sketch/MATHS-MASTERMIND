import os
import requests
import streamlit as st
from google import genai

# 1. Page Configuration
st.set_page_config(
    page_title="A/L Master Tutor",
    page_icon="🎓",
    layout="wide"
)

# 2. CSS & Background Video Loop (Direct Working Space URL)
st.markdown(
    """
    <style>
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
    </style>
    
    <video autoplay muted loop id="bg-video">
      <source src="https://assets.mixkit.co/videos/preview/mixkit-stars-in-space-1610-large.mp4" type="video/mp4">
    </video>
    """,
    unsafe_allow_html=True
)

# 3. Lottie Animation Helper Function
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

# 4. Main UI Header
col1, col2 = st.columns([2, 1])

with col1:
    st.title("🎓 A/L Master Tutor")
    st.write("A/L Combined Mathematics, Physics & Chemistry Tutor with LaTeX Support.")

with col2:
    if st_lottie and lottie_anim:
        st_lottie(lottie_anim, height=150, key="tutor_anim")

# 5. Sidebar Options (Subject & Language Selectors)
st.sidebar.title("⚙️ App Settings")

subject = st.sidebar.selectbox(
    "📚 Select Subject / විෂය තෝරන්න:",
    ["Combined Mathematics", "Physics", "Chemistry"]
)

language = st.sidebar.radio(
    "🌐 Select Response Language / භාෂාව තෝරන්න:",
    ["Sinhala", "English"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 👨‍💻 Developed by")
st.sidebar.write("**Janidu Kaveesha**")

# 6. Question Input Area
user_query = st.text_area(f"ඔබගේ {subject} ප්‍රශ්නය මෙතන Type කරන්න ({language}):", height=120)

if st.button("🚀 විසඳුම ලබාගන්න (Solve Problem)"):
    # API Key එක Check කිරීම
    api_key = None
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    elif os.environ.get("GEMINI_API_KEY"):
        api_key = os.environ.get("GEMINI_API_KEY")

    if not user_query.strip():
        st.warning("කරුණාකර ප්‍රශ්නයක් ඇතුළත් කරන්න.")
    elif not api_key:
        st.error("Gemini API Key එක සකස් කර නැත! Streamlit Cloud Secrets වලට GEMINI_API_KEY එකතු කරන්න.")
    else:
        with st.spinner("Gemini AI මගින් විසඳුම සකස් කරමින් පවතී..."):
            try:
                client = genai.Client(api_key=api_key)
                
                # Dynamic System Prompt
                prompt = f"""
                You are an expert Sri Lankan G.C.E. Advanced Level {subject} tutor.
                Solve the following student query step-by-step strictly in {language} language.
                Use standard LaTeX formatting ($...$ for inline math equations and $$...$$ for block equations) for all variables, formulas, and math expressions.
                
                Question:
                {user_query}
                """
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                
                st.success("විසඳුම සාර්ථකව සකස් කරන ලදී!")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"දෝෂයක් සිදු විය: {str(e)}")

# 7. Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #ffffff; padding: 10px;">
        <p>Created with ❤️ by <b>Janidu Kaveesha</b> | Powered by <b>Gemini AI</b> 🤖</p>
    </div>
    """,
    unsafe_allow_html=True
)