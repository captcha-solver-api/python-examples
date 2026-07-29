"""
Example: Solve a Yandex SmartCaptcha image challenge.

Prerequisites:
    Set the CAPTCHA_API_KEY environment variable.
    Provide the captcha image and instruction image as base64.
    Use imgType to specify smart_captcha (select objects) or pazl_smart_captcha (puzzle).
    For smart_captcha, imgInstructions is required.
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

# --- Option 1: Selecting objects by instruction (smart_captcha) ---
# The worker selects objects on the captcha image following the instruction image.
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
    })
    task_id = response.json().get("taskId")

    # Step 2: Poll for the result until the task is ready.
    while True:
        result = requests.post("https://api.captcha-solver.com/getTaskResult", json={
            "clientKey": api_key,
            "taskId": task_id
        }).json()
        if result.get("status") == "ready":
            # Solution contains {"coordinates": [{"x": 57, "y": 82}, {"x": 239, "y": 75}, ...]}
            # Click on each coordinate in order as the instruction indicates.
            print("result: " + str(result.get("solution")))
            break
        time.sleep(3)  # Wait 3 seconds before polling again.
except Exception as e:
    sys.exit(e)

# --- Option 2: Puzzle captcha (pazl_smart_captcha) ---
# The worker solves a puzzle by dragging a slider to the correct position.
# Only body and imgType are required. No instruction image is needed.
try:
    # Read and encode the puzzle captcha image to base64.
    with open("./puzzle.png", "rb") as f:
        body = b64encode(f.read()).decode("utf-8")

    # Step 1: Create a task to solve the puzzle captcha.
    response = requests.post("https://api.captcha-solver.com/createTask", json={
        "clientKey": api_key,
        "task": {
            "type": "CoordinatesTask",
            "body": body,                      # Base64-encoded puzzle image (required)
            "imgType": "pazl_smart_captcha"    # pazl_smart_captcha for puzzle solving
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
            # Solution contains coordinates with the slider position.
            print("result: " + str(result.get("solution")))
            break
        time.sleep(3)  # Wait 3 seconds before polling again.
except Exception as e:
    sys.exit(e)