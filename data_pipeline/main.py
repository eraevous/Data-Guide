from api_client import APIClient
from data_pull import fetch_aged_ar_report, fetch_statement_submission_report
import sys

def main():
    if len(sys.argv) != 3:
        print("Usage: main.py <username> <password>")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]

    # Initialize API client with hardcoded cookie from separate JSON file
    client = APIClient(username=username, password=password)

    # Perform initial login to retrieve elements of the return cookie
    client.login()

    # Load or authenticate
    client.load_cookies()
    if not client.session.cookies:
        client.login()

    # Fetch reports
    fetch_statement_submission_report(client)
    fetch_aged_ar_report(client)

if __name__ == "__main__":
    main()