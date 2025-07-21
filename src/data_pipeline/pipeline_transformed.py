import pandas as pd
import os
from data_profiler import DataProfiler
from data_transform import DataTransform
import sys

def load_csv_files(file_paths):
    """Load multiple CSV files into a dictionary keyed by filename."""
    dataframes = {}
    for file_path in file_paths:
        df_name = os.path.basename(file_path).replace(".csv", "")
        dataframes[df_name] = pd.read_csv(file_path)
    return dataframes

def save_report(report, output_dir, file_name):
    with open(os.path.join(output_dir, file_name), "w") as f:
        f.write(report)

if __name__ == "__main__":
    # Define CSV files, custom types, and output directory

    if len(sys.argv) < 2:
        print("Usage: main.py <input_dif> (optional) <output_dir> (optional)")
        sys.exit(1)

    input_dir = sys.argv[1] if len(sys.argv) > 1 else "input"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
    format = sys.argv[3] if len(sys.argv) > 3 else "md"

    csv_files = {
        "aged_AR" : os.path.join(input_dir, "transformed_aged_AR.csv"),
        "aged_AR_long" : os.path.join(input_dir, "transformed_aged_AR_long.csv"),
        "statement_submission" : os.path.join(input_dir, "transformed_statement_submission.csv"),
        "integrated_payments" : os.path.join(input_dir, "transformed_integrated_payments.csv"),
        #"billing_statement" : os.path.join(input_dir, "billing_statement_report.csv"),
        "outstanding_claims" : os.path.join(input_dir, "transformed_outstanding_claims.csv"),
        # "unresolved_claims" : os.path.join(input_dir, "unresolved_claims_report.csv"),
        #"fee_schedule" : os.path.join(input_dir, "fee_schedule.csv"),
        #"openings" : os.path.join(input_dir,"openings.csv"),
        #"schedule" : os.path.join(input_dir,"schedule.csv"),
        "patient_details" : os.path.join(input_dir, "transformed_patient_details.csv"),
        "active_patients" : os.path.join(input_dir, "transformed_active_patient_details.csv"),
        "processed_payments": os.path.join(input_dir, "transformed_processed_payments.csv"),
        "payments": os.path.join(input_dir, "transformed_payments.csv"),
        "incurred_charges": os.path.join(input_dir, "transformed_incurred_charges.csv"),
        "transaction_details" : os.path.join(input_dir, "transformed_transaction_details.csv"),
        # "treatment_tracker" : os.path.join(input_dir, "ZR - Treatment Tracker.csv"),
        # "merged_data" : os.path.join(input_dir, "merged_data.csv"),
        'carrier_decision_data' : os.path.join(input_dir, 'Carrier_Decision_Data.csv'),
        'insurance_payment_metrics' : os.path.join(input_dir, 'insurance_payment_metrics.csv'),
        "financial_timeline" : os.path.join(input_dir, "financial_timeline.csv"),
        'time_to_payments' : os.path.join(input_dir, "time_to_payments.csv"),
    }
    
    custom_types = {
        "aged_AR": {"id": "id", 'Ascend Patient ID':'id', "phoneNumber": "phone_number", "billingStatement": "id", 
            "lastPayment.datedAs": "unix_timestamp", "guarantor" : "name", 'claimsPending': 'category','remaining_guarantorPortion':'bool', 'remaining_insurancePortion':'bool'},

        "aged_AR_long": {"id": "id", 'Ascend Patient ID':'id', "Bucket" : "category", 'Responsible Party' : 'name','Bucket' : 'category',},

        "statement_submission": {"id": "id", "dateTime": "date", "patient.id": "id",
                                 'patient.firstName' : 'name', 'patient.lastName' : 'name',
                                 'neg_balances': 'category', 'possibleDuplicate': 'category'},

        "patient_details": {"Ascend Patient ID": "id", "Phone": "phone_number", "Date Of Birth": "date", 
            "Prim. Subscriber ID": "id", "Address": "address", "Email": "email", "First Visit": "date", 
            "Last Visit": "date", 'Patient' : 'name', 'Primary Guarantor' : 'name', 'Primary Contact' : 'name',
            'Last Name' : 'name', 'Chart Number' : 'id',
            "Last Procedure Date": "date", "Next Appointment Date": "date",
            'student': 'category','Visit and Procedure Mismatch':'bool', 'hasNextAppointment':'bool','overdue':'bool',
            'Affiliate State':'category','Cleaned Carrier':'category', 
            'Street':'address', 'City':'category', 'State':'category', 'ZIP Code':'category', 'merge_key': 'id', 'Ascend Patient ID': 'id', 'Empty': 'none',
            'DCS': 'bool', 'DNU': 'bool'},

        "active_patients": {"Ascend Patient ID": "id", "Phone": "phone_number", "Date Of Birth": "date", 
            "Prim. Subscriber ID": "id", "Address": "address", "Email": "email", "First Visit": "date", 
            "Last Visit": "date", 'Patient' : 'name', 'Primary Guarantor' : 'name', 'Primary Contact' : 'name',
            'Last Name' : 'name', 'Chart Number' : 'id',
            "Last Procedure Date": "date", "Next Appointment Date": "date",
            'student': 'category','Visit and Procedure Mismatch':'bool', 'hasNextAppointment':'bool','overdue':'bool',
            'Affiliate State':'category','Cleaned Carrier':'category', 
            'Street':'address', 'City':'category', 'State':'category', 'ZIP Code':'category', 'merge_key': 'id', 'Ascend Patient ID': 'id', 'Empty': 'none', 'DCS': 'bool', 'DNU': 'bool'},

        "processed_payments" : {"Date (Modified)" : "date", "Amount" : "currency", "Ascend Patient ID" : 'id',
                                'Patient' : 'name', 'Transaction ID' : 'id',
                                'sort_key':'id'},

        "payments" : {"Date (Modified)" : "date", "Amount" : "currency", "Ascend Patient ID" : 'id',
                                'Patient' : 'name', 'Transaction ID' : 'id',
                                'Extracted Insurance' : 'category', 'Extracted Card Type' : 'category','sort_key':'id'},

        "incurred_charges" : {"Date (Modified)" : "date", "Amount" : "currency", "Ascend Patient ID" : 'id',
                                'Patient' : 'name', 'Transaction ID' : 'id',
                                'sort_key':'id'},

        "transaction_details" : {"Date" : "date", "Ascend Patient ID" : "id", "Charges" : "currency", 
            "Credits" : "currency", 'Patient' : 'name', 'Chart Number' : 'id'},
            
        "treatment_tracker" : {"Ascend Patient ID" : "id", "Date" : "date", "Amount Presented" : "currency", 'Patient' : 'name',
                               },

        "outstanding_claims" :{'id':'id', "createdDate" : "unix_timestamp", 'subscriberNumber' : 'id', "serviceDate" : "unix_timestamp",
            'insuranceCarrier.phoneNumber' : 'phone_number', 'insuranceCarrier.phoneExtension' : 'skip', "insuranceCarrier.website" : "url",
            'subscriber.id':'id', 'patient.id':'id', 'groupPlan.phoneNumber':'phone_number', 'groupPlan.phoneExtension':'skip', 
            'subscriber.dateOfBirth' : 'unix_timestamp', 'patient.dateOfBirth' : 'unix_timestamp',
            'subscriber.firstName' : 'name', 'subscriber.lastName' : 'name', 'patient.firstName' : 'name', 'patient.lastName' : 'name'},
        
        "unresolved_claims" :{'claimId': 'id', 'carrierId': 'id', 'patientId': 'id',},

        "integrated_payments" :{'id': 'id', 'transactionDateTime': 'date','transactionId': 'id', 
                                "transactionReferenceNumber" : 'id', 'transactionCardLogo' : 'category',
                                'event':'category','Card Type':'category','transactionCardholderName':'name',},

        "unresolved_claims" :{'claimStateId': 'category', 'carrierId': 'id', 'patientId': 'id', 'claimId': 'id',
                              'carrierInsurancePlan.id': 'category', 'carrierInsurancePlan.insuranceCarrier.id': 'id',
                              'patientName': 'name'},
        
        "merged_data" : {"Ascend Patient ID": "id", "Phone": "phone_number", "Date Of Birth": "date", 
            "Prim. Subscriber ID": "id", "Address": "address", "Email": "email", "First Visit": "date", 
            "Last Visit": "date", 'Patient' : 'name', 'Primary Guarantor' : 'name', 'Primary Contact' : 'name',
            'Last Name' : 'name', 'Chart Number' : 'id',
            "Last Procedure Date": "date", "Next Appointment Date": "date",
            'student': 'category','Visit and Procedure Mismatch':'bool', 'hasNextAppointment':'bool','overdue':'bool',
            'Affiliate State':'category','Cleaned Carrier':'category', 
            'Street':'address', 'City':'category', 'State':'category', 'ZIP Code':'category', 'neg_balances': 'category', 'possibleDuplicate': 'category', 
            'merge_key_x': 'id', 'merge_key_y': 'id', 'Empty': 'none',},
        
        'carrier_decision_data' : {'carrierId': 'id', 'carrierName': 'name', 'carrierState': 'category', 'carrierType': 'category'},
        'insurance_payment_metrics' : {'carrierId': 'id', 'carrierName': 'name', 'carrierState': 'category', 'carrierType': 'category'},
        'financial_timeline' : {'id': 'id', 'date': 'date', 'event': 'category', 'amount': 'currency', 'balance': 'currency'},
        'time_to_payments' : {'id': 'id', 'date': 'date', 'event': 'category', 'amount': 'currency', 'balance': 'currency'},
    }

    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Load datasets
    dataframes = {dataset: pd.read_csv(file_path) for dataset, file_path in csv_files.items()}

    for df_name, df in dataframes.items():
        print(f"Processing {df_name}...")

        print(df.head())

        # Step 1: Profile raw data
        print("Profiling raw data...")
        profiler = DataProfiler(df, custom_types=custom_types.get(df_name, {}), output_dir=f"{output_dir}/{df_name}/")
        profiler.profile_dataset()
        raw_report = profiler.generate_report(format, f"{df_name} raw data.{format}")
        #save_report(raw_report, output_dir, f"{df_name}_raw_data_profile.md")

        # # Step 2: Transform data
        # print("Transforming data...")
        # df_cleaned = DataTransform.handle_nulls(df, strategy="fill", fill_value="Unknown")
        # date_columns = [col for col, dtype in custom_types.get(df_name, {}).items() if dtype == "date"]
        # df_cleaned = DataTransform.convert_dates(df_cleaned, date_columns)

        # # Step 3: Profile transformed data
        # print("Profiling transformed data...")
        # transformed_profiler = DataProfiler(df_cleaned)
        # transformed_profiler.profile_dataset()
        # transformed_report = transformed_profiler.generate_report("markdown", f"{df_name} transformed data")
        # save_report(transformed_report, output_dir, f"{df_name}_transformed_data_profile.md")

    print("Pipeline execution complete.")