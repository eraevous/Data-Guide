import requests
import pickle
import os
import json
import sys

class APIClient:
    COOKIE_FILE = "session_cookies.pkl"
    LOGIN_URL = "https://live6.dentrixascend.com/login/authenticate"
    ORGANIZATION = "JuniperD"

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Referer": "https://live6.dentrixascend.com/",
            "Origin": "https://live6.dentrixascend.com"
        }

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
        """Perform login to retrieve elements of the return cookie."""
        payload = f"organization=JuniperD&username={self.username}&username_escaped=&password={self.password}&send=Log+In"

        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": self.headers["user-agent"]
        }

        response = self.session.post(self.LOGIN_URL, data=payload, headers=headers)
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

            print(response.url)

            print(f"{method} {url} - Status Code: {response.status_code}")

            # Debugging: Print response headers and content
            #print(f"Response Headers: {response.headers}")
            #print(f"Response Content: {response.text}")

            # Output headers and cookies to a text file for debugging
            with open("debug_output.txt", "w") as file:
                file.write("Headers:\n")
                for key, value in response.headers.items():
                    file.write(f"{key}: {value}\n")
                file.write("\nCookies:\n")
                for key, value in self.session.cookies.items():
                    file.write(f"{key}: {value}\n")

            # Check if response is valid JSON
            try:
                return response.json()
            except requests.exceptions.JSONDecodeError:
                # Handle redirection to login
                if "Login" in response.text or response.status_code == 401:
                    print("Session expired or invalid.")
                    #self.login()
                    #return self.make_request(url, method, params, payload)
                else:
                    raise Exception("Invalid JSON response or unexpected content.")

        except Exception as e:
            print(f"Request failed: {e}")
            raise