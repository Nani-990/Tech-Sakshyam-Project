import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Add yellow background color
st.markdown(
    """
    <style>
        [data-testid="stAppViewContainer"] {
            background-color: #FFFF99; /* Light Yellow */
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Function to extract text from PDF
def extract_text_from_pdf(file):
    pdf = PdfReader(file)
    text = ""
    for page in pdf.pages:
        extracted_text = page.extract_text()
        if extracted_text:
            text += extracted_text
    return text

# Function to rank resumes
def rank_resume(job_description, resumes):
    documents = [job_description] + resumes
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(documents).toarray()
    
    job_description_vector = vectors[0]
    resume_vectors = vectors[1:]

    # Compute similarity
    cosine_similarities = cosine_similarity([job_description_vector], resume_vectors).flatten()
    return cosine_similarities

# Streamlit UI
st.title("AI Resume Screening & Candidate Ranking System")

st.header("Job Description")
job_description = st.text_area("Enter the job description")

st.header("Upload Resumes")
uploaded_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)

if uploaded_files and job_description:
    st.header("Ranking Resumes")

    resumes = []
    for file in uploaded_files:
        text = extract_text_from_pdf(file)
        resumes.append(text)
    
    # Rank resumes
    scores = rank_resume(job_description, resumes)

    # Define a threshold for a good match
    threshold = 0.5  # Adjust this value if needed

    # Create DataFrame for results
    results = pd.DataFrame({
        "Resume": [file.name for file in uploaded_files],
        "Score": scores
    })

    # Add a column to indicate if it's a good match
    results["Match Status"] = results["Score"].apply(lambda x: "✅ Good Match" if x >= threshold else "❌ Not a Match")

    # Sort results by highest score
    results = results.sort_values(by="Score", ascending=False).reset_index(drop=True)

    # Add Rank column starting from 1
    results.index += 1
    results.insert(0, "Rank", results.index)

    # Display results
    st.write(results)

    # Show only good matches
    good_matches = results[results["Score"] >= threshold]
    
    if not good_matches.empty:
        st.subheader("Best Matches Based on Job Description")
        st.write(good_matches)
    else:
        st.subheader("No resumes matched the job description well.")
