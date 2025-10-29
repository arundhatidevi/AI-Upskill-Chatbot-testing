## Chatbot UI Automation (Playwright + Pytest)

End-to-end UI automation to validate chatbot responses in the browser: semantic similarity, intent identification, and prompt-injection robustness. Produces CI-ready reports, logs, and evidence.

### Quickstart

1. Create env
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill values
```

2. Install browsers
```bash
python -m playwright install --with-deps
```

3. Run tests
```bash
pytest -q
```

Artifacts appear under `artifacts/` (JUnit XML, Allure, logs, screenshots, videos).

### Configuration
- Env vars in `.env` control URL, selectors, thresholds, and OpenAI models/keys
- Defaults:
  - `CHAT_MODEL=gpt-4`
  - `EMBEDDING_MODEL=text-embedding-3-small`

### Structure
- `src/config.py`: env + thresholds
- `src/extraction.py`: DOM parsing, normalization
- `src/validators/semantic.py`: embeddings + similarity
- `src/validators/intent.py`: LLM Yes/No intent check
- `tests/`: Playwright tests and fixtures (`data/*.yaml`)

### CI
- JUnit at `artifacts/junit/results.xml`
- Allure at `artifacts/allure/`
- Screenshots/videos saved per test on failure









