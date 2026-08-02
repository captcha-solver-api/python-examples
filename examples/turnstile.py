"""
Example: Solve a Cloudflare Turnstile challenge.

Prerequisites:
    Set the CAPTCHA_API_KEY environment variable.
    Replace websiteURL and websiteKey with values from your target page.
    Pass action, data, and pageData if the target site uses them.
    Always pass userAgent for complex pages like Cloudflare Challenge.
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
# Solves Cloudflare Turnstile without a proxy.
# The token is tied to the User-Agent, so pass the same one your browser or bot uses.
try:
    # Step 1: Create a task to solve the Turnstile captcha.
    # Pass action, data (cData), or pageData if the site uses them.
    # For Cloudflare Challenge pages, you need to intercept turnstile.render to get these values.
    response = requests.post("https://api.captcha-solver.com/createTask", json={
        "clientKey": api_key,
        "task": {
            "type": "TurnstileTaskProxyless",
            "websiteURL": "https://example.com/login",                   # Full URL of the page with Turnstile
            "websiteKey": "0x4AAAAAAAVrOwQWPlm3Bnr5",                    # data-sitekey attribute value
            # Optional fields (pass only if the target site uses them):
            # "action": "login",                                         # Value of data-action attribute
            # "data": "custom-cdata-value",                              # Value of data-cdata attribute
            # "pageData": "chl-page-data-value",                         # Value of chlPageData parameter
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ..." # User-Agent your browser or bot uses
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
            # Solution contains {"token": "0.zxcv..."}
            # Pass this token to the cf-turnstile-response field or widget callback.
            print("result: " + str(result.get("solution")))
            break
        time.sleep(3)  # Wait 3 seconds before polling again.
    else:
        sys.exit("Timed out waiting for the captcha result.")
except Exception as e:
    sys.exit(e)

# --- With proxy example ---
# Solves Cloudflare Turnstile through your own proxy.
# Use when the target site is geo-restricted or you need a consistent session.
try:
    # Step 1: Create a task with proxy parameters.
    # Your proxy IP will be used to access the target site and solve the captcha.
    response = requests.post("https://api.captcha-solver.com/createTask", json={
        "clientKey": api_key,
        "task": {
            "type": "TurnstileTask",
            "websiteURL": "https://example.com/login",                   # Full URL of the page with Turnstile
            "websiteKey": "0x4AAAAAAAVrOwQWPlm3Bnr5",                    # data-sitekey attribute value
            # Proxy parameters:
            "proxyType": "http",        # http, socks4, or socks5
            "proxyAddress": "1.2.3.4",  # Proxy IP address
            "proxyPort": 8080,          # Proxy port
            "proxyLogin": "user",       # Login for proxy authorization (optional)
            "proxyPassword": "password",# Password for proxy authorization (optional)
            # Optional fields:
            # "action": "login",                                         # Value of data-action attribute
            # "data": "custom-cdata-value",                              # Value of data-cdata attribute
            # "pageData": "chl-page-data-value",                         # Value of chlPageData parameter
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ..." # User-Agent your browser or bot uses
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
            # Solution contains the same token.
            print("result: " + str(result.get("solution")))
            break
        time.sleep(3)  # Wait 3 seconds before polling again.
    else:
        sys.exit("Timed out waiting for the captcha result.")
except Exception as e:
    sys.exit(e)
