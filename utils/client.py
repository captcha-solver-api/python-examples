import time
import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("CAPTCHA_API_KEY")
BASE_URL = "https://api.captcha-solver.com"

REQUEST_TIMEOUT = 30
POLL_INTERVAL = 3
POLL_TIMEOUT = 120


def create_task(task_payload):
    response = requests.post(f"{BASE_URL}/createTask", json={
        "clientKey": API_KEY,
        "task": task_payload
    }, timeout=REQUEST_TIMEOUT).json()
    if response.get("errorId"):
        raise RuntimeError(response.get("errorDescription", "Unknown error"))
    return response["taskId"]


def get_task_result(task_id):
    response = requests.post(f"{BASE_URL}/getTaskResult", json={
        "clientKey": API_KEY,
        "taskId": task_id
    }, timeout=REQUEST_TIMEOUT).json()
    if response.get("errorId"):
        raise RuntimeError(response.get("errorDescription", "Unknown error"))
    return response


def solve_task(task_payload):
    task_id = create_task(task_payload)
    deadline = time.time() + POLL_TIMEOUT
    while time.time() < deadline:
        result = get_task_result(task_id)
        if result.get("status") == "ready":
            return result.get("solution")
        time.sleep(POLL_INTERVAL)
    raise TimeoutError("Timed out waiting for the captcha result.")
