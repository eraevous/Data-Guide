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
    params1 = {
        "location": "14000000000286",
        "dateTimeFrom": "0",
        "dateTimeTo": "9999999999999",
        "deliveryMethod": "ELECTRONIC",
        "from": "1",
        "rows": "10000",
        "field": "dateTime",
        "order": "desc"
    }

    params2, params3 = params1.copy(), params1.copy()
    params2["deliveryMethod"] = "MAIL_FOR_ME"
    params3["deliveryMethod"] = "PRINT"

    data1 = client.make_request(url, method="GET", params=params1)
    data2 = client.make_request(url, method="GET", params=params2)
    data3 = client.make_request(url, method="GET", params=params3)

    # Convert to dataframes and add source column
    df1 = pd.json_normalize(data1)
    df1["source"] = "ELECTRONIC"
    df2 = pd.json_normalize(data2)
    df2["source"] = "MAIL_FOR_ME"
    df3 = pd.json_normalize(data3)
    df3["source"] = "PRINT"

    # Concatenate dataframes
    combined_df = pd.concat([df1, df2, df3], ignore_index=True)

    # Save to CSV
    combined_df.to_csv("statement_submission.csv", index=False)
    print("Statement Submission Report saved to statement_submission.csv")