from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import base64
import os
import io
from PIL import Image
import fitz  # PyMuPDF
import google.generativeai as genai
import re


genai.configure(api_key=os.getenv("API_KEY"))


def get_gemini_response(input, pdf_content, prompt):
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    response = model.generate_content([input, pdf_content[0], prompt])
    return response.text

def input_pdf_setup(uploaded_file):
    """Convert PDF first page to image using PyMuPDF and return as base64."""
    if uploaded_file is not None:
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc[0]  # first page
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

#bg
def add_high_tech_bg():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url('https://images.unsplash.com/photo-1545486332-9e0999c535b2?w=500&auto=format&fit=crop&q=60');
            background-size: cover;
            background-attachment: fixed;
            color: #e0e0e0;
            font-family: 'Segoe UI', sans-serif;
        }
        .stApp::before {
            content:"";
            position:absolute;
            top:0;
            left:0;
            width:100%;
            height:100%;
            background: rgba(0,0,0,0.6);
            z-index:-1;
        }
        .stButton>button {
            background: linear-gradient(90deg, #00f0ff, #ff00f0);
            color:white;
            font-size:16px;
            font-weight:bold;
            border-radius:12px;
            padding:12px 25px;
            margin:5px;
            box-shadow: 0 0 10px #00f0ff, 0 0 20px #ff00f0;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            box-shadow: 0 0 20px #00f0ff, 0 0 30px #ff00f0;
            transform: scale(1.05);
        }
        .stTextArea textarea {
            border:2px solid #00f0ff;
            border-radius:12px;
            background-color: rgba(0,0,0,0.7);
            color:white;
            padding:10px;
        }
        .stExpanderHeader {
            font-weight:bold;
            font-size:18px;
            color:#00f0ff;
        }
        .stMarkdown p, .stMarkdown li {
            color:#e0e0e0;
            font-size:16px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


st.set_page_config(page_title="ATS Resume Expert", layout="wide")
add_high_tech_bg()

st.markdown(
    """
    <div style="background: linear-gradient(90deg, #00f0ff, #ff00f0);
                padding:20px;
                border-radius:15px;
                text-align:center;
                box-shadow: 0 0 20px #00f0ff, 0 0 20px #ff00f0;">
        <h1 style="color:white; font-family:'Segoe UI',sans-serif;">📄 ATS Resume Expert</h1>
        <p style="color:white; font-size:18px;">Evaluate your resume like a recruiter & ATS would</p>
    </div>
    """,
    unsafe_allow_html=True
)

col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("📝 Job Description")
    input_text = st.text_area("Paste the job description here:", key="input", height=250)

with col2:
    st.subheader("📂 Upload Resume")
    uploaded_file = st.file_uploader("Upload PDF only", type=["pdf"])
    if uploaded_file is not None:
        st.success("✅ Resume uploaded successfully!")


st.markdown("### 🔘 Choose an Action")
col1, col2, col3 = st.columns(3)
with col1:
    submit1 = st.button("📝 Tell Me About the Resume")
with col2:
    submit2 = st.button("💡 How Can I Improve my Skills")
with col3:
    submit3 = st.button("📊 Percentage Match")


input_prompt1 = """You are an experienced Technical Human Resource Manager...
Format in bullet points with headings: Overall Alignment, Strengths, Weaknesses, Recommendation."""
input_prompt2 = """You are a career development coach...
Format as actionable bullet points: Technical Skills, Soft Skills, Certifications, Tools."""
input_prompt3 = """You are a skilled ATS scanner...
Format clearly: Percentage Match, Missing Keywords, Final Thoughts."""


def display_response(prompt, title, color="#00f0ff"):
    if uploaded_file is None:
        st.error("⚠️ Please upload the resume")
        return
    pdf_content = input_pdf_setup(uploaded_file)
    response = get_gemini_response(prompt, pdf_content, input_text)
    with st.expander(f"{title}"):
        st.markdown(
            f"<div style='padding:15px;border-radius:12px;background-color:rgba(0,0,0,0.5);color:{color};'>{response}</div>",
            unsafe_allow_html=True
        )
    return response

if submit1:
    display_response(input_prompt1, "🔍 HR Evaluation Results")
elif submit2:
    display_response(input_prompt2, "💡 Skill Improvement Suggestions", color="#ff00f0")
elif submit3:
    response = display_response(input_prompt3, "📊 ATS Evaluation Details", color="#00fff0")
    try:
   
     matches = re.findall(r'(\d+)%', response)
     if matches:
        percent = int(matches[0])
        st.metric("ATS Match", f"{percent}%")
        st.progress(percent / 100)
     else:
        st.warning("⚠️ Could not extract % match automatically.")
    except Exception as e:
        st.warning(f"⚠️ Could not extract % match automatically. Error: {e}")

