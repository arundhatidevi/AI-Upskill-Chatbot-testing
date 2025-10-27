## Chatbot UI Automation (Playwright + Pytest)

Automated end-to-end UI tests for the Sun Outdoors chatbot. Tests run Playwright in Python with pytest, validate responses (semantic similarity and intent), and produce artifacts (JUnit, Allure, screenshots, videos).

This README describes how to prepare a local environment, install dependencies and browsers, configure API keys, run tests, and troubleshoot common issues.

## Requirements

- Linux / macOS / Windows with WSL
- Python 3.10+ (3.12 used in CI for this repo)
- Git

## Quick setup (recommended)

1. Open a terminal and change to the repository root (where this README lives):

```bash
cd /path/to/milestone_UI_AUTOMATION(2)/milestone_UI_AUTOMATION
```

2. Create and activate a virtual environment (we use `venv` here):

```bash
python3 -m venv venv
source venv/bin/activate   # Unix / macOS
# On Windows (PowerShell): venv\Scripts\Activate.ps1
```

3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

4. Install Playwright browsers (required for UI tests):

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









