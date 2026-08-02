"""
Example: Solve an Image to Text challenge.

Prerequisites:
    Set the CAPTCHA_API_KEY environment variable.
    Provide a captcha image file as base64 in the body parameter.
    Use optional fields to give hints to the worker for faster solving.
"""

import os
import sys
import time
import requests
from base64 import b64encode

# Load API key from environment variable or set it directly here.
# export CAPTCHA_API_KEY=1abc234de56fab7c89012d34e56fa7b8 on Linux or macOS.
# set CAPTCHA_API_KEY=1abc234de56fab7c89012d34e56fa7b8 on Windows.
api_key = os.getenv("CAPTCHA_API_KEY", "YOUR_API_KEY")

REQUEST_TIMEOUT = 30    # Seconds to wait for a single HTTP request.
POLL_TIMEOUT = 60       # Seconds to wait for the task to be solved before giving up. Image to Text tasks are usually fast.

# --- Basic example ---
# Solves a simple image captcha with character set hints.
try:
    # Read and encode the captcha image to base64.
    # The body must be a pure base64 string without the data:image/...;base64, prefix.
    with open("./captcha.png", "rb") as f:
        body = b64encode(f.read()).decode("utf-8")

    # Create a task to solve the image captcha.
    response = requests.post("https://api.captcha-solver.com/createTask", json={
        "clientKey": api_key,
        "task": {
            "type": "ImageToTextTask",
            "body": body,     # Base64-encoded image (required)
            "numeric": 1,     # 1 = digits only
            "minLength": 4,   # Minimum expected answer length
            "maxLength": 6    # Maximum expected answer length
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
            # Solution contains {"text": "aB3fX9"}
            # Submit solution.text to the target form field.
            print("result: " + str(result.get("solution")))
            break
        time.sleep(3)  # Wait 3 seconds before polling again.
    else:
        sys.exit("Timed out waiting for the captcha result.")
except Exception as e:
    sys.exit(e)

# --- Advanced example ---
# Solves a math captcha with comment and instruction image.
try:
    # Read and encode the hint image as base64.
    with open("./captcha_hint.png", "rb") as f:
        img_instructions = b64encode(f.read()).decode("utf-8")

    # Create a task with optional hints for the worker.
    response = requests.post("https://api.captcha-solver.com/createTask", json={
        "clientKey": api_key,
        "task": {
            "type": "ImageToTextTask",
            "body": body,                                            # Base64-encoded captcha image
            # Optional fields (pass only if needed by the captcha type):
            "phrase": False,                                         # True if answer has multiple words
            "case": True,                                            # True if answer is case-sensitive
            "numeric": 0,                                            # 0 = not specified, 1 = digits, 2 = letters, 3 = any with digits, 4 = any with letters
            "math": True,                                            # True if image is a math expression to solve
            "minLength": 1,                                          # Minimum answer length
            "maxLength": 10,                                         # Maximum answer length
            "comment": "Enter the result of the equation",           # Text hint for the worker
            "imgInstructions": img_instructions                      # Optional instruction image for the worker
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
            print("result: " + str(result.get("solution")))
            break
        time.sleep(3)  # Wait 3 seconds before polling again.
    else:
        sys.exit("Timed out waiting for the captcha result.")
except Exception as e:
    sys.exit(e)
