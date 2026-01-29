import stanza
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

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

analyzer = AnalyzerEngine(nlp_engine=nlp_engine, log_decision_process=True)
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

cv_md_path = 'test-resources/cv.md'
with open(cv_md_path, 'r', encoding='utf-8') as file:
    cv_text = file.read()
print(clean_cv_content(cv_text))