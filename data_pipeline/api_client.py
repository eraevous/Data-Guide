import requests
import pickle
import os
import json

class APIClient:
    COOKIE_FILE = "session_cookies.pkl"

    def __init__(self, login_url, cookie_file="cookie.json", config_file="config.json"):
        self.login_url = login_url
        self.cookie_file = cookie_file
        self.config_file = config.file
        self.session = requests.Session()
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Referer": "https://live6.dentrixascend.com/",
            "Origin": "https://live6.dentrixascend.com"
        }
        self.hardcoded_cookie = self.load_cookie_from_json()
        self.set_cookies_from_dict(self.hardcoded_cookie)

    def load_cookie_from_json(self):
        """Load the hardcoded cookie from a JSON dictionary."""
        if os.path.exists(self.cookie_file):
            with open(self.cookie_file, "r") as file:
                data = json.load(file)
                print("Loaded hardcoded cookie from JSON dict.")
                return data
        else:
            print(f"Cookie file {self.cookie_file} not found.")
            return None

    def set_cookies_from_dict(self, cookies):
        """Set cookies from a dictionary."""
        if cookies:
            for key, value in cookies.items():
                self.session.cookies.set(key, value)

    def save_cookies(self):
        """Save session cookies to a local file."""
        with open(self.COOKIE_FILE, 'wb') as file:
            pickle.dump(self.session.cookies, file)

    def load_cookies(self):
        """Load session cookies from a local file and update the session."""
        if os.path.exists(self.COOKIE_FILE):
            with open(self.COOKIE_FILE, 'rb') as file:
                self.session.cookies.update(pickle.load(file))
                print("Loaded session cookies.")

    def login(self):
        """Perform login using credentials from config.json."""
        if not os.path.exists(self.config_file):
            raise Exception(f"Config file {self.config_file} not found.")
        with open(self.config_file, "r") as file:
            credentials = json.load(file)

        payload = {
            "organization": credentials["organization"],
            "username": credentials["username"],
            "password": credentials["password"]
        }
        response = self.session.post(self.login_url, data=payload, headers=self.headers)
        if response.status_code == 200:
            print("Login successful.")
            self.save_cookies()
        else:
            raise Exception(f"Login failed: {response.text}")

    def make_request(self, url, method="GET", params=None, payload=None):
        """
        Perform a GET or POST request with the current session, reauthenticating if needed.
        """
        try:
            if method == "GET":
                response = self.session.get(url, headers=self.headers, params=params)
            elif method == "POST":
                response = self.session.post(url, headers=self.headers, json=payload)
            else:
                raise ValueError("Unsupported HTTP method.")

            print(f"{method} {url} - Status Code: {response.status_code}")
            print(f"Response Headers: {response.headers}")
            print(f"Response Content: {response.text}")

            # Output headers and cookies to a text file for debugging
            with open("debug_output.txt", "w") as file:
                file.write("Headers:\n")
                for key, value in response.headers.items():
                    file.write(f"{key}: {value}\n")
                file.write("\nCookies:\n")
                for key, value in self.session.cookies.items():
                    file.write(f"{key}: {value}\n")
                if self.hardcoded_cookie:
                    file.write("\nHardcoded Cookie:\n")
                    for key, value in self.hardcoded_cookie.items():
                        file.write(f"{key}: {value}\n")

            # Check if response is valid JSON
            try:
                return response.json()
            except requests.exceptions.JSONDecodeError:
                # Handle redirection to login
                if "Login" in response.text or response.status_code == 401:
                    print("Session expired or invalid. Reauthenticating...")
                    self.login()
                    return self.make_request(url, method, params, payload)
                else:
                    raise Exception("Invalid JSON response or unexpected content.")

        except Exception as e:
            print(f"Request failed: {e}")
            raise