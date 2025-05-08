# Jira Time Logs Exporter

This Python application retrieves time log entries from Jira for the current month and exports them to a CSV file.

## Features

- Fetches all time log entries for the current month
- Exports data to a CSV file with the following information:
  - Assignee name
  - Ticket number
  - Ticket description
  - Hours logged

## Setup

1. Create a virtual environment (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up configuration:
   - Copy the example configuration file:
     ```bash
     cp config.example.py config.py
     ```
   - Edit `config.py` and replace the placeholder values with your actual Jira credentials:
     - `JIRA_URL`: Your Jira instance URL
     - `JIRA_EMAIL`: Your Jira account email
     - `JIRA_API_TOKEN`: Your Jira API token (generate from https://id.atlassian.com/manage-profile/security/api-tokens)
   
   Note: The `config.py` file is gitignored for security reasons. Only `config.example.py` is included in the repository.

## Usage

Simply run the script:
```bash
python jira_time_logs.py
```

The script will:
1. Connect to your Jira instance
2. Fetch all time logs for the current month
3. Save the data to a CSV file named `jira_time_logs_YYYY_MM.csv` in the current directory

## Output

The generated CSV file will contain the following columns:
- Assignee: The name of the person who logged the time
- Ticket Number: The Jira ticket number
- Ticket Description: The summary/description of the ticket
- Hours Logged: The number of hours logged (converted from seconds) 