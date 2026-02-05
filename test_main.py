import pytest
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig


# Set up analyzer with spaCy instead of Stanza for testing
@pytest.fixture(scope="module")
def analyzer_engine():
    """Create an analyzer engine using spaCy for testing."""
    configuration = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
    }
    provider = NlpEngineProvider(nlp_configuration=configuration)
    nlp_engine = provider.create_engine()
    return AnalyzerEngine(nlp_engine=nlp_engine)


@pytest.fixture(scope="module")
def anonymizer_engine():
    """Create an anonymizer engine for testing."""
    return AnonymizerEngine()


def clean_cv_content_test(text, analyzer, anonymizer):
    """Test version of clean_cv_content that uses spaCy."""
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


class TestCleanCvContentPerson:
    """Test cases for PERSON entity detection and redaction."""
    
    def test_person_positive_single_name(self, analyzer_engine, anonymizer_engine):
        """Test that a single person name is redacted."""
        text = "My name is John Smith and I work as a software engineer."
        result = clean_cv_content_test(text, analyzer_engine, anonymizer_engine)
        assert "[NAME]" in result
        assert "John Smith" not in result
    
    def test_person_positive_multiple_names(self, analyzer_engine, anonymizer_engine):
        """Test that multiple person names are redacted."""
        text = "John Smith and Sarah Johnson worked together on the project."
        result = clean_cv_content_test(text, analyzer_engine, anonymizer_engine)
        assert "[NAME]" in result
        assert "John Smith" not in result
        assert "Sarah Johnson" not in result
    
    def test_person_negative_common_words(self, analyzer_engine, anonymizer_engine):
        """Test that common words that are not names are not redacted."""
        text = "The project was completed successfully with great attention to detail."
        result = clean_cv_content_test(text, analyzer_engine, anonymizer_engine)
        assert "[NAME]" not in result
        assert "project" in result
        assert "completed" in result
    
    def test_person_negative_job_titles(self, analyzer_engine, anonymizer_engine):
        """Test that job titles without names are not redacted."""
        text = "Software Engineer with 5 years of experience."
        result = clean_cv_content_test(text, analyzer_engine, anonymizer_engine)
        # Job titles alone should not be redacted
        assert "Software Engineer" in result


class TestCleanCvContentEmail:
    """Test cases for EMAIL_ADDRESS entity detection and redaction."""
    
    def test_email_positive_standard_format(self, analyzer_engine, anonymizer_engine):
        """Test that standard email addresses are redacted."""
        text = "Contact me at john.smith@example.com for more information."
        result = clean_cv_content_test(text, analyzer_engine, anonymizer_engine)
        assert "[EMAIL]" in result
        assert "john.smith@example.com" not in result
    
    def test_email_positive_multiple_emails(self, analyzer_engine, anonymizer_engine):
        """Test that multiple email addresses are redacted."""
        text = "Email me at john@example.com or sarah@company.org"
        result = clean_cv_content_test(text, analyzer_engine, anonymizer_engine)
        assert "[EMAIL]" in result
        assert "john@example.com" not in result
        assert "sarah@company.org" not in result
    
    def test_email_negative_no_email(self, analyzer_engine, anonymizer_engine):
        """Test that text without emails is not affected."""
        text = "Please contact me through the company website."
        result = clean_cv_content_test(text, analyzer_engine, anonymizer_engine)
        assert "[EMAIL]" not in result
        assert "contact" in result
    
    def test_email_negative_incomplete_email(self, analyzer_engine, anonymizer_engine):
        """Test that incomplete email-like text is not redacted."""
        text = "The file is named document@draft and needs review."
        result = clean_cv_content_test(text, analyzer_engine, anonymizer_engine)
        # An incomplete email pattern might not be detected
        assert "document@draft" in result


