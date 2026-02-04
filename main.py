from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
import fitz  # PyMuPDF

# Use default analyzer with pattern-based detection (no NLP model needed)
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

def clean_cv_content(text):
    analysis_results = analyzer.analyze(
        text=text, 
        entities=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "LOCATION", "URL"], 
        language='en',
        score_threshold=0.85
    )

    operators = {
        "PERSON": OperatorConfig("replace", {"new_value": "[NAME]"}),
        "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "[EMAIL]"}),
        "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "[PHONE]"}),
        "LOCATION": OperatorConfig("replace", {"new_value": "[LOCATION]"}),
        "URL": OperatorConfig("replace", {"new_value": "[URL]"}),
    }

    redacted_result = anonymizer.anonymize(
        text=text,
        analyzer_results=analysis_results,
        operators=operators
    )

    return redacted_result.text

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def redact_pdf(input_pdf_path, output_pdf_path):
    """Redact PII from a PDF and save the redacted version."""
    # Extract text from all pages
    full_text = extract_text_from_pdf(input_pdf_path)
    
    # Analyze the text for PII
    analysis_results = analyzer.analyze(
        text=full_text, 
        entities=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "LOCATION", "URL"], 
        language='en',
        score_threshold=0.85
    )
    
    # Create a mapping of original text to redacted text
    operators = {
        "PERSON": OperatorConfig("replace", {"new_value": "[NAME]"}),
        "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "[EMAIL]"}),
        "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "[PHONE]"}),
        "LOCATION": OperatorConfig("replace", {"new_value": "[LOCATION]"}),
        "URL": OperatorConfig("replace", {"new_value": "[URL]"}),
    }
    
    redacted_result = anonymizer.anonymize(
        text=full_text,
        analyzer_results=analysis_results,
        operators=operators
    )
    
    # Create a new PDF with redacted text
    # For simplicity, we'll create a new document with the redacted text
    # A more sophisticated approach would overlay redactions on the original PDF
    output_doc = fitz.open()  # Create a new empty PDF
    
    # Add a page with the redacted text
    page = output_doc.new_page(width=612, height=792)  # Letter size
    
    # Add the redacted text to the page with error handling
    rect = fitz.Rect(50, 50, 562, 742)  # Margins
    try:
        result = page.insert_textbox(rect, redacted_result.text, fontsize=11, fontname="helv", align=0)
        if result < 0:
            print(f"Warning: Text may have been truncated. Not all content fit in the text box.")
    except Exception as e:
        print(f"Error inserting text into PDF: {e}")
        output_doc.close()
        raise
    
    # Save the output PDF
    output_doc.save(output_pdf_path)
    output_doc.close()
    
    return redacted_result.text

cv_pdf_path = 'test-resources/cv.pdf'
output_pdf_path = 'test-resources/cv_redacted.pdf'

print("Redacting PDF...")
redacted_text = redact_pdf(cv_pdf_path, output_pdf_path)
print(f"\nRedacted PDF saved to: {output_pdf_path}")
print("\nRedacted text preview:")
print(redacted_text[:500] + "..." if len(redacted_text) > 500 else redacted_text)