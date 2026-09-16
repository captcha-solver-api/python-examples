# Captcha Solver API Python Examples

![python-examples-banner](assets/repo-banner-python.png)

Runnable examples for the official [`captcha-solver-api`](https://pypi.org/project/captcha-solver-api/) Python SDK.

## Installation

```bash
git clone https://github.com/captcha-solver-api/python-examples.git
cd python-examples
python -m venv .venv
```

Activate the environment and install dependencies:

```bash
python -m pip install -r requirements.txt
```

Set the API key:

```bash
# Linux/macOS
export CAPTCHA_API_KEY=your_api_key

# PowerShell
$env:CAPTCHA_API_KEY = "your_api_key"
```

You can also create a `.env` file:

```text
CAPTCHA_API_KEY=your_api_key
```

## Run examples

```bash
python examples/recaptcha_v2.py
python examples/turnstile.py
python examples/image_to_text.py
python examples/coordinates.py
python examples/balance.py
```

Replace placeholder URLs, site keys, application IDs, dynamic values, and proxy credentials before running token captcha examples. GeeTest v3 requires a fresh `challenge` value from the target page for every request.

Image examples use sample files from `assets/` and can run with only a valid API key.

## Included examples

| File | Task |
|---|---|
| `recaptcha_v2.py` | reCAPTCHA v2, proxyless and proxy |
| `recaptcha_v2_enterprise.py` | reCAPTCHA v2 Enterprise, proxyless and proxy |
| `recaptcha_v3.py` | reCAPTCHA v3 proxyless |
| `turnstile.py` | Cloudflare Turnstile, proxyless and proxy |
| `yandex_smartcaptcha.py` | Yandex SmartCaptcha token, proxyless and proxy |
| `yandex_smartcaptcha_image.py` | Yandex SmartCaptcha image mode |
| `image_to_text.py` | Image to Text |
| `coordinates.py` | Click coordinates |
| `geetest_v3.py` | GeeTest v3, proxyless and proxy |
| `geetest_v4.py` | GeeTest v4, proxyless and proxy |
| `tencent.py` | Tencent, proxyless and proxy |
| `balance.py` | Account balance |

Each example creates a task class from `captcha_solver_api.tasks` and calls `CaptchaClient.solve()`. Polling, API errors, network errors, and timeouts are handled by the SDK.

## Requirements

- Python 3.9+
- Captcha Solver account and API key
- Real target parameters for token captchas
- Working proxy for proxy examples

API documentation: https://captcha-solver.com/en/docs/captcha-types

## License

MIT. See [LICENSE.md](LICENSE.md).