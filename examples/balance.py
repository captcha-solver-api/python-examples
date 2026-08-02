"""
Example: Get account balance.

Prerequisites:
    Set the CAPTCHA_API_KEY environment variable.
    Returns the current available balance of your account.
"""

import os
import sys
import requests

api_key = os.getenv("CAPTCHA_API_KEY", "YOUR_API_KEY")

try:
    response = requests.post("https://api.captcha-solver.com/getBalance", json={
        "clientKey": api_key
    }, timeout=30)
    data = response.json()
    if data.get("errorId") != 0:
        sys.exit(data.get("errorDescription", "Unknown error"))
    print("Balance: " + str(data.get("balance")))
except Exception as e:
    sys.exit(e)