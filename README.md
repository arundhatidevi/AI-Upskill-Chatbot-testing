## Chatbot UI Automation (Playwright + Pytest)

Automated end-to-end UI tests for the Sun Outdoors chatbot. Tests run Playwright in Python with pytest, validate responses (semantic similarity and intent), and produce artifacts (JUnit, Allure, screenshots, videos).

This README describes how to prepare a local environment, install dependencies and browsers, configure API keys, run tests, and troubleshoot common issues.

## Requirements

- Linux / macOS / Windows with WSL
- Python 3.10+ (3.12 used in CI for this repo)
- Git

## Setup Guide

### 1. Clone the Repository

First, clone this repository to your local machine:

```bash
# Clone the repository
git clone https://github.com/arundhatidevi/AI-Upskill-Chatbot-testing.git

# Navigate to the project directory
cd AI-Upskill-Chatbot-testing
```

### 2. Set Up Python Virtual Environment

#### Install Python (if not already installed)

- For Ubuntu/Debian:
  ```bash
  sudo apt update
  sudo apt install python3.12 python3.12-venv
  ```
- For macOS (using Homebrew):
  ```bash
  brew install python@3.12
  ```
- For Windows:
  - Download Python 3.12 from [python.org](https://www.python.org/downloads/)
  - Make sure to check "Add Python to PATH" during installation

#### Create and Activate Virtual Environment

We use `venv` to create an isolated Python environment:

```bash
# For Unix/macOS:
python3 -m venv venv
source venv/bin/activate

# For Windows (Command Prompt):
python -m venv venv
.\venv\Scripts\activate.bat

# For Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

Once your virtual environment is activated (you should see `(venv)` in your terminal prompt), install the required packages:

```bash
# Upgrade pip to latest version
python -m pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt
```

The main dependencies include:
- pytest: Testing framework
- playwright: Browser automation
- pydantic: Data validation
- python-dotenv: Environment variable management
- allure-pytest: Test reporting
- openai: For semantic analysis

### 4. Install Playwright Browsers

Playwright needs to install browser binaries for automation:

```bash
venv/bin/playwright install
```

5. Configure environment variables. Create a `.env` file in the repository root with the following keys at minimum:

```text
# .env (example)
OPENAI_API_KEY=sk-...            # REQUIRED for semantic and intent validators
BASE_URL=https://sunrv-chatbot.dev02cms.milestoneinternet.info/?_enablechatbot=true
# Optional:
# RECORD_VIDEO=true
# SCREENSHOT_ON_FAILURE=true
# CHAT_MODEL=gpt-4
# EMBEDDING_MODEL=text-embedding-3-small
```

Important: Keep your `OPENAI_API_KEY` secret. Do not commit `.env` to the repository. `.gitignore` already ignores `.env` and virtualenv directories.

## Run tests

Activate your venv (if not already active) and run pytest. Example commands:

Run all tests (recommended):

```bash
source venv/bin/activate
venv/bin/python -m pytest -v
```

Run the conversation flow test only:

```bash
venv/bin/python -m pytest tests/test_conversation_flows.py -v
```

Run a single test function or add `-k` to filter by name:

```bash
venv/bin/python -m pytest -k "conversation_flow" -v
```

Test artifacts will be saved to the `artifacts/` directory:

- `artifacts/junit/` — JUnit XML
- `artifacts/allure/` — Allure result JSON
- `artifacts/logs/`, `artifacts/screenshots/`, `artifacts/videos/`

## Common configuration points

- `src/config.py` holds defaults for `BASE_URL`, selectors and thresholds.
- `tests/data/*.yaml` contains test case definitions used by parametrized tests.

## Troubleshooting

### Virtual Environment Issues

- If `venv` creation fails:
  ```bash
  # Make sure python3-venv is installed
  # On Ubuntu/Debian:
  sudo apt install python3.12-venv
  
  # Try creating venv with full path to Python
  /usr/bin/python3.12 -m venv venv
  ```

- If activation doesn't work:
  - On Unix/macOS: Make sure you're using `source venv/bin/activate`
  - On Windows: Try both `.\venv\Scripts\activate.bat` (CMD) and `.\venv\Scripts\Activate.ps1` (PowerShell)
  - Check if virtualenv is installed: `python -m pip install --user virtualenv`

- If pip install fails:
  ```bash
  # Make sure your venv is activated (you should see (venv) in prompt)
  # Then try updating pip first:
  python -m pip install --upgrade pip setuptools wheel
  
  # Then retry installing requirements
  pip install -r requirements.txt
  ```

### Playwright Issues

- Playwright/Browser not found: make sure `venv/bin/playwright install` completed successfully. Re-run it if needed.
- `TimeoutError: Page.wait_for_selector` in tests: this usually means the page/chat widget took longer to render or the selector changed. Try:
  - Increasing selector timeout in the test or Playwright config
  - Verifying `BASE_URL` is correct and the chatbot is enabled
  - Opening the page manually in a browser and inspecting the elements used by selectors
- OpenAI errors (authentication / rate limit / quota):
  - Ensure `OPENAI_API_KEY` in `.env` is valid and has quota
  - If you don't have an OpenAI key, tests that call the embedding or intent validators will fail. You can either provide a valid key or temporarily skip semantic/intent checks (by editing tests), but be careful — skipping reduces validation coverage.

## Continuous Integration

- A GitHub Actions workflow (`.github/workflows/ci.yml`) is included. The workflow installs dependencies, Playwright browsers, runs the tests, and uploads artifacts.
- If you enable Actions in the GitHub repo, ensure secrets are configured for `OPENAI_API_KEY` (Repository Settings -> Secrets) so CI can run semantic validators.

## Developer notes & extensions

- To add new conversation flows, edit `tests/data/conversation_flows.yaml` and add a new test case. Tests are parameterized using that file.
- To add more validators, implement them under `src/validators/` and call from the test runner (`src/utils/conversation_runner.py`).

## Example: run a single test locally

```bash
cd /path/to/repo
source venv/bin/activate
venv/bin/python -m pytest tests/test_conversation_flows.py::test_conversation_flow -q -k complete_booking_flow_with_button_send
```

## License & contributions

See `README.md` or the repository root for contribution guidelines. If you want, I can add a CONTRIBUTING.md or expand the CI to run matrix testing across multiple browsers.

---

If you'd like, I can also:

- Add badges to the README (CI, coverage)
- Add a script to create the venv and install dependencies (`setup.sh` is included in the repo)
- Add an environment-safe toggle to tests to skip OpenAI-based validations when no key is present

If you want me to commit and push this README update, tell me to proceed (I'll commit and push to `origin/main`).









