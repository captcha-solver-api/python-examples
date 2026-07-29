"""
Example: Solve a click-based image captcha using CoordinatesTask.

Prerequisites:
    Set the CAPTCHA_API_KEY environment variable.
    Provide the captcha image as base64 in the body parameter.
    Use comment to tell the worker what to click on the image.
    No proxy is required. The image is submitted directly to the service.
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

# Read and encode the captcha image to base64.
# The body must be a pure base64 string without the data:image/...;base64, prefix.
with open("./captcha.png", "rb") as f:
    body = b64encode(f.read()).decode("utf-8")

# --- Basic example ---
# Solves a simple click-based captcha with a hint for the worker.
try:
    # Step 1: Create a task to solve the click-based captcha.
    # The worker will click on the specified points on the image.
    response = requests.post("https://api.captcha-solver.com/createTask", json={
        "clientKey": api_key,
        "task": {
            "type": "CoordinatesTask",
            "body": body,                                # Base64-encoded captcha image (required)
            "comment": "click on the green apple"        # Text hint for the worker
        }
    })
    task_id = response.json().get("taskId")

    # Step 2: Poll for the result until the task is ready.
    # The API processes the captcha asynchronously. Check the status periodically.
    while True:
        result = requests.post("https://api.captcha-solver.com/getTaskResult", json={
            "clientKey": api_key,
            "taskId": task_id
        }).json()
        if result.get("status") == "ready":
            # Solution contains {"coordinates": [{"x": 358, "y": 268}]}
            # Click on each coordinate in order. Coordinates are pixel positions.
            print("result: " + str(result.get("solution")))
            break
        time.sleep(3)  # Wait 3 seconds before polling again.
except Exception as e:
    sys.exit(e)

# --- Advanced example ---
# Solves a captcha with instruction image and click count limits.
try:
    # Read and encode an optional instruction image.
    # This image helps the worker understand what to click.
    with open("./instruction.png", "rb") as f:
        img_instructions = b64encode(f.read()).decode("utf-8")

    # Step 1: Create a task with more options.
    response = requests.post("https://api.captcha-solver.com/createTask", json={
        "clientKey": api_key,
        "task": {
            "type": "CoordinatesTask",
            "body": body,                                # Base64-encoded captcha image
            "comment": "click on all traffic lights",    # Text hint for the worker
            "imgInstructions": img_instructions,         # Optional instruction image
            "minClicks": 1,                              # Minimum number of clicks (default 1)
            "maxClicks": 3                               # Maximum number of clicks allowed
        }
    })
    task_id = response.json().get("taskId")

    # Step 2: Poll for the result until the task is ready.
    while True:
        result = requests.post("https://api.captcha-solver.com/getTaskResult", json={
            "clientKey": api_key,
            "taskId": task_id
        }).json()
        if result.get("status") == "ready":
            # Solution contains coordinates for all requested clicks.
            print("result: " + str(result.get("solution")))
            break
        time.sleep(3)  # Wait 3 seconds before polling again.
except Exception as e:
    sys.exit(e)