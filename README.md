# Captcha Solver API Python Examples
![python-examples-banner](assets/repo-banner-python.png)
A collection of examples for interacting with the [Captcha Solver](https://captcha-solver.com/) service.
This project demonstrates how to send HTTP requests to the API for solving CAPTCHA challenges. You will find examples for reCAPTCHA v2, reCAPTCHA v3, Cloudflare Turnstile, Yandex SmartCaptcha, GeeTest, Tencent, and image-based tasks. The code helps automate task creation, status polling, and result retrieval.
## Table of Contents
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Supported CAPTCHA Types](#supported-types)
- [Usage Examples](#usage-examples)
  - [reCAPTCHA v2](#recaptcha-v2)
  - [reCAPTCHA v2 Enterprise](#recaptcha-v2-enterprise)
  - [reCAPTCHA v3](#recaptcha-v3)
  - [Cloudflare Turnstile](#cloudflare-turnstile)
  - [Yandex SmartCaptcha](#yandex-smartcaptcha)
  - [Image to Text](#image-to-text)
  - [Coordinates](#coordinates)
  - [GeeTest v3](#geetest-v3)
  - [GeeTest v4](#geetest-v4)
  - [Tencent](#tencent)
  - [Check Balance](#check-balance)
  - [Custom Timeout and Polling](#custom-timeout-and-polling)
  - [Error Handling](#error-handling)
- [Requirements](#requirements)
- [API Documentation](#api-documentation)
- [License](#license)
---
## Installation
Clone the repository:
```bash
git clone https://github.com/captcha-solver-api/python-examples.git
cd python-examples
```
Install dependencies:
```bash
pip install -r requirements.txt
```
Create a `.env` file in the root directory:
```text
CAPTCHA_API_KEY=your_api_key
```
Run an example:
```bash
python examples/recaptcha_v2.py
```
---
## Quick Start
This single example solves a reCAPTCHA v2. It creates a task, polls for the result, and prints the solution token.
```python
import requests
import time
API_KEY = "YOUR_API_KEY"
response = requests.post("https://api.captcha-solver.com/createTask", json={
    "clientKey": API_KEY,
    "task": {
        "type": "RecaptchaV2TaskProxyless",
        "websiteURL": "https://example.com/login",
        "websiteKey": "SITE_KEY"
    }
}, timeout=30).json()
if response.get("errorId"):
    raise SystemExit(response.get("errorDescription"))
task_id = response.get("taskId")
deadline = time.time() + 120
while time.time() < deadline:
    result = requests.post("https://api.captcha-solver.com/getTaskResult", json={
        "clientKey": API_KEY,
        "taskId": task_id
    }, timeout=30).json()
    if result.get("errorId"):
        raise SystemExit(result.get("errorDescription"))
    if result.get("status") == "ready":
        print(result.get("solution", {}).get("gRecaptchaResponse"))
        break
    time.sleep(3)
else:
    print("Timed out waiting for the captcha result.")
```
---
## Supported Types
| Type | Proxyless | With Proxy |
|---|---|---|
| reCAPTCHA v2 | ✅ | ✅ |
| reCAPTCHA v2 Enterprise | ✅ | ✅ |
| reCAPTCHA v3 | ✅ | ❌ |
| Cloudflare Turnstile | ✅ | ✅ |
| Yandex SmartCaptcha (token) | ✅ | ✅ |
| Yandex SmartCaptcha (image) | ✅ | ❌ |
| Image to Text | ✅ | ❌ |
| Coordinates | ✅ | ❌ |
| GeeTest v3 | ✅ | ✅ |
| GeeTest v4 | ✅ | ✅ |
| Tencent | ✅ | ✅ |
---
## Usage Examples
### reCAPTCHA v2
Uses `RecaptchaV2TaskProxyless`. Add `isInvisible`, `apiDomain`, `userAgent`, or `cookies` if your target page requires them. Use `RecaptchaV2Task` for your own proxy. See the official docs for reCAPTCHA v2 parameters and response format [here](https://captcha-solver.com/en/docs/captcha-types#recaptcha-v2).
```python
response = requests.post("https://api.captcha-solver.com/createTask", json={
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type": "RecaptchaV2TaskProxyless",
        "websiteURL": "https://example.com",
        "websiteKey": "SITE_KEY",
        "isInvisible": False
    }
}, timeout=30)
task_id = response.json().get("taskId")
```
### reCAPTCHA v2 Enterprise
Uses `RecaptchaV2EnterpriseTaskProxyless`. Pass `enterprisePayload` if the site uses `grecaptcha.enterprise.render` with extra parameters. Use `RecaptchaV2EnterpriseTask` for your own proxy. See the official docs for reCAPTCHA v2 Enterprise parameters and response format [here](https://captcha-solver.com/en/docs/captcha-types#recaptcha-v2-enterprise).
```python
response = requests.post("https://api.captcha-solver.com/createTask", json={
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type": "RecaptchaV2EnterpriseTaskProxyless",
        "websiteURL": "https://example.com",
        "websiteKey": "SITE_KEY",
        "enterprisePayload": {"s": "SITE_SPECIFIC_DATA"}
    }
}, timeout=30)
task_id = response.json().get("taskId")
```
### reCAPTCHA v3
Uses `RecaptchaV3TaskProxyless`. Set `minScore` to the required threshold. Pass `pageAction` if known. Set `isEnterprise` to `true` for reCAPTCHA v3 Enterprise. See the official docs for reCAPTCHA v3 parameters and response format [here](https://captcha-solver.com/en/docs/captcha-types#recaptcha-v3).
```python
response = requests.post("https://api.captcha-solver.com/createTask", json={
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type": "RecaptchaV3TaskProxyless",
        "websiteURL": "https://example.com",
        "websiteKey": "SITE_KEY",
        "minScore": 0.3,
        "pageAction": "login"
    }
}, timeout=30)
task_id = response.json().get("taskId")
```
### Cloudflare Turnstile
Uses `TurnstileTaskProxyless`. Pass `action`, `data` (cData), or `pagedata` if the site uses them. The returned token is only valid together with the `userAgent` in the solution — use both, not the User-Agent your own bot sent the request with. Use `TurnstileTask` for your own proxy. See the official docs for Cloudflare Turnstile parameters and response format [here](https://captcha-solver.com/en/docs/captcha-types#cloudflare-turnstile).
```python
response = requests.post("https://api.captcha-solver.com/createTask", json={
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type": "TurnstileTaskProxyless",
        "websiteURL": "https://example.com",
        "websiteKey": "SITE_KEY"
    }
}, timeout=30)
task_id = response.json().get("taskId")
```
### Yandex SmartCaptcha
Token-based solving uses `YandexSmartCaptchaTaskProxyless` or `YandexSmartCaptchaTask`. Image-based solving uses `CoordinatesTask` with `imgType` set to `smart_captcha`. See the Coordinates section for image examples. See the official docs for Yandex SmartCaptcha parameters and response format [here](https://captcha-solver.com/en/docs/captcha-types#yandex-smartcaptcha).
```python
response = requests.post("https://api.captcha-solver.com/createTask", json={
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type": "YandexSmartCaptchaTaskProxyless",
        "websiteURL": "https://example.com",
        "websiteKey": "Y5Lh0ti..."
    }
}, timeout=30)
task_id = response.json().get("taskId")
```
### Image to Text
Uses `ImageToTextTask`. Set `numeric`, `minLength`, `maxLength`, or `case` to improve accuracy. Add `comment` for worker instructions. See the official docs for Image to Text parameters and response format [here](https://captcha-solver.com/en/docs/captcha-types#image-to-text).
```python
import base64
with open("captcha.png", "rb") as f:
    img_base64 = base64.b64encode(f.read()).decode("utf-8")
response = requests.post("https://api.captcha-solver.com/createTask", json={
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type": "ImageToTextTask",
        "body": img_base64,
        "numeric": 1,
        "minLength": 4,
        "maxLength": 6
    }
}, timeout=30)
task_id = response.json().get("taskId")
```
### Coordinates
Uses `CoordinatesTask`. Works for click-based captchas and Yandex SmartCaptcha image challenges. Set `imgType` to `smart_captcha` for Yandex. Always pass `imgInstructions` for `smart_captcha`. See the official docs for Coordinates parameters and response format [here](https://captcha-solver.com/en/docs/captcha-types#coordinates).
```python
import base64
with open("captcha.png", "rb") as f:
    img_base64 = base64.b64encode(f.read()).decode("utf-8")
response = requests.post("https://api.captcha-solver.com/createTask", json={
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type": "CoordinatesTask",
        "body": img_base64,
        "comment": "click on the green apple"
    }
}, timeout=30)
task_id = response.json().get("taskId")
```
### GeeTest v3
Uses `GeeTestTaskProxyless` or `GeeTestTask`. Requires fresh `gt` and `challenge` values from the target page on each request. Version defaults to 3. See the official docs for GeeTest v3 parameters and response format [here](https://captcha-solver.com/en/docs/captcha-types#geetest-v3).
```python
response = requests.post("https://api.captcha-solver.com/createTask", json={
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type": "GeeTestTaskProxyless",
        "websiteURL": "https://example.com",
        "gt": "f2ae6cadcf7886856696c46d84d109d1",
        "challenge": "12345678abc90123d45678e90123f45g6"
    }
}, timeout=30)
task_id = response.json().get("taskId")
```
### GeeTest v4
Uses `GeeTestTaskProxyless` or `GeeTestTask`. Set `version` to 4. Pass `initParameters` with `captcha_id` from the target page. See the official docs for GeeTest v4 parameters and response format [here](https://captcha-solver.com/en/docs/captcha-types#geetest-v4).
```python
response = requests.post("https://api.captcha-solver.com/createTask", json={
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type": "GeeTestTaskProxyless",
        "websiteURL": "https://example.com",
        "version": 4,
        "initParameters": {"captcha_id": "e392e65f912c780f2c3ebac7702651de"}
    }
}, timeout=30)
task_id = response.json().get("taskId")
```
### Tencent
Uses `TencentTaskProxyless` or `TencentTask`. Requires `appId` from the page source. Pass `captchaScript` if the site uses a non-default script URL. See the official docs for Tencent parameters and response format [here](https://captcha-solver.com/en/docs/captcha-types#tencent).
```python
response = requests.post("https://api.captcha-solver.com/createTask", json={
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type": "TencentTaskProxyless",
        "websiteURL": "https://example.com",
        "appId": "190014885"
    }
}, timeout=30)
task_id = response.json().get("taskId")
```
### Check Balance
```python
response = requests.post("https://api.captcha-solver.com/getBalance", json={
    "clientKey": "YOUR_API_KEY"
}, timeout=30)
print(response.json().get("balance"))
```
### Custom Timeout and Polling
```python
import time
task_id = "YOUR_TASK_ID"
timeout = 120
start_time = time.time()
while True:
    if time.time() - start_time > timeout:
        print("Timeout reached")
        break
    result = requests.post("https://api.captcha-solver.com/getTaskResult", json={
        "clientKey": "YOUR_API_KEY",
        "taskId": task_id
    }, timeout=30).json()
    if result.get("errorId"):
        print(f"Error: {result.get('errorDescription')}")
        break
    if result.get("status") == "ready":
        print(result.get("solution"))
        break
    time.sleep(3)
```
### Error Handling
```python
response = requests.post("https://api.captcha-solver.com/createTask", json={
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type": "RecaptchaV2TaskProxyless",
        "websiteURL": "https://example.com",
        "websiteKey": "INVALID_KEY"
    }
}, timeout=30)
data = response.json()
if data.get("errorId") != 0:
    print(f"Error: {data.get('errorDescription')}")
```
---
## Requirements
* Python 3.8+
* [Captcha Solver](https://captcha-solver.com/) account and API key
* `requests` library (included in requirements.txt)
---
## API Documentation

See the [official service documentation](https://captcha-solver.com/en/docs/captcha-types) for full descriptions of task parameters and endpoints.

---
## License
This project is licensed under the MIT License. See [LICENSE.md](LICENSE.md) for details.