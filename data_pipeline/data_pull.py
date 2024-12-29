import pandas as pd

def fetch_aged_ar_report(client):
    """
    Fetch the Aged AR Report using a POST request.
    """
    url = "https://live6.dentrixascend.com/agedReceivables/create"
    payload = {
        "0": {"id": 14000000000191},
        "1": {"id": 14000000000756},
        "2": {"id": 14000000001321},
        "3": {"id": 14000000001886},
        "asOfDate": 1734480000000,
        "billingTypes": [],
        "isEmpty": False,
        "isPendingClaimCheckboxDisabled": False,
        "isPendingClaimHidden": False,
        "locations": [14000000000286],
        "period": "ALL",
        "periodName": "All",
        "skipPendingClaim": False,
        "start": 1644772954021,
        "withOrganization": False
    }
    
    data = client.make_request(url, method="POST", payload=payload)
    # Save to CSV
    pd.json_normalize(data).to_csv("aged_ar_report.csv", index=False)
    print("Aged AR Report saved to aged_ar_report.csv")

def fetch_statement_submission_report(client):
    """
    Fetch the Statement Submission Report using a GET request.
    """
    url = "https://live6.dentrixascend.com/statementSubmissionReport"
    params = {
        "location": "14000000000286",
        "dateTimeFrom": "0",
        "dateTimeTo": "9999999999999",
        "deliveryMethod": "ELECTRONIC",
        "from": "1",
        "rows": "10000",
        "field": "dateTime",
        "order": "desc"
    }
    data = client.make_request(url, method="GET", params=params)
    # Save to CSV
    pd.json_normalize(data).to_csv("statement_submission.csv", index=False)
    print("Statement Submission Report saved to statement_submission.csv")