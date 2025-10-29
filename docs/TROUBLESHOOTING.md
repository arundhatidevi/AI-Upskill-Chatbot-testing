# Troubleshooting Guide

Common issues and their solutions when running chatbot UI automation tests.

## Table of Contents

- [Setup Issues](#setup-issues)
- [Selector Issues](#selector-issues)
- [API Issues](#api-issues)
- [Test Failures](#test-failures)
- [Performance Issues](#performance-issues)
- [CI/CD Issues](#cicd-issues)

---

## Setup Issues

### Python virtual environment not activating

**Symptoms:**
```bash
source .venv/bin/activate
bash: .venv/bin/activate: No such file or directory
```

**Solution:**
```bash
# Create virtual environment first
python3 -m venv .venv

# Then activate
source .venv/bin/activate
```

### Playwright installation fails

**Symptoms:**
```
Error: Browser installation failed
```

**Solution:**
```bash
# Install with system dependencies
python -m playwright install --with-deps chromium

# If still failing, install system deps manually (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2
```

### ImportError: No module named 'src'

**Symptoms:**
```python
ModuleNotFoundError: No module named 'src'
```

**Solution:**
```bash
# Ensure you're in the project root
cd /home/sreya/Documents/milestone_UI_AUTOMATION

# Check PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or add to .env
echo "PYTHONPATH=$(pwd)" >> .env
```

---

## Selector Issues

### Element not found / Timeout error

**Symptoms:**
```
playwright._impl._api_types.TimeoutError: Locator.click: Timeout 30000ms exceeded.
```

**Diagnosis:**
```bash
# Run inspector to find correct selectors
make inspect

# Or use Playwright debug mode
PWDEBUG=1 pytest tests/test_semantic_similarity.py::test_semantic_similarity[greeting_hello]
```

**Common Causes:**

1. **Selector is wrong**
   - Use inspector to find correct selector
   - Update `.env` with correct selector

2. **Element is inside an iframe**
   ```python
   # In src/extraction.py, modify to use frame_locator
   frame = page.frame_locator("iframe#chat-iframe")
   input_area = frame.locator(settings.selectors.input_area)
   ```

3. **Element loads slowly**
   ```python
   # Increase timeout in src/extraction.py
   input_area.wait_for(state="visible", timeout=60000)
   ```

4. **Element is hidden until interaction**
   ```python
   # Scroll into view first
   input_area.scroll_into_view_if_needed()
   input_area.click()
   ```

### Multiple elements matched

**Symptoms:**
Test interacts with wrong element (e.g., clicks first of many buttons).

**Solution:**
```bash
# Make selector more specific
# Bad:
SELECTOR_SEND_BUTTON=button

# Good:
SELECTOR_SEND_BUTTON=button.send-message
# or
SELECTOR_SEND_BUTTON=[data-testid="chat-send"]
# or
SELECTOR_SEND_BUTTON=.chat-input-container button[type="submit"]
```

### Messages not extracted correctly

**Symptoms:**
```
[test_id] Actual: 
AssertionError: Similarity check failed...
Actual: [empty string]
```

**Diagnosis:**

1. **Check message structure**
   ```bash
   PWDEBUG=1 pytest tests/test_semantic_similarity.py -k greeting_hello
   # In Playwright Inspector, run:
   page.locator(".chat-message").count()
   page.locator(".chat-message").first.inner_text()
   ```

2. **Verify role attribute**
   ```python
   # Test in Playwright console
   page.locator(".message").first.get_attribute("data-role")
   ```

**Solution:**

Update selectors in `.env`:
```bash
# Example fixes:
SELECTOR_MESSAGE_ROW=.message-item  # Not .chat-message
SELECTOR_MESSAGE_ROLE_ATTR=data-sender  # Not data-role
SELECTOR_MESSAGE_TEXT=.text-content  # Not .message-text
```

---

## API Issues

### OpenAI authentication error

**Symptoms:**
```
openai.AuthenticationError: Incorrect API key provided
```

**Solution:**
```bash
# Check your API key
cat .env | grep OPENAI_API_KEY

# Ensure no extra spaces or quotes
# Bad: OPENAI_API_KEY="sk-..."
# Good: OPENAI_API_KEY=sk-...

# Test API key manually
python -c "
from openai import OpenAI
client = OpenAI(api_key='sk-your-key')
print(client.models.list())
"
```

### Rate limit exceeded

**Symptoms:**
```
openai.RateLimitError: Rate limit reached for requests
```

**Solution:**

1. **Add delays between tests:**
   ```python
   # In tests/conftest.py
   import time
   
   @pytest.fixture(autouse=True)
   def rate_limit_pause():
       yield
       time.sleep(2)  # 2 second delay between tests
   ```

2. **Run tests sequentially:**
   ```bash
   pytest -n 1  # No parallelization
   ```

3. **Use cheaper/faster models:**
   ```bash
   # In .env
   CHAT_MODEL=gpt-3.5-turbo  # Instead of gpt-4
   ```

4. **Upgrade OpenAI plan:**
   Visit https://platform.openai.com/account/billing

### Embedding dimension mismatch

**Symptoms:**
```
ValueError: operands could not be broadcast together
```

**Solution:**
Ensure you're using consistent embedding models. Don't mix embeddings from different models.

```bash
# In .env, stick to one model
EMBEDDING_MODEL=text-embedding-3-small
```

---

## Test Failures

### Semantic similarity too low

**Symptoms:**
```
AssertionError: Semantic similarity check failed for 'business_hours'.
Similarity: 0.6234 < 0.80
```

**Diagnosis:**

1. **Check if answer is actually wrong:**
   - Look at expected vs actual
   - Is the bot giving a different (but valid) answer?

2. **Check if threshold is too strict:**
   - 0.95+: Very strict
   - 0.80-0.94: Reasonable
   - 0.70-0.79: Lenient

**Solution:**

Option 1: Adjust threshold globally:
```bash
# In .env
SEMANTIC_THRESHOLD=0.75  # Lower threshold
```

Option 2: Adjust per-test:
```yaml
# In tests/data/semantic_tests.yaml
- id: business_hours
  prompt: "What are your hours?"
  expected_answer: "9 AM to 5 PM Monday-Friday"
  threshold: 0.70  # More lenient for this test
```

Option 3: Update expected answer:
```yaml
# If bot's answer is correct but different
expected_answer: "We're open 24/7 for your convenience"
```

### Intent validation fails

**Symptoms:**
```
AssertionError: Intent validation failed for 'help_intent'.
Decision: False, Confidence: 0.32 < 0.50
```

**Solution:**

1. **Check intent description clarity:**
   ```yaml
   # Vague:
   intent_description: "help"
   
   # Better:
   intent_description: "requesting assistance or asking for help"
   ```

2. **Check actual response:**
   - Maybe bot didn't understand the prompt
   - Update prompt or expected intent

3. **Adjust confidence threshold:**
   ```bash
   # In .env
   INTENT_CONFIDENCE_THRESHOLD=0.4  # Lower threshold
   ```

### Prompt injection tests failing incorrectly

**Symptoms:**
Bot isn't refusing when it should, or refusing when it shouldn't.

**Solution:**

1. **Review refusal logic:**
   ```python
   # In tests/test_prompt_injection.py
   # Tune refusal_keywords list
   refusal_keywords = [
       "cannot", "can't", "unable", "not allowed",
       # Add chatbot-specific refusal phrases
       "sorry, I can't", "that's outside my capabilities"
   ]
   ```

2. **Check bot's actual behavior:**
   - Screenshot in `artifacts/screenshots/`
   - Review response text in logs

3. **Update test expectations:**
   ```yaml
   # If bot has weak guardrails for a specific injection
   - id: weak_injection
     prompt: "..."
     expected_behavior: "comply"  # Change from "refuse" if bot doesn't refuse
     description: "Known limitation - bot doesn't refuse this"
   ```

---

## Performance Issues

### Tests run too slowly

**Causes:**
- Many API calls
- Slow network
- Headed mode (browser GUI)

**Solutions:**

1. **Run in headless mode:**
   ```bash
   pytest --headed=false
   ```

2. **Parallelize (carefully):**
   ```bash
   pip install pytest-xdist
   pytest -n 2  # 2 parallel workers (watch rate limits!)
   ```

3. **Cache embeddings:**
   ```python
   # In src/utils/embedding.py
   import functools
   
   @functools.lru_cache(maxsize=1000)
   def embed_texts_cached(text_tuple):
       return embed_texts(list(text_tuple))
   ```

4. **Skip slow tests in dev:**
   ```bash
   pytest -m "not slow"
   ```

### Browser hangs or crashes

**Solution:**

1. **Increase timeouts:**
   ```python
   # In pytest.ini
   timeout = 300  # 5 minutes per test
   ```

2. **Close browser properly:**
   ```python
   # Already handled in conftest.py, but verify
   ```

3. **Check system resources:**
   ```bash
   # Ensure enough RAM/CPU
   free -h
   top
   ```

---

## CI/CD Issues

### Tests pass locally but fail in CI

**Common Causes:**

1. **Missing environment variables:**
   ```yaml
   # In .github/workflows/ci.yml
   env:
     OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
     BASE_URL: ${{ secrets.BASE_URL }}
   ```

2. **Different selectors in production:**
   - Use environment-specific `.env` files
   - Or detect environment and load selectors accordingly

3. **Headless vs headed mode:**
   ```bash
   # CI should run headless
   pytest --headed=false
   ```

4. **Timing issues (network latency):**
   ```python
   # Increase waits in CI
   if os.getenv("CI"):
       page.wait_for_timeout(5000)  # Extra wait in CI
   ```

### Artifacts not uploading

**Check:**

1. **Paths are correct:**
   ```yaml
   # In workflow
   path: |
     artifacts/screenshots/
     artifacts/videos/
     artifacts/logs/
   ```

2. **Artifacts directory exists:**
   ```bash
   # In workflow, before tests
   mkdir -p artifacts/{screenshots,videos,logs}
   ```

3. **Artifact retention:**
   ```yaml
   retention-days: 30  # Artifacts kept for 30 days
   ```

### Secrets not working

**Solution:**

1. **Add secrets in repo settings:**
   - GitHub: Settings → Secrets and variables → Actions → New repository secret

2. **Reference correctly:**
   ```yaml
   env:
     OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
   ```

3. **Don't print secrets in logs:**
   ```python
   # Bad
   print(f"API Key: {os.getenv('OPENAI_API_KEY')}")
   
   # Good
   print("API Key: [REDACTED]")
   ```

---

## Still Stuck?

### Enable Debug Mode

```bash
# Full debug output
PWDEBUG=1 pytest tests/test_semantic_similarity.py -v --log-cli-level=DEBUG

# Or just Playwright inspector
PWDEBUG=1 pytest tests/test_semantic_similarity.py -k greeting_hello
```

### Check Logs

```bash
# Test logs
cat artifacts/logs/test.log

# Structured results
cat artifacts/logs/test_results.jsonl | jq '.'

# Error logs only
grep ERROR artifacts/logs/test.log
```

### Visual Evidence

```bash
# Screenshots (taken on failure)
ls artifacts/screenshots/

# Videos (if recording enabled)
ls artifacts/videos/
```

### Minimal Reproduction

Create a minimal test to isolate the issue:

```python
# tests/test_minimal.py
from playwright.sync_api import Page

def test_minimal(page: Page):
    page.goto("https://sunrv-chatbot.dev02cms.milestoneinternet.info/?_enablechatbot=true")
    page.wait_for_load_state("networkidle")
    # Try to interact with one element
    page.locator("YOUR_SELECTOR").click()
    assert True
```

Run it:
```bash
PWDEBUG=1 pytest tests/test_minimal.py -v
```

### Report an Issue

If you've tried everything:

1. Collect information:
   - Error message
   - Full logs
   - Screenshot
   - Steps to reproduce

2. Check if it's a known issue:
   - Playwright docs: https://playwright.dev/python/
   - OpenAI docs: https://platform.openai.com/docs/

3. Create a minimal reproducible example

---

**Pro Tip:** Most issues are selector-related. When in doubt, run `make inspect` and visually verify selectors match your chatbot's DOM structure.


