"""
Example: Solve a GeeTest v3 challenge.

Prerequisites:
    Set the CAPTCHA_API_KEY environment variable.
    Replace websiteURL, gt, and challenge with values from your target page.
    Important: the challenge value is dynamic. Fetch a fresh one for each request.
"""

import os
import sys
import time
import requests

# Load API key from environment variable or set it directly here.
# export CAPTCHA_API_KEY=1abc234de56fab7c89012d34e56fa7b8 on Linux or macOS.
# set CAPTCHA_API_KEY=1abc234de56fab7c89012d34e56fa7b8 on Windows.
api_key = os.getenv("CAPTCHA_API_KEY", "YOUR_API_KEY")

REQUEST_TIMEOUT = 30    # Seconds to wait for a single HTTP request.
POLL_TIMEOUT = 180      # Seconds to wait for the task to be solved before giving up. GeeTest tasks may take longer.

"""
Important: the value of the 'challenge' parameter is dynamic.
For each request to the API you need to get a new value from the target page.
Below is an example of fetching it from a demo endpoint.
In production, extract this from the page's initGeetest call or network requests.
"""
try:
    resp = requests.get("https://target-site.com/path/to/geetest/init", timeout=REQUEST_TIMEOUT)
    challenge = resp.json()["challenge"]
except Exception as e:
    sys.exit(e)

# --- Proxyless example ---
# Solves GeeTest v3 without a proxy.
# v3 is the default version, so the version field can be omitted.
try:
    # Create a task to solve the GeeTest v3 captcha.
    response = requests.post("https://api.captcha-solver.com/createTask", json={
        "clientKey": api_key,
        "task": {
            "type": "GeeTestTaskProxyless",
            "websiteURL": "https://example.com/login",          # Full URL of the page with GeeTest
            "gt": "f2ae6cadcf7886856696c46d84d109d1",           # Public key of the GeeTest widget
            "challenge": challenge,                              # Session-specific value, must be fresh
            # Optional fields:
            # "geetestApiServerSubdomain": "api-na.geetest.com", # Custom API subdomain
            # "initParameters": {},                               # Extra params from initGeetest call
            # "userAgent": "Mozilla/5.0 ...",                     # Browser User-Agent
            # "risk_type": "slide"                                # Dynamic value from the captcha loading request, single-use
        }
    }, timeout=REQUEST_TIMEOUT).json()
    if response.get("errorId"):
        sys.exit(response.get("errorDescription", "Unknown error"))
    task_id = response.get("taskId")

    # Poll for the result until the task is ready or the timeout is reached.
    # GeeTest tasks may take longer. Increase timeout if needed.
    deadline = time.time() + POLL_TIMEOUT
    while time.time() < deadline:
        result = requests.post("https://api.captcha-solver.com/getTaskResult", json={
            "clientKey": api_key,
            "taskId": task_id
        }, timeout=REQUEST_TIMEOUT).json()
        if result.get("errorId"):
            sys.exit(result.get("errorDescription", "Unknown error"))
        if result.get("status") == "ready":
            # Solution contains {"challenge": "...", "validate": "...", "seccode": "..."}
            # Pass solution.validate and solution.seccode to the page's GeeTest callback.
            print("result: " + str(result.get("solution")))
            break
        time.sleep(10)  # Wait 10 seconds before polling again.
    else:
        sys.exit("Timed out waiting for the captcha result.")
except Exception as e:
    sys.exit(e)

# --- With proxy example ---
# Solves GeeTest v3 through your own proxy.
try:
    # Create a task with proxy parameters.
    response = requests.post("https://api.captcha-solver.com/createTask", json={
        "clientKey": api_key,
        "task": {
            "type": "GeeTestTask",
            "websiteURL": "https://example.com/login",          # Full URL of the page with GeeTest
            "gt": "f2ae6cadcf7886856696c46d84d109d1",           # Public key of the GeeTest widget
            "challenge": challenge,                              # Session-specific value, must be fresh
            # Proxy parameters:
            "proxyType": "http",        # http, socks4, or socks5
            "proxyAddress": "1.2.3.4",  # Proxy IP address
            "proxyPort": 8080,          # Proxy port
            "proxyLogin": "user",       # Login for proxy authorization (optional)
            "proxyPassword": "password" # Password for proxy authorization (optional)
        }
    }, timeout=REQUEST_TIMEOUT).json()
    if response.get("errorId"):
        sys.exit(response.get("errorDescription", "Unknown error"))
    task_id = response.get("taskId")

    # Poll for the result until the task is ready or the timeout is reached.
    deadline = time.time() + POLL_TIMEOUT
    while time.time() < deadline:
        result = requests.post("https://api.captcha-solver.com/getTaskResult", json={
            "clientKey": api_key,
            "taskId": task_id
        }, timeout=REQUEST_TIMEOUT).json()
        if result.get("errorId"):
            sys.exit(result.get("errorDescription", "Unknown error"))
        if result.get("status") == "ready":
            # Solution contains {"challenge": "...", "validate": "...", "seccode": "..."}
            print("result: " + str(result.get("solution")))
            break
        time.sleep(10)  # Wait 10 seconds before polling again.
    else:
        sys.exit("Timed out waiting for the captcha result.")
except Exception as e:
    sys.exit(e)
