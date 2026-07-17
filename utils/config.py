import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("CAPTCHA_API_KEY")

if not API_KEY:
    raise ValueError(
        "CAPTCHA_API_KEY environment variable is not set."
    )