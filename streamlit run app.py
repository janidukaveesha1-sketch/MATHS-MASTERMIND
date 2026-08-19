import os
import re
import streamlit as st
from PIL import Image
from google import genai
from google.genai import types

# Page Config (අකුරු සහ Layout එක සකස් කිරීම)
st.set_page_config(page_title="A/L Science Master Tutor", layout="wide")

st.title("🎓 A/L Master Tutor (Maths | Physics | Chemistry)")
st.write("අතින් ලියන නිවැරදි ගණිතමය සංකේත (LaTeX Math) සහ Live Visual Animations සමඟින්")

# API Key එක
# Streamlit Secrets වලින් API Key එක ලබාගැනීම
API_KEY = st.secrets["GEMINI_API_KEY"]

# Sidebar - Settings
with st.sidebar:
    st.header("⚙️ Settings")
    language = st.radio("Language / භාෂාව තෝරන්න:", ["Sinhala", "English"])
    subject = st.selectbox("විෂය තෝරන්න:", ["Combined Mathematics", "Physics", "Chemistry"])
    input_type = st.radio("ප්‍රශ්නය ලබාදෙන ආකාරය:", ["Text", "Photo Upload"])

user_image = None
user_text = ""

if input_type == "Photo Upload":
    uploaded_file = st.file_uploader("ප්‍රශ්නයේ Photo එක Upload කරන්න", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        user_image = Image.open(uploaded_file)
        st.image(user_image, caption="Uploaded Image", use_column_width=True)
    user_text = st.text_input("අමතර විස්තර/උපදෙස් (අවශ්‍ය නම් පමණක්):")
else:
    user_text = st.text_area("ඔබගේ ප්‍රශ්නය මෙතන Type කරන්න:", height=150)

# Submit Button
if st.button("🚀 විසඳුම ලබාගන්න (Solve & Animate)"):
    if API_KEY == "YOUR_GEMINI_API_KEY_HERE" or not API_KEY.strip():
        st.error("❌ කරුණාකර නිවැරදි Gemini API Key එක ඇතුළත් කරන්න.")
    elif not user_text and not user_image:
        st.warning("⚠️ කරුණාකර ප්‍රශ්නයක් හෝ Image එකක් ලබාදෙන්න.")
    else:
        try:
            client = genai.Client(api_key=API_KEY)

            system_prompt = f"""
            ඔබ ශ්‍රී ලංකාවේ A/L {subject} ප්‍රවීණ ආචාර්යවරයෙකි.
            ලබාදී ඇති ප්‍රශ්නයට පිළිතුරු සපයන විට:
            1. **ගණිතමය සංකේත සහ සූත්‍ර (Math Symbols & Formulas):** පරිගණක සංකේත (*, /, **) වෙනුවට අතින් ලියන ක්‍රමයටම LaTeX භාවිත කරන්න (උදා: \\frac{{a}}{{b}}, \\sqrt{{x}}, x^2, \\times, \\int, \\theta).
            2. **මූලික සිද්ධාන්ත (Core Theory):** සිංහලෙන් පැහැදිලි කරන්න.
            3. **පියවරෙන් පියවර විසඳීම (Step-by-Step Solution):** සියලු සුළු කිරීම් අතින් ලියන සංකේත සහිතව දක්වන්න.
            4. **Visual Simulation:** ප්‍රස්ථාර/Animations සඳහා runnable Python code එකක් වෙනම ```python ``` block එකක් ඇතුළත ලබාදෙන්න (plt.show() රහිතව, st.pytest/st.pyplot සඳහා සූදානම් කර).
            """

            contents = []
            if user_image:
                contents.append(user_image)
            contents.append(user_text if user_text.strip() else f"Solve {subject} problem.")

            with st.spinner("⚡ විසඳුම සහ ප්‍රස්ථාර සකස් වෙමින් පවතී..."):
                response = client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.1
                    )
                )

                full_response = response.text

                # Display Response with LaTeX Math
                st.markdown("### 📝 විසඳුම සහ සිද්ධාන්ත පැහැදිලි කිරීම:")
                st.markdown(full_response)

                # Execute Matplotlib Code inside Web App
                python_code_match = re.search(r"```python(.*?)```", full_response, re.DOTALL)
                if python_code_match:
                    code = python_code_match.group(1).strip()
                    st.markdown("### 🎬 Visual Simulation / Graph:")
                    
                    # Safe execution for Streamlit rendering
                    exec_scope = {}
                    exec(code, exec_scope)
                    
                    import matplotlib.pyplot as plt
                    st.pyplot(plt.gcf())

        except Exception as e:
            st.error(f"❌ දෝෂයක් සිදු විය: {e}")