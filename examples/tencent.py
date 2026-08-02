"""
Example: Solve a Tencent captcha challenge.

Prerequisites:
    Set the CAPTCHA_API_KEY environment variable.
    Replace websiteURL and appId with values from your target page.
    Pass captchaScript if the site uses a non-default script URL.
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
POLL_TIMEOUT = 120      # Seconds to wait for the task to be solved before giving up.

# --- Proxyless example ---
# Solves Tencent captcha without a proxy.
# The service proxies are used to solve the captcha.
try:
    # Step 1: Create a task to solve the Tencent captcha.
    # appId is found in the page source code. captchaScript is optional if the site uses the default.
    response = requests.post("https://api.captcha-solver.com/createTask", json={
        "clientKey": api_key,
        "task": {
            "type": "TencentTaskProxyless",
            "websiteURL": "https://example.com/login",                   # Full URL of the page with captcha
            "appId": "190014885",                                        # appId from page source code (required)
            # Optional fields:
            # "captchaScript": "https://turing.captcha.qcloud.com/TCaptcha.js"  # Custom script URL if non-default
        }
    }, timeout=REQUEST_TIMEOUT).json()
    if response.get("errorId"):
        sys.exit(response.get("errorDescription", "Unknown error"))
    task_id = response.get("taskId")

    # Step 2: Poll for the result until the task is ready or the timeout is reached.
    # The API processes the captcha asynchronously. Check the status periodically.
    deadline = time.time() + POLL_TIMEOUT
    while time.time() < deadline:
        result = requests.post("https://api.captcha-solver.com/getTaskResult", json={
            "clientKey": api_key,
            "taskId": task_id
        }, timeout=REQUEST_TIMEOUT).json()
        if result.get("errorId"):
            sys.exit(result.get("errorDescription", "Unknown error"))
        if result.get("status") == "ready":
            # Solution contains {"appid": "...", "ret": 0, "ticket": "...", "randstr": "..."}
            # Pass all four values together into the page's captcha callback as-is.
            print("result: " + str(result.get("solution")))
            break
        time.sleep(3)  # Wait 3 seconds before polling again.
    else:
        sys.exit("Timed out waiting for the captcha result.")
except Exception as e:
    sys.exit(e)

# --- With proxy example ---
# Solves Tencent captcha through your own proxy.
# Use when the target site is geo-restricted or you need a consistent session.
try:
    # Step 1: Create a task with proxy parameters.
    # Your proxy IP will be used to access the target site and solve the captcha.
    response = requests.post("https://api.captcha-solver.com/createTask", json={
        "clientKey": api_key,
        "task": {
            "type": "TencentTask",
            "websiteURL": "https://example.com/login",                   # Full URL of the page with captcha
            "appId": "190014885",                                        # appId from page source code (required)
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

    # Step 2: Poll for the result until the task is ready or the timeout is reached.
    deadline = time.time() + POLL_TIMEOUT
    while time.time() < deadline:
        result = requests.post("https://api.captcha-solver.com/getTaskResult", json={
            "clientKey": api_key,
            "taskId": task_id
        }, timeout=REQUEST_TIMEOUT).json()
        if result.get("errorId"):
            sys.exit(result.get("errorDescription", "Unknown error"))
        if result.get("status") == "ready":
            # Solution contains the same appid, ret, ticket, and randstr values.
            print("result: " + str(result.get("solution")))
            break
        time.sleep(3)  # Wait 3 seconds before polling again.
    else:
        sys.exit("Timed out waiting for the captcha result.")
except Exception as e:
    sys.exit(e)
