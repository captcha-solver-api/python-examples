"""
Example: Solve a Yandex SmartCaptcha image challenge.

Prerequisites:
    Set the CAPTCHA_API_KEY environment variable.
    Provide the captcha image and instruction image as base64.
    Use imgType set to smart_captcha to select objects by instruction.
    imgInstructions is required.
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
POLL_TIMEOUT = 60       # Seconds to wait for the task to be solved before giving up.

# Selects objects on the captcha image following the instruction image (smart_captcha).
# imgInstructions is required. Without it, the worker may misunderstand the task.
try:
    # Read and encode the captcha image to base64.
    # The body must be a pure base64 string without the data:image/...;base64, prefix.
    with open("./captcha.png", "rb") as f:
        body = b64encode(f.read()).decode("utf-8")

    # Read and encode the instruction image to base64.
    # This image shows the worker what objects to click and in what order.
    with open("./instruction.png", "rb") as f:
        img_instructions = b64encode(f.read()).decode("utf-8")

    # Step 1: Create a task to solve the image-based Yandex SmartCaptcha.
    response = requests.post("https://api.captcha-solver.com/createTask", json={
        "clientKey": api_key,
        "task": {
            "type": "CoordinatesTask",
            "body": body,                                                     # Base64-encoded captcha image (required)
            "imgType": "smart_captcha",                                       # smart_captcha for object selection
            "imgInstructions": img_instructions,                              # Instruction image (required for smart_captcha)
            "comment": "select objects in the order of the instruction"       # Text hint for the worker (recommended)
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
            # Solution contains {"coordinates": [{"x": 57, "y": 82}, {"x": 239, "y": 75}, ...]}
            # Click on each coordinate in order as the instruction indicates.
            print("result: " + str(result.get("solution")))
            break
        time.sleep(3)  # Wait 3 seconds before polling again.
    else:
        sys.exit("Timed out waiting for the captcha result.")
except Exception as e:
    sys.exit(e)
