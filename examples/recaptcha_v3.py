"""
Example: Solve a reCAPTCHA v3 challenge.

Prerequisites:
    Set the CAPTCHA_API_KEY environment variable.
    Replace websiteURL, websiteKey, minScore, and pageAction with values from your target page.
    reCAPTCHA v3 does not require a proxy. It is solved from the service IP addresses.
"""

import os
import sys
import time
import requests

# Load API key from environment variable or set it directly here.
# export CAPTCHA_API_KEY=1abc234de56fab7c89012d34e56fa7b8 on Linux or macOS.
# set CAPTCHA_API_KEY=1abc234de56fab7c89012d34e56fa7b8 on Windows.
api_key = os.getenv("CAPTCHA_API_KEY", "YOUR_API_KEY")

# --- Proxyless example ---
# Solves reCAPTCHA v3 without a proxy.
# A proxy is not required for v3. Tasks are solved from the service IP addresses.
# The higher the minScore, the harder and longer the task takes to solve.
try:
    # Step 1: Create a task to solve the reCAPTCHA v3 captcha.
    # pageAction is the value of the action parameter the site sets when calling grecaptcha.execute().
    # Passing it increases the chance of the site accepting the token.
    # Set isEnterprise to True if the site uses reCAPTCHA v3 Enterprise.
    response = requests.post("https://api.captcha-solver.com/createTask", json={
        "clientKey": api_key,
        "task": {
            "type": "RecaptchaV3TaskProxyless",
            "websiteURL": "https://example.com/login",                   # Full URL of the page with captcha
            "websiteKey": "6Le-xxxxxxxxxxxxxxxxxxxxxxxxxxxx",            # Site key of the reCAPTCHA v3 widget
            "minScore": 0.7,                                             # Minimum acceptable token score (0.1 to 0.9)
            "pageAction": "verify",                                      # Action value from grecaptcha.execute() call
            # Optional fields:
            # "isEnterprise": False,                                     # Set True for reCAPTCHA v3 Enterprise
            # "apiDomain": "www.recaptcha.net"                           # Set if site loads from recaptcha.net
        }
    })
    task_id = response.json().get("taskId")

    # Step 2: Poll for the result until the task is ready.
    # The API processes the captcha asynchronously. Check the status periodically.
    # Higher minScore values will take longer to solve.
    while True:
        result = requests.post("https://api.captcha-solver.com/getTaskResult", json={
            "clientKey": api_key,
            "taskId": task_id
        }).json()
        if result.get("status") == "ready":
            # Solution contains {"gRecaptchaResponse": "03AGdBq..."}
            # Use this token just like a regular reCAPTCHA v3 token.
            print("result: " + str(result.get("solution")))
            break
        time.sleep(10)  # Wait 10 seconds before polling again. v3 tasks take longer.
except Exception as e:
    sys.exit(e)