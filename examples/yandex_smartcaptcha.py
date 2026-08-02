"""
Example: Solve a Yandex SmartCaptcha challenge (token-based).

Prerequisites:
    Set the CAPTCHA_API_KEY environment variable.
    Replace websiteURL and websiteKey with values from your target page.
    This example uses the token-based method. For image-based solving, see the Coordinates example.
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
# Solves Yandex SmartCaptcha without a proxy.
# The service proxies are used to solve the captcha.
try:
    # Step 1: Create a task to solve the Yandex SmartCaptcha.
    # websiteKey is the sitekey value from the page code or captcha iframe.
    response = requests.post("https://api.captcha-solver.com/createTask", json={
        "clientKey": api_key,
        "task": {
            "type": "YandexSmartCaptchaTaskProxyless",
            "websiteURL": "https://example.com/login",                   # Full URL of the page with captcha
            "websiteKey": "FEXfAbHQsToo97VidNVk3j4dC74nGW1DgdxK4OoR",   # sitekey from page code or iframe
            # Optional fields:
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
            # Solution contains {"token": "dV9xNjYyNTU3NjkxO4k9OTQuNVMuMjkuMjM9..."}
            # Use solution.token in the smart-token field or pass to your site's backend.
            print("result: " + str(result.get("solution")))
            break
        time.sleep(3)  # Wait 3 seconds before polling again.
    else:
        sys.exit("Timed out waiting for the captcha result.")
except Exception as e:
    sys.exit(e)

# --- With proxy example ---
# Solves Yandex SmartCaptcha through your own proxy.
# Note: this is the only captcha type where https proxy is accepted.
try:
    # Step 1: Create a task with proxy parameters.
    # Your proxy IP will be used to access the target site and solve the captcha.
    response = requests.post("https://api.captcha-solver.com/createTask", json={
        "clientKey": api_key,
        "task": {
            "type": "YandexSmartCaptchaTask",
            "websiteURL": "https://example.com/login",                   # Full URL of the page with captcha
            "websiteKey": "FEXfAbHQsToo97VidNVk3j4dC74nGW1DgdxK4OoR",   # sitekey from page code or iframe
            # Proxy parameters:
            "proxyType": "http",        # http, https, socks4, or socks5 (https is accepted only for this type)
            "proxyAddress": "1.2.3.4",  # Proxy IP address
            "proxyPort": 8080,          # Proxy port
            "proxyLogin": "user",       # Login for proxy authorization (optional)
            "proxyPassword": "password",# Password for proxy authorization (optional)
            # Optional fields:
            # "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...",  # Browser User-Agent
            # "cookies": "session=abc123; token=xyz789"                   # Session cookies if needed
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
