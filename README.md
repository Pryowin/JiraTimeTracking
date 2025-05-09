# Jira Time Logs Reporter

This Python script fetches time log entries from a Jira instance for a specified month (or current month if not specified) and saves them to either a CSV or Excel file. The script aggregates time entries by assignee and ticket, making it easy to track time spent on different tasks.

## Features

- Fetches time logs from Jira for a specific month or current month
- Aggregates time entries by assignee and ticket
- Saves data to either CSV or Excel file with a clear naming convention
- Handles date validation and error cases
- Includes comprehensive test suite

## Prerequisites

- Python 3.8 or higher
- Jira instance with API access
- Jira API token

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd jira-time-reports
```

2. Create a virtual environment and activate it:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Create a `config.py` file in the project root with your Jira credentials:
```python
JIRA_URL = "https://your-domain.atlassian.net"
JIRA_EMAIL = "your-email@example.com"
JIRA_API_TOKEN = "your-api-token"
OUTPUT_FILENAME_PREFIX = "jira_time_logs"  # Optional, defaults to "jira_time_logs"
```

## Usage

### Basic Usage (Current Month)

To fetch time logs for the current month:

```bash
python jira_time_logs.py
```

This will create a CSV file named `jira_time_logs_YYYY_MM.csv` in the current directory.

### Specifying a Month

To fetch time logs for a specific month:

```bash
python jira_time_logs.py --date YYYY-MM
```

For example:
```bash
python jira_time_logs.py --date 2024-03
```

This will create a CSV file named `jira_time_logs_2024_03.csv`.

### Output Format

By default, the script saves data in CSV format. To save in Excel format, use the `--format` option:

```bash
python jira_time_logs.py --format excel
```

You can combine this with the date option:

```bash
python jira_time_logs.py --date 2024-03 --format excel
```

This will create an Excel file named `jira_time_logs_2024_03.xlsx`.

### Date Format Requirements

- The date must be in `YYYY-MM` format
- Year must be between 2000 and current year + 1
- Month must be between 01 and 12
- Examples of valid dates: `2024-03`, `2023-12`, `2024-01`

## Output

The script generates a CSV file containing the following columns:
- Assignee: Name of the person who logged the time
- Ticket Number: Jira ticket identifier
- Ticket Description: Summary of the ticket
- Hours Logged: Total hours spent on the ticket (aggregated)

## Running Tests

The project includes a comprehensive test suite using pytest. To run the tests:

1. Make sure you have all dependencies installed:
```bash
pip install -r requirements.txt
```

2. Run the tests:
```bash
# Run all tests
python -m pytest tests/

# Run tests with verbose output
python -m pytest tests/ -v

# Run tests with very verbose output
python -m pytest tests/ -vv
```

The test suite includes:
- Date format validation
- Month range calculation
- Time log aggregation
- CSV file generation
- Jira API interaction (mocked)

## Error Handling

The script handles various error cases:
- Invalid date format
- Invalid month/year values
- Missing or invalid Jira credentials
- Network connectivity issues
- Empty time logs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 