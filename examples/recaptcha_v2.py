import time
import os
import requests
from seleniumbase import SB
from dotenv import load_dotenv

# Load API credentials from .env file
load_dotenv()
API_KEY = os.getenv("CAPTCHA_API_KEY")
API_BASE = "https://api.captcha-solver.com"

def solve_recaptcha_v2(driver, api_key):
    """
    Solves reCAPTCHA v2 challenges using the Captcha Solver API.
    Returns the solved token string upon success, or None if an error occurs.
    """

    def find_sitekey():
        """
        Attempts to locate the 'sitekey' parameter required by the API.
        Checks for data-sitekey attribute, iframe source, and internal config.
        """
        # Method 1: Locate via HTML data-sitekey attribute
        try:
            sitekey = driver.execute_script("""
                let el = document.querySelector("[data-sitekey]");
                return el ? el.getAttribute("data-sitekey") : null;
            """)
            if sitekey:
                return sitekey, None
        except Exception as e:
            print(f"data-sitekey search error: {e}")

        # Method 2: Extract from reCAPTCHA iframe URL
        try:
            src = driver.execute_script("""
                let frame = document.querySelector('iframe[src*="recaptcha"]');
                return frame ? frame.src : null;
            """)
            if src and "k=" in src:
                import re
                match = re.search(r"[?&]k=([^&]+)", src)
                if match:
                    return match.group(1), None
        except Exception as e:
            print(f"iframe search error: {e}")

        # Method 3: Parse internal Google reCAPTCHA configuration object
        try:
            result = driver.execute_script("""
                if(typeof ___grecaptcha_cfg === 'undefined') return null;
                for(const cid in ___grecaptcha_cfg.clients) {
                    const client = ___grecaptcha_cfg.clients[cid];
                    for(const k1 in client) {
                        const obj = client[k1];
                        if(typeof obj !== "object") continue;
                        for(const k2 in obj) {
                            const item = obj[k2];
                            if(item && typeof item === "object" && item.sitekey) {
                                return { sitekey: item.sitekey, callback: item.callback || null };
                            }
                        }
                    }
                }
                return null;
            """)
            if result:
                return result["sitekey"], result.get("callback")
        except Exception as e:
            print(f"grecaptcha_cfg search error: {e}")

        return None, None

    # Step 1: Identify the site parameters
    sitekey, callback = find_sitekey()
    if not sitekey:
        print("[-] Error: Could not find sitekey.")
        return None

    page_url = driver.current_url
    print(f"[*] Target URL: {page_url}")

    # Step 2: Prepare task payload
    # 'clientKey' is mandatory. The parameters are nested inside the 'task' object.
    payload = {
        "clientKey": api_key,
        "task": {
            "type": "RecaptchaV2TaskProxyless",
            "websiteURL": page_url,
            "websiteKey": sitekey,
        },
    }

    # Step 3: Submit the task
    print("[*] Submitting task to API...")
    try:
        r = requests.post(f"{API_BASE}/createTask", json=payload, timeout=60)
        data = r.json()
    except Exception as e:
        print(f"API request error: {e}")
        return None

    # Always check errorId: 0 indicates success
    if data.get("errorId") != 0:
        print(f"API Error during task creation: {data}")
        return None

    task_id = data["taskId"]
    print(f"[+] Task created. ID: {task_id}")

    # Step 4: Poll for results (Asynchronous workflow)
    time.sleep(5)  # Wait for initial processing
    token = None

    while True:
        try:
            r = requests.post(f"{API_BASE}/getTaskResult", json={
                "clientKey": api_key,
                "taskId": task_id,
            }, timeout=60)
            data = r.json()
        except Exception as e:
            print(f"Polling error: {e}")
            break

        if data.get("errorId") != 0:
            print(f"API Error during polling: {data}")
            break

        status = data.get("status")
        print(f"[*] Current status: {status}")

        if status == "ready":
            token = data["solution"]["gRecaptchaResponse"]
            print("[+] CAPTCHA solved successfully.")
            break
        elif status == "processing":
            time.sleep(5)  # Wait before next poll
        else:
            print(f"Unexpected status: {status}")
            break

    if not token:
        return None

    # Step 5: Inject the token into the page
    driver.execute_script("""
        const token = arguments[0];
        document.querySelectorAll('[name="g-recaptcha-response"]').forEach(el => {
            el.style.display = 'block';
            el.value = token;
            el.dispatchEvent(new Event('input', {bubbles: true}));
            el.dispatchEvent(new Event('change', {bubbles: true}));
        });
    """, token)

    # Step 6: Trigger callback if required by the site
    if callback:
        driver.execute_script("arguments[0](arguments[1]);", callback, token)

    return token

if __name__ == "__main__":
    if not API_KEY:
        print("[-] Error: CAPTCHA_API_KEY not found in environment.")
    else:
        with SB(uc=True, test=False) as sb:
            sb.open("https://www.google.com/recaptcha/api2/demo")
            sb.reconnect(0.1)
            token = solve_recaptcha_v2(sb.driver, API_KEY)
            if token:
                print(f"\n[+] Final Token: {token[:20]}...")