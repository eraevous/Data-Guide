import pandas as pd

class DataPull:
    @staticmethod
    def get_data(client, urls, params, output_file):
        data_frames = []
        for url in urls:
            response = client.session.get(url, headers=client.headers, params=params)
            if response.status_code == 200:
                data = response.json().get("data", [])
                if data:
                    df = pd.json_normalize(data)
                    data_frames.append(df)
                else:
                    print(f"No data found for URL: {url}")
            else:
                raise Exception(f"GET request failed for URL {url}: {response.status_code}, {response.text}")
        
        if data_frames:
            combined_df = pd.concat(data_frames, ignore_index=True)
            combined_df.to_csv(output_file, index=False)
            print(f"GET data saved to {output_file}.")
        else:
            print("No data to save.")

    @staticmethod
    def post_data(client, urls, payload, output_file):
        data_frames = []
        for url in urls:
            response = client.session.post(url, headers=client.headers, json=payload)
            if response.status_code == 200:
                data = response.json().get("data", [])
                if data:
                    df = pd.json_normalize(data)
                    data_frames.append(df)
                else:
                    print(f"No data found for URL: {url}")
            else:
                raise Exception(f"POST request failed for URL {url}: {response.status_code}, {response.text}")
        
        if data_frames:
            combined_df = pd.concat(data_frames, ignore_index=True)
            combined_df.to_csv(output_file, index=False)
            print(f"POST data saved to {output_file}.")
        else:
            print("No data to save.")