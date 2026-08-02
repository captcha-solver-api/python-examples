"""
Example: Solve a reCAPTCHA v2 Enterprise challenge.

Prerequisites:
    Set the CAPTCHA_API_KEY environment variable.
    Replace websiteURL and websiteKey with values from your target page.
    If the site uses enterprisePayload, extract and pass it or the token may be rejected.
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
# Solves reCAPTCHA v2 Enterprise without a proxy.
# Enterprise captchas are loaded via the reCAPTCHA Enterprise API.
# If the site passes extra parameters to grecaptcha.enterprise.render(),
# you must pass them as enterprisePayload or the token will be rejected.
try:
    # Step 1: Create a task to solve the reCAPTCHA v2 Enterprise captcha.
    # The API returns a taskId that you use to poll for the result.
    response = requests.post("https://api.captcha-solver.com/createTask", json={
        "clientKey": api_key,
        "task": {
            "type": "RecaptchaV2EnterpriseTaskProxyless",
            "websiteURL": "https://example.com/login",                   # Full URL of the page with captcha
            "websiteKey": "6Le-xxxxxxxxxxxxxxxxxxxxxxxxxxxx",            # data-sitekey attribute value
            "isInvisible": False,                                        # Set True for invisible reCAPTCHA
            # Optional fields (pass only if the target site requires them):
            # "enterprisePayload": {"s": "value-from-page"},             # Extra params from grecaptcha.enterprise.render()
            # "apiDomain": "recaptcha.net",                               # Set if site loads captcha from recaptcha.net
            # "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...",  # Browser User-Agent
            # "cookies": "session=abc123; token=xyz789"                   # Session cookies if needed
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
            # Solution contains {"gRecaptchaResponse": "03AGdBq..."}
            # Pass this token to the g-recaptcha-response field or widget callback.
            print("result: " + str(result.get("solution")))
            break
        time.sleep(3)  # Wait 3 seconds before polling again.
    else:
        sys.exit("Timed out waiting for the captcha result.")
except Exception as e:
    sys.exit(e)

# --- With proxy example ---
# Solves reCAPTCHA v2 Enterprise through your own proxy.
# Use when the target site is geo-restricted or you need a consistent session.
try:
    # Step 1: Create a task with proxy parameters.
    # Your proxy IP will be used to access the target site and solve the captcha.
    response = requests.post("https://api.captcha-solver.com/createTask", json={
        "clientKey": api_key,
        "task": {
            "type": "RecaptchaV2EnterpriseTask",
            "websiteURL": "https://example.com/login",                   # Full URL of the page with captcha
            "websiteKey": "6Le-xxxxxxxxxxxxxxxxxxxxxxxxxxxx",            # data-sitekey attribute value
            # Proxy parameters:
            "proxyType": "http",        # http, socks4, or socks5
            "proxyAddress": "1.2.3.4",  # Proxy IP address
            "proxyPort": 8080,          # Proxy port
            "proxyLogin": "user",       # Login for proxy authorization (optional)
            "proxyPassword": "password",# Password for proxy authorization (optional)
            # Optional fields:
            "isInvisible": False,
            # "enterprisePayload": {"s": "value-from-page"},             # Extra params from grecaptcha.enterprise.render()
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...",  # Browser User-Agent
            "cookies": "foo=bar; baz=1"                                  # Session cookies if needed
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
            # Solution contains the same gRecaptchaResponse token.
            print("result: " + str(result.get("solution")))
            break
        time.sleep(3)  # Wait 3 seconds before polling again.
    else:
        sys.exit("Timed out waiting for the captcha result.")
except Exception as e:
    sys.exit(e)
