from jira import JIRA
import pandas as pd
from datetime import datetime, date
import calendar
import sys

try:
    from config import JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN
except ImportError:
    print("Error: config.py file not found. Please create config.py with JIRA_URL, JIRA_EMAIL, and JIRA_API_TOKEN.")
    sys.exit(1)

def get_current_month_range():
    """Get the start and end dates for the current month."""
    today = date.today()
    first_day = date(today.year, today.month, 1)
    last_day = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
    return first_day, last_day

def fetch_time_logs():
    """Fetch time logs from Jira for the current month."""
    # Connect to Jira
    jira = JIRA(
        server=JIRA_URL,
        basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN)
    )

    # Get current month's date range
    start_date, end_date = get_current_month_range()
    
    # Prepare the JQL query for worklogs in the current month
    jql_query = f'worklogDate >= "{start_date}" AND worklogDate <= "{end_date}"'
    
    # Initialize lists to store data
    time_logs = []
    
    # Search for issues with worklogs
    issues = jira.search_issues(jql_query, maxResults=False)
    
    for issue in issues:
        # Get worklogs for each issue
        worklogs = jira.worklogs(issue.key)
        
        for worklog in worklogs:
            # Convert worklog date to datetime
            worklog_date = datetime.strptime(worklog.started, "%Y-%m-%dT%H:%M:%S.%f%z").date()
            
            # Only include worklogs from current month
            if start_date <= worklog_date <= end_date:
                time_logs.append({
                    'Assignee': worklog.author.displayName,
                    'Ticket Number': issue.key,
                    'Ticket Description': issue.fields.summary,
                    'Hours Logged': worklog.timeSpentSeconds / 3600  # Convert seconds to hours
                })
    
    return time_logs

def save_to_csv(time_logs):
    """Save time logs to a CSV file."""
    if not time_logs:
        print("No time logs found for the current month.")
        return
    
    # Create DataFrame
    df = pd.DataFrame(time_logs)
    
    # Generate filename with current month and year
    current_date = datetime.now()
    filename = f"jira_time_logs_{current_date.strftime('%Y_%m')}.csv"
    
    # Save to CSV
    df.to_csv(filename, index=False)
    print(f"Time logs have been saved to {filename}")

def main():
    try:
        print("Fetching time logs from Jira...")
        time_logs = fetch_time_logs()
        save_to_csv(time_logs)
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 