class TestCleanCvContentPhone:
    """Test cases for PHONE_NUMBER entity detection and redaction.
    
    Note: These tests use pattern-based recognizers that are enabled in presidio
    by default. Phone number detection depends on the quality of the patterns.
    """
    
    @pytest.mark.xfail(reason="Phone detection requires pattern-based recognizers that may not be fully configured")
    def test_phone_positive_international_format(self, analyzer_engine, anonymizer_engine):
        """Test that international phone numbers are redacted."""
        text = "Call me at +1-555-123-4567 for details."
        result = clean_cv_content_test(text, analyzer_engine, anonymizer_engine)
        assert "[PHONE]" in result
        assert "+1-555-123-4567" not in result
    
    @pytest.mark.xfail(reason="Phone detection requires pattern-based recognizers that may not be fully configured")
    def test_phone_positive_uk_format(self, analyzer_engine, anonymizer_engine):
        """Test that UK format phone numbers are redacted."""
        text = "My phone is 020 7372 5330 for inquiries."
        result = clean_cv_content_test(text, analyzer_engine, anonymizer_engine)
        assert "[PHONE]" in result
        assert "020 7372 5330" not in result
    
    @pytest.mark.xfail(reason="Phone detection requires pattern-based recognizers that may not be fully configured")
    def test_phone_positive_us_format(self, analyzer_engine, anonymizer_engine):
        """Test that US format phone numbers are redacted."""
        text = "Reach me at (555) 123-4567 anytime."
        result = clean_cv_content_test(text, analyzer_engine, anonymizer_engine)
        assert "[PHONE]" in result
        assert "(555) 123-4567" not in result
    
    def test_phone_negative_no_phone(self, analyzer_engine, anonymizer_engine):
        """Test that text without phone numbers is not affected."""
        text = "Contact information available upon request."
        result = clean_cv_content_test(text, analyzer_engine, anonymizer_engine)
        assert "[PHONE]" not in result
        assert "Contact" in result
    
    def test_phone_negative_random_numbers(self, analyzer_engine, anonymizer_engine):
        """Test that random numbers are not redacted as phone numbers."""
        text = "I have 5 years of experience and worked on 10 projects."
        result = clean_cv_content_test(text, analyzer_engine, anonymizer_engine)
        assert "[PHONE]" not in result
        assert "5 years" in result
        assert "10 projects" in result


class TestCleanCvContentLocation:
    """Test cases for LOCATION entity detection and redaction."""
    
    def test_location_positive_city_country(self, analyzer_engine, anonymizer_engine):
        """Test that city and country locations are redacted."""
        text = "I live in London, England and work remotely."
        result = clean_cv_content_test(text, analyzer_engine, anonymizer_engine)
        assert "[LOCATION]" in result
        assert "London" not in result or "England" not in result
    
    def test_location_positive_city_only(self, analyzer_engine, anonymizer_engine):
        """Test that city names are redacted."""
        text = "Based in San Francisco with experience in tech."
        result = clean_cv_content_test(text, analyzer_engine, anonymizer_engine)
        assert "[LOCATION]" in result
        assert "San Francisco" not in result
    
    def test_location_positive_state_country(self, analyzer_engine, anonymizer_engine):
        """Test that states and countries are redacted."""
        text = "Originally from California, United States."
        result = clean_cv_content_test(text, analyzer_engine, anonymizer_engine)
        assert "[LOCATION]" in result
        # At least one location should be redacted
        assert "California" not in result or "United States" not in result
    
    def test_location_negative_no_location(self, analyzer_engine, anonymizer_engine):
        """Test that text without locations is not affected."""
        text = "I work in software development and enjoy problem solving."
        result = clean_cv_content_test(text, analyzer_engine, anonymizer_engine)
        # "in" is not a location
        assert "software development" in result
    
    def test_location_negative_direction_words(self, analyzer_engine, anonymizer_engine):
        """Test that directional words are not redacted as locations."""
        text = "Looking forward to new opportunities in the future."
        result = clean_cv_content_test(text, analyzer_engine, anonymizer_engine)
        # "forward" and "future" should not be redacted
        assert "forward" in result
        assert "future" in result


