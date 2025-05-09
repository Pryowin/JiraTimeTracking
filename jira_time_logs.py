from jira import JIRA
import pandas as pd
from datetime import datetime, date
import calendar
import sys
import re
import argparse

try:
    from config import JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN, OUTPUT_FILENAME_PREFIX
except ImportError:
    print("Error: config.py file not found. Please create config.py with JIRA_URL, JIRA_EMAIL, and JIRA_API_TOKEN.")
    sys.exit(1)

def validate_date_format(date_str):
    """Validate the date string format (YYYY-MM) and return a tuple of (year, month)."""
    if date_str is None:
        return None
        
    if not isinstance(date_str, str):
        raise ValueError("Date must be a string in format YYYY-MM (e.g., 2024-03)")
    
    if not date_str:
        raise ValueError("Date string cannot be empty")
        
    # Basic format check
    if not re.match(r'^\d{4}-\d{2}$', date_str):
        raise ValueError("Date must be in format YYYY-MM (e.g., 2024-03)")
    
    try:
        year, month = map(int, date_str.split('-'))
    except (ValueError, TypeError):
        raise ValueError("Date must be in format YYYY-MM (e.g., 2024-03)")
    
    # Check if year is reasonable (between 2000 and current year + 1)
    current_year = datetime.now().year
    if year < 2000 or year > current_year + 1:
        raise ValueError(f"Year must be between 2000 and {current_year + 1}")
    
    # Validate month range (1-12)
    if month < 1 or month > 12:
        raise ValueError("Month must be between 01 and 12")
    
    return year, month

def get_month_range(year=None, month=None):
    """Get the start and end dates for the specified month or current month."""
    if year is None or month is None:
        today = date.today()
        year = today.year
        month = today.month
    
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])
    return first_day, last_day

def fetch_time_logs(target_date=None):
    """Fetch time logs from Jira for the specified month or current month."""
    # Connect to Jira
    jira = JIRA(
        server=JIRA_URL,
        basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN)
    )

    # Get date range
    if target_date:
        year, month = validate_date_format(target_date)
        start_date, end_date = get_month_range(year, month)
    else:
        start_date, end_date = get_month_range()
    
    # Prepare the JQL query for worklogs in the target month
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
            
            # Only include worklogs from target month
            if start_date <= worklog_date <= end_date:
                time_logs.append({
                    'Assignee': worklog.author.displayName,
                    'Ticket Number': issue.key,
                    'Ticket Description': issue.fields.summary,
                    'Hours Logged': worklog.timeSpentSeconds / 3600  # Convert seconds to hours
                })
    
    return time_logs

def aggregate_time_logs(time_logs):
    """Aggregate time logs by assignee and ticket."""
    if not time_logs:
        return []
    
    # Create DataFrame
    df = pd.DataFrame(time_logs)
    
    # Group by assignee, ticket number, and ticket description, then sum the hours
    aggregated_df = df.groupby(['Assignee', 'Ticket Number', 'Ticket Description'])['Hours Logged'].sum().reset_index()
    
    # Sort by assignee and ticket number
    aggregated_df = aggregated_df.sort_values(['Assignee', 'Ticket Number'])
    
    # Round hours to 2 decimal places
    aggregated_df['Hours Logged'] = aggregated_df['Hours Logged'].round(2)
    
    return aggregated_df.to_dict('records')

def save_time_logs(time_logs, target_date=None, output_format='csv'):
    """Save time logs to a file in the specified format (csv or excel)."""
    if not time_logs:
        print("No time logs found for the specified month.")
        return
    
    # Create DataFrame
    df = pd.DataFrame(time_logs)
    
    # Generate filename with target month and year or current date
    if target_date:
        year, month = validate_date_format(target_date)
        base_filename = f"{OUTPUT_FILENAME_PREFIX}_{year}_{month:02d}"
    else:
        current_date = datetime.now()
        base_filename = f"{OUTPUT_FILENAME_PREFIX}_{current_date.strftime('%Y_%m')}"
    
    # Save to file based on format
    if output_format.lower() == 'excel':
        filename = f"{base_filename}.xlsx"
        
        # Create Excel writer
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Save main data to first sheet
            df.to_excel(writer, sheet_name='Time Logs', index=False)
            
            # Create pivot table for hours by person
            pivot_by_person = df.pivot_table(
                values='Hours Logged',
                index='Assignee',
                aggfunc='sum'
            ).round(2)
            pivot_by_person = pivot_by_person.sort_index()  # Sort by name
            pivot_by_person.to_excel(writer, sheet_name='Hours by Person')
            
            # Create pivot table for hours by ticket
            pivot_by_ticket = df.pivot_table(
                values='Hours Logged',
                index=['Ticket Number', 'Ticket Description'],
                aggfunc='sum'
            ).round(2)
            pivot_by_ticket = pivot_by_ticket.sort_values('Ticket Description')  # Sort by description
            pivot_by_ticket.to_excel(writer, sheet_name='Hours by Ticket')
            
            # Adjust column widths for all sheets
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                
                # Get the maximum length of content in each column
                for idx, col in enumerate(worksheet.columns):
                    # Get the maximum length of content in the column
                    max_length = 0
                    column = [cell for cell in col]
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    # Add some padding to the max length
                    adjusted_width = (max_length + 2)
                    
                    # Set the column width
                    worksheet.column_dimensions[chr(65 + idx)].width = adjusted_width
            
    else:  # default to csv
        filename = f"{base_filename}.csv"
        df.to_csv(filename, index=False)
    
    print(f"Time logs have been saved to {filename}")

def main():
    try:
        # Set up argument parser
        parser = argparse.ArgumentParser(description='Fetch Jira time logs for a specific month')
        parser.add_argument('--date', type=str, help='Target month in YYYY-MM format (e.g., 2024-03)')
        parser.add_argument('--format', type=str, choices=['csv', 'excel'], default='csv',
                          help='Output format (csv or excel)')
        args = parser.parse_args()

        # Validate date if provided
        if args.date:
            validate_date_format(args.date)
        
        print(f"Fetching time logs from Jira for {'specified month' if args.date else 'current month'}...")
        time_logs = fetch_time_logs(args.date)
        print("Aggregating time logs...")
        aggregated_logs = aggregate_time_logs(time_logs)
        save_time_logs(aggregated_logs, args.date, args.format)
    except ValueError as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 