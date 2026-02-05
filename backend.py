import stanza
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
import fitz  # PyMuPDF

# Global variables for lazy initialization
_analyzer = None
_anonymizer = None

def _initialize_engines():
    """Lazy initialization of analyzer and anonymizer engines."""
    global _analyzer, _anonymizer
    
    if _analyzer is not None and _anonymizer is not None:
        return
    
    # Auto-download Stanza English model if not present
    try:
        stanza.Pipeline('en', download_method=None)
    except Exception:
        print("Downloading Stanza English model (one-time setup)...")
        stanza.download('en')

    configuration = {
        "nlp_engine_name": "stanza",
        "models": [{"lang_code": "en", "model_name": "en"}],
    }
    provider = NlpEngineProvider(nlp_configuration=configuration)
    nlp_engine = provider.create_engine()

    _analyzer = AnalyzerEngine(nlp_engine=nlp_engine, log_decision_process=True)
    _anonymizer = AnonymizerEngine()

def clean_cv_content(text):
    _initialize_engines()
    analysis_results = _analyzer.analyze(
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

    redacted_result = _anonymizer.anonymize(
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
    """Redact PII from a PDF by drawing black boxes over sensitive information."""
    _initialize_engines()
    # Open the original PDF
    doc = fitz.open(input_pdf_path)
    
    # Process each page
    for page_num, page in enumerate(doc):
        # Extract text from the page
        page_text = page.get_text()
        
        # Analyze the text for PII
        analysis_results = _analyzer.analyze(
            text=page_text, 
            entities=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "LOCATION", "URL"], 
            language='en',
            score_threshold=0.85
        )

        # For each detected entity, draw a black box over it
        for result in analysis_results:
            print(f"Page {page_num + 1}: Detected {result.entity_type} - '{page_text[result.start:result.end]}' (score: {result.score:.2f})")
            print(f"Entity spans from index {result.start} to {result.end} in the page text.")
            # Get the text that needs to be redacted
            redacted_text = page_text[result.start:result.end]
            print(f"Redacting text: '{redacted_text}'")

            # Search for the text in the page and draw black boxes
            text_dict = page.get_text("dict")
            for block in text_dict["blocks"]:
                if block["type"] == 0:  # Text block
                    for line in block["lines"]:
                        for span in line["spans"]:
                            span_text = span["text"]
                            # Check if this span contains the sensitive text
                            if redacted_text in span_text or any(word in span_text for word in redacted_text.split()):
                                # Draw a black rectangle over the sensitive text
                                rect = fitz.Rect(span["bbox"])
                                page.draw_rect(rect, color=None, fill=(0, 0, 0))
    
    # Save the redacted PDF
    doc.save(output_pdf_path)
    doc.close()
    
    return f"PDF redacted and saved to {output_pdf_path}"
