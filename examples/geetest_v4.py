"""
Example: Solve a GeeTest v4 challenge.

Prerequisites:
    Set the CAPTCHA_API_KEY environment variable.
    Replace websiteURL and captcha_id with values from your target page.
    GeeTest v4 drops gt/challenge entirely. It uses captcha_id instead.
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
POLL_TIMEOUT = 180      # Seconds to wait for the task to be solved before giving up. GeeTest v4 tasks may take longer.

# --- Proxyless example ---
# Solves GeeTest v4 without a proxy.
# v4 drops gt/challenge. The widget is identified by captcha_id inside initParameters.
try:
    # Create a task to solve the GeeTest v4 captcha.
    response = requests.post("https://api.captcha-solver.com/createTask", json={
        "clientKey": api_key,
        "task": {
            "type": "GeeTestTaskProxyless",
            "websiteURL": "https://example.com/login",                   # Full URL of the page with GeeTest v4
            "version": 4,                                                # Required: must be 4 for this version
            "initParameters": {                                          # Required: must contain captcha_id
                "captcha_id": "e392e1d7fd421dc63325744d5a2b9c73"         # Static site identifier
            }
            # Optional fields:
            # "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ..."  # Browser User-Agent
        }
    }, timeout=REQUEST_TIMEOUT).json()
    if response.get("errorId"):
        sys.exit(response.get("errorDescription", "Unknown error"))
    task_id = response.get("taskId")

    # Poll for the result until the task is ready or the timeout is reached.
    # GeeTest v4 tasks may take longer. Increase timeout if needed.
    deadline = time.time() + POLL_TIMEOUT
    while time.time() < deadline:
        result = requests.post("https://api.captcha-solver.com/getTaskResult", json={
            "clientKey": api_key,
            "taskId": task_id
        }, timeout=REQUEST_TIMEOUT).json()
        if result.get("errorId"):
            sys.exit(result.get("errorDescription", "Unknown error"))
        if result.get("status") == "ready":
            # Solution contains {"captcha_id": "...", "lot_number": "...", "pass_token": "...", "gen_time": "...", "captcha_output": "..."}
            # Pass these values together into the page's GeeTest v4 callback as-is.
            print("result: " + str(result.get("solution")))
            break
        time.sleep(10)  # Wait 10 seconds before polling again.
    else:
        sys.exit("Timed out waiting for the captcha result.")
except Exception as e:
    sys.exit(e)

# --- With proxy example ---
# Solves GeeTest v4 through your own proxy.
try:
    # Create a task with proxy parameters.
    response = requests.post("https://api.captcha-solver.com/createTask", json={
        "clientKey": api_key,
        "task": {
            "type": "GeeTestTask",
            "websiteURL": "https://example.com/login",                   # Full URL of the page with GeeTest v4
            "version": 4,                                                # Required: must be 4 for this version
            "initParameters": {                                          # Required: must contain captcha_id
                "captcha_id": "e392e1d7fd421dc63325744d5a2b9c73"         # Static site identifier
            },
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
            # Solution contains {"captcha_id": "...", "lot_number": "...", "pass_token": "...", "gen_time": "...", "captcha_output": "..."}
            print("result: " + str(result.get("solution")))
            break
        time.sleep(10)  # Wait 10 seconds before polling again.
    else:
        sys.exit("Timed out waiting for the captcha result.")
except Exception as e:
    sys.exit(e)
