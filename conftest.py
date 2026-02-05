"""Pytest configuration for test suite."""
import pytest
import sys
from unittest.mock import MagicMock, Mock, patch


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Set up test environment with necessary mocks and configurations.
    This fixture runs automatically for all tests.
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
