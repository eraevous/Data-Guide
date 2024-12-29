import requests
import pickle
import os
import json

class APIClient:
    COOKIE_FILE = "session_cookies.pkl"

    def __init__(self, login_url):
        self.login_url = login_url
        self.session = requests.Session()
        self.headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}

    def save_cookies(self):
        with open(self.COOKIE_FILE, 'wb') as file:
            pickle.dump(self.session.cookies, file)

    def load_cookies(self):
        if os.path.exists(self.COOKIE_FILE):
            with open(self.COOKIE_FILE, 'rb') as file:
                self.session.cookies.update(pickle.load(file))
                print("Loaded session cookies.")

    def login(self, username, password, organization):
        payload = {
            "organization": organization,
            "username": username,
            "password": password
        }
        response = self.session.post(self.login_url, data=payload, headers=self.headers)
        if response.status_code == 200:
            print("Login successful.")
            self.save_cookies()
        else:
            raise Exception(f"Login failed: {response.text}")

    def make_request(self, url, method="GET", params=None, payload=None):
        if method == "GET":
            response = self.session.get(url, headers=self.headers, params=params)
        elif method == "POST":
            response = self.session.post(url, headers=self.headers, json=payload)
        else:
            raise ValueError("Unsupported HTTP method")

        print(f"{method} {url} - Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print(f"Response Content: {response.text}")

        if response.status_code != 200:
            raise Exception(f"Request failed: {response.status_code}, {response.text}")

        try:
            return response.json()
        except ValueError:
            raise Exception("Invalid JSON response")