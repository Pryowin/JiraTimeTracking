import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_config():
    """Fixture to provide mock configuration."""
    return {
        'JIRA_URL': 'https://test.atlassian.net',
        'JIRA_EMAIL': 'test@example.com',
        'JIRA_API_TOKEN': 'test-token',
        'OUTPUT_FILENAME_PREFIX': 'test_time_logs'
    } 