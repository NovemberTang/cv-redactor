from backend import redact_pdf

if __name__ == "__main__":
    cv_pdf_path = 'test-resources/cv.pdf'
    output_pdf_path = 'test-resources/cv_redacted.pdf'
    
    print("Redacting PDF...")
    redacted_text = redact_pdf(cv_pdf_path, output_pdf_path)
    print(f"\nRedacted PDF saved to: {output_pdf_path}")
    print("\nRedacted text preview:")
    print(redacted_text[:500] + "..." if len(redacted_text) > 500 else redacted_text)