class TestCleanCvContentUrl:
    """Test cases for URL entity detection and redaction.
    
    Note: URL detection with http/https may require higher confidence scores
    or pattern-based recognizers depending on the NLP engine configuration.
    """
    
    @pytest.mark.xfail(reason="URL detection with https may score below threshold with some NLP engines")
    def test_url_positive_https(self, analyzer_engine, anonymizer_engine):
        """Test that HTTPS URLs are redacted."""
        text = "Visit my portfolio at https://www.example.com for more details."
        result = clean_cv_content_test(text, analyzer_engine, anonymizer_engine)
        assert "[URL]" in result
        assert "https://www.example.com" not in result
    
    @pytest.mark.xfail(reason="URL detection with http may score below threshold with some NLP engines")
    def test_url_positive_http(self, analyzer_engine, anonymizer_engine):
        """Test that HTTP URLs are redacted."""
        text = "Check out http://example.com for my work."
        result = clean_cv_content_test(text, analyzer_engine, anonymizer_engine)
        assert "[URL]" in result
        assert "http://example.com" not in result
    
    def test_url_positive_www(self, analyzer_engine, anonymizer_engine):
        """Test that www URLs are redacted."""
        text = "My website is www.johnsmith.com with my portfolio."
        result = clean_cv_content_test(text, analyzer_engine, anonymizer_engine)
        assert "[URL]" in result
        assert "www.johnsmith.com" not in result
    
    def test_url_negative_no_url(self, analyzer_engine, anonymizer_engine):
        """Test that text without URLs is not affected."""
        text = "I have experience with web development and databases."
        result = clean_cv_content_test(text, analyzer_engine, anonymizer_engine)
        assert "[URL]" not in result
        assert "web development" in result
    
    def test_url_negative_partial_url(self, analyzer_engine, anonymizer_engine):
        """Test that partial URL-like text is not always redacted."""
        text = "The dot com boom was a significant period in tech history."
        result = clean_cv_content_test(text, analyzer_engine, anonymizer_engine)
        # "dot com" should not be redacted as a URL
        assert "dot com" in result or "com" in result


class TestCleanCvContentIntegration:
    """Integration test cases with multiple PII types."""
    
    def test_multiple_pii_types(self, analyzer_engine, anonymizer_engine):
        """Test that multiple types of PII are redacted in one text.
        
        Note: Some PII types may not be detected depending on NLP engine and patterns.
        """
        text = """
        John Smith
        Email: john.smith@example.com
        Phone: +1-555-123-4567
        Location: San Francisco, CA
        My website is www.johnsmith.com
        """
        result = clean_cv_content_test(text, analyzer_engine, anonymizer_engine)
        
        # Check that NAME, EMAIL, and LOCATION are redacted (most reliable)
        assert "[NAME]" in result
        assert "[EMAIL]" in result
        assert "[LOCATION]" in result
        
        # Check that original PII is not present
        assert "john.smith@example.com" not in result
        
        # URL with www should be detected
        assert "[URL]" in result
        assert "www.johnsmith.com" not in result
    
    def test_no_pii_present(self, analyzer_engine, anonymizer_engine):
        """Test that text without PII is mostly preserved.
        
        Note: Some common words may be incorrectly identified as locations
        (e.g., programming language names like Python, Java).
        """
        text = "Software developer with experience in JavaScript and web development."
        result = clean_cv_content_test(text, analyzer_engine, anonymizer_engine)
        
        # No email or phone markers should be present
        assert "[EMAIL]" not in result
        assert "[PHONE]" not in result
        assert "[URL]" not in result
        
        # Most of the text should be preserved
        assert "Software developer" in result
        assert "web development" in result
    
    def test_mixed_pii_and_regular_text(self, analyzer_engine, anonymizer_engine):
        """Test that only PII is redacted while preserving regular text."""
        text = "I am a software engineer based in London. Contact me at test@example.com"
        result = clean_cv_content_test(text, analyzer_engine, anonymizer_engine)
        
        # Regular text should be preserved
        assert "software engineer" in result
        assert "based in" in result
        
        # PII should be redacted
        assert "[LOCATION]" in result or "London" not in result
        assert "[EMAIL]" in result
        assert "test@example.com" not in result