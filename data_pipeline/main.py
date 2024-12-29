from api_client import APIClient
from data_pull import *
import sys
import os

def main():
    if len(sys.argv) < 3:
        print("Usage: main.py <username> <password> <output_dir> (optional)")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "output"

    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Initialize API client with hardcoded cookie from separate JSON file
    client = APIClient(username=username, password=password)

    # Perform initial login to retrieve elements of the return cookie
    client.login()

    # Load or authenticate
    client.load_cookies()
    if not client.session.cookies:
        client.login()

    # Fetch reports
    fetch_statement_submission_report(client, output_dir)
    fetch_aged_ar_report(client, output_dir)
    fetch_integrated_payments_report(client, output_dir)
    #fetch_billing_statement_report(client, output_dir)
    #fetch_outstanding_claims_report(client, output_dir)
    #fetch_unresolved_claims_report(client, output_dir)

if __name__ == "__main__":
    main()