"""Pytest configuration for test suite."""
import pytest
import sys
from unittest.mock import MagicMock, Mock, patch


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Set up test environment with necessary mocks and configurations.
    This fixture runs automatically for all tests.
    
    Mocks the stanza module to prevent automatic model downloads during test execution.
    The main module (main.py) attempts to initialize Stanza on import, which requires
    downloading large language models. By mocking stanza, we prevent this behavior
    and allow tests to use spaCy as an alternative NLP engine instead.
    """
    # Mock stanza to prevent it from being imported by main module
    stanza_mock = MagicMock()
    mock_pipeline = MagicMock()
    stanza_mock.Pipeline.return_value = mock_pipeline
    stanza_mock.download = MagicMock()
    sys.modules['stanza'] = stanza_mock
    
    yield
    
    # Cleanup
    if 'stanza' in sys.modules:
        del sys.modules['stanza']
