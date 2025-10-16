import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import pdfplumber

# Load environment variables
load_dotenv()

# Configure Google Gemini AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        # Try direct text extraction
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text

        if text.strip():
            return text.strip()
    except Exception as e:
        print(f"Direct text extraction failed: {e}")


# Function to get response from Gemini AI
def analyze_resume(resume_text, job_description=None):
    if not resume_text:
        return {"error": "Resume text is required for analysis."}
    
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    base_prompt = f"""
     # Context:
    - You are an AI Resume Analyzer, you will be given Candidate's resume and Job Description of the role he is applying for.

    # Instruction:
    - Analyze candidate's resume based on the possible points that can be extracted from job description,and give your evaluation on each point with the criteria below:  
    - Consider all points like required skills, experience,etc that are needed for the job role.
    - Calculate the score to be given (out of 5) for every point based on evaluation at the beginning of each point with a detailed explanation.  
    - If the resume aligns with the job description point, mark it with ✅ and provide a detailed explanation.  
    - If the resume doesn't align with the job description point, mark it with ❌ and provide a reason for it.  
    - If a clear conclusion cannot be made, use a ⚠️ sign with a reason.  
    - The Final Heading should be "Suggestions to improve your resume:" and give where and what the candidate can improve to be selected for that job role.

    Resume:
    {resume_text}
    """

    if job_description:
        base_prompt += f"""
        Additionally, compare this resume to the following job description:
        
        Job Description:
        {job_description}
        
        # Output:
        - Each any every point should be given a score (example: 3/5 ). 
        - Mention the scores and  relevant emoji at the beginning of each point and then explain the reason.
            """

    response = model.generate_content(base_prompt)

    analysis = response.text.strip()
    return analysis


# Streamlit app

st.set_page_config(page_title="Resume Analyzer", layout="wide")
# Title
st.title("AI Resume Analyzer")
st.write("Analyze your resume and match it with job descriptions using Google Gemini AI.")

col1 , col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
with col2:
    job_description = st.text_area("Enter Job Description:", placeholder="Paste the job description here...")

if uploaded_file is not None:
    st.success("Resume uploaded successfully!")
else:
    st.warning("Please upload a resume in PDF format.")


st.markdown("<div style= 'padding-top: 10px;'></div>", unsafe_allow_html=True)
if uploaded_file:
    # Save uploaded file locally for processing
    with open("uploaded_resume.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    # Extract text from PDF
    resume_text = extract_text_from_pdf("uploaded_resume.pdf")

    if st.button("Analyze Resume"):
        with st.spinner("Analyzing resume..."):
            try:
                # Analyze resume
                analysis = analyze_resume(resume_text, job_description)
                st.success("Analysis complete!")
                st.write(analysis)
            except Exception as e:
                st.error(f"Analysis failed: {e}")

#Footer
st.markdown("---")
st.markdown("""<p style= 'text-align: center;' >Powered by <b>Streamlit</b> and <b>Google Gemini AI</b> | Developed by <a href="www.linkedin.com/in/raja-kumar-thakur-577047220"  target="_blank" style='text-decoration: none; color: #FFFFFF'><b>Raja Kumar Thakur</b></a></p>""", unsafe_allow_html=True)
