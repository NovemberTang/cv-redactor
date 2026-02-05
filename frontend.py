import streamlit as st
import os
from backend import redact_pdf

st.title("CV Redactor")
st.write("Upload a PDF CV to redact personally identifiable information (PII)")

# File uploader
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Create a temporary directory if it doesn't exist
    temp_dir = "/tmp/cv-redactor"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Save uploaded file temporarily
    input_path = os.path.join(temp_dir, "uploaded.pdf")
    output_path = os.path.join(temp_dir, "redacted.pdf")
    
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success("File uploaded successfully!")
    
    # Add a button to process the PDF
    if st.button("Redact PII"):
        with st.spinner("Redacting PDF..."):
            try:
                result = redact_pdf(input_path, output_path)
                st.success(result)
                
                # Read the redacted PDF
                with open(output_path, "rb") as f:
                    pdf_bytes = f.read()
                
                # Download button
                st.download_button(
                    label="Download Redacted CV",
                    data=pdf_bytes,
                    file_name="cv_redacted.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Error during redaction: {str(e)}")
