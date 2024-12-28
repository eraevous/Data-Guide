import pandas as pd

class DataPull:
    @staticmethod
    def get_data(client, url, params, output_file):
        response = client.session.get(url, headers=client.headers, params=params)
        if response.status_code == 200:
            data = response.json().get("data", [])
            if data:
                df = pd.json_normalize(data)
                df.to_csv(output_file, index=False)
                print(f"GET data saved to {output_file}.")
            else:
                print("No data found.")
        else:
            raise Exception(f"GET request failed: {response.status_code}, {response.text}")

    @staticmethod
    def post_data(client, url, payload, output_file):
        response = client.session.post(url, headers=client.headers, json=payload)
        if response.status_code == 200:
            data = response.json().get("data", [])
            if data:
                df = pd.json_normalize(data)
                df.to_csv(output_file, index=False)
                print(f"POST data saved to {output_file}.")
            else:
                print("No data found.")
        else:
            raise Exception(f"POST request failed: {response.status_code}, {response.text}")
