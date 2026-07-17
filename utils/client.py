import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("CAPTCHA_API_KEY")
BASE_URL = "https://api.captcha-solver.com"

def create_task(task_payload):
    response = requests.post(f"{BASE_URL}/createTask", json={
        "clientKey": API_KEY,
        "task": task_payload
    })
    return response.json()