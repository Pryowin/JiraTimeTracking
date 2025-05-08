import pytest
from datetime import datetime, date
import pandas as pd
from unittest.mock import Mock, patch
from jira_time_logs import (
    get_month_range,
    aggregate_time_logs,
    save_to_csv,
    validate_date_format
)

# Test data
MOCK_TIME_LOGS = [
    {
        'Assignee': 'John Doe',
        'Ticket Number': 'TR-123',
        'Ticket Description': 'Test Ticket 1',
        'Hours Logged': 2.5
    },
    {
        'Assignee': 'John Doe',
        'Ticket Number': 'TR-123',
        'Ticket Description': 'Test Ticket 1',
        'Hours Logged': 1.5
    },
    {
        'Assignee': 'Jane Smith',
        'Ticket Number': 'TR-456',
        'Ticket Description': 'Test Ticket 2',
        'Hours Logged': 3.0
    }
]

def test_validate_date_format_valid():
    """Test date validation with valid dates."""
    # Test current year and month
    result = validate_date_format("2024-03")
    assert result == (2024, 3)
    
    # Test edge cases for months
    assert validate_date_format("2024-01") == (2024, 1)
    assert validate_date_format("2024-12") == (2024, 12)

def test_validate_date_format_invalid():
    """Test date validation with invalid dates."""
    invalid_dates = [
        "2024-13",    # Invalid month
        "2024-00",    # Invalid month
        "202-01",     # Invalid year format
        "2024-1",     # Invalid month format (needs leading zero)
        "2024/01",    # Invalid separator
        "abcd-01",    # Invalid year
        "2024-ab",    # Invalid month format
        "2024-1a",    # Invalid month format
        "",          # Empty string
        "2024",      # Missing month
        "2024-",     # Incomplete format
        "-01",       # Missing year
        123,         # Non-string input
        True,        # Non-string input
        None         # None value
    ]
    
    for invalid_date in invalid_dates:
        if invalid_date is None:
            assert validate_date_format(invalid_date) is None
        else:
            with pytest.raises(ValueError):
                validate_date_format(invalid_date)

def test_validate_date_format_year_range():
    """Test year range validation."""
    current_year = datetime.now().year
    
    # Test year too far in the past
    with pytest.raises(ValueError):
        validate_date_format("1999-12")
    
    # Test year too far in the future
    with pytest.raises(ValueError):
        validate_date_format(f"{current_year + 2}-01")

def test_get_month_range_current():
    """Test getting date range for current month."""
    start_date, end_date = get_month_range()
    
    today = date.today()
    assert start_date.day == 1
    assert start_date.month == today.month
    assert start_date.year == today.year
    
    last_day = pd.Timestamp(end_date).days_in_month
    assert end_date.day == last_day
    assert end_date.month == today.month
    assert end_date.year == today.year

def test_get_month_range_specific():
    """Test getting date range for specific month."""
    start_date, end_date = get_month_range(2024, 2)  # February 2024
    
    assert start_date == date(2024, 2, 1)
    assert end_date == date(2024, 2, 29)  # 2024 is a leap year

def test_aggregate_time_logs_empty():
    """Test aggregation with empty time logs."""
    result = aggregate_time_logs([])
    assert result == []

def test_aggregate_time_logs():
    """Test that time logs are correctly aggregated by assignee and ticket."""
    result = aggregate_time_logs(MOCK_TIME_LOGS)
    
    # Should have 2 entries after aggregation (2 unique assignee-ticket combinations)
    assert len(result) == 2
    
    # Find John Doe's entry
    john_entry = next(entry for entry in result if entry['Assignee'] == 'John Doe')
    assert john_entry['Ticket Number'] == 'TR-123'
    assert john_entry['Hours Logged'] == 4.0  # 2.5 + 1.5
    
    # Find Jane Smith's entry
    jane_entry = next(entry for entry in result if entry['Assignee'] == 'Jane Smith')
    assert jane_entry['Ticket Number'] == 'TR-456'
    assert jane_entry['Hours Logged'] == 3.0

def test_aggregate_time_logs_sorting():
    """Test that aggregated results are sorted by assignee and ticket number."""
    result = aggregate_time_logs(MOCK_TIME_LOGS)
    
    # Check that results are sorted by assignee name
    assignees = [entry['Assignee'] for entry in result]
    assert assignees == sorted(assignees)

@patch('pandas.DataFrame.to_csv')
def test_save_to_csv_current_month(mock_to_csv):
    """Test saving to CSV for current month."""
    save_to_csv(MOCK_TIME_LOGS)
    mock_to_csv.assert_called_once()
    
    current_date = datetime.now()
    expected_filename = f"jira_time_logs_{current_date.strftime('%Y_%m')}.csv"
    assert expected_filename in str(mock_to_csv.call_args)

@patch('pandas.DataFrame.to_csv')
def test_save_to_csv_specific_month(mock_to_csv):
    """Test saving to CSV for specific month."""
    save_to_csv(MOCK_TIME_LOGS, "2024-03")
    mock_to_csv.assert_called_once()
    assert "jira_time_logs_2024_03.csv" in str(mock_to_csv.call_args)

@patch('pandas.DataFrame.to_csv')
def test_save_to_csv_empty(mock_to_csv):
    """Test that save_to_csv handles empty data correctly."""
    save_to_csv([])
    mock_to_csv.assert_not_called()

@pytest.fixture
def mock_jira():
    """Fixture to create a mock Jira instance."""
    mock_issue = Mock()
    mock_issue.key = 'TR-123'
    mock_issue.fields.summary = 'Test Ticket'
    
    mock_worklog = Mock()
    mock_worklog.author.displayName = 'Test User'
    mock_worklog.started = '2024-03-15T10:00:00.000+0000'
    mock_worklog.timeSpentSeconds = 3600  # 1 hour
    
    mock_issue.worklogs.return_value = [mock_worklog]
    
    mock_jira = Mock()
    mock_jira.search_issues.return_value = [mock_issue]
    mock_jira.worklogs.return_value = [mock_worklog]
    
    return mock_jira

@patch('jira_time_logs.JIRA')
def test_fetch_time_logs(mock_jira_class, mock_jira):
    """Test that fetch_time_logs correctly processes Jira data."""
    mock_jira_class.return_value = mock_jira
    
    from jira_time_logs import fetch_time_logs
    
    # Test with specific date
    result = fetch_time_logs("2024-03")
    
    # Verify the result structure
    assert len(result) == 1
    entry = result[0]
    assert entry['Assignee'] == 'Test User'
    assert entry['Ticket Number'] == 'TR-123'
    assert entry['Ticket Description'] == 'Test Ticket'
    assert entry['Hours Logged'] == 1.0  # 3600 seconds = 1 hour 