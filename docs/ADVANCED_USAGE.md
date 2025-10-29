# Advanced Usage Guide

This guide covers advanced features and customization options for the chatbot UI automation framework.

## Custom Test Fixtures

### Adding New Test Cases

Test cases are defined in YAML files under `tests/data/`. You can add new cases or create new files.

#### Semantic Similarity Tests

Add to `tests/data/semantic_tests.yaml`:

```yaml
semantic_tests:
  - id: your_test_id
    prompt: "Your question"
    expected_answer: "Expected bot response"
    threshold: 0.80  # Similarity threshold (0-1)
```

#### Intent Validation Tests

Add to `tests/data/intent_tests.yaml`:

```yaml
intent_tests:
  - id: your_test_id
    prompt: "User message"
    intent_description: "what the bot should express"
    min_confidence: 0.6  # Confidence threshold (0-1)
```

#### Prompt Injection Tests

Add to `tests/data/injection_tests.yaml`:

```yaml
injection_tests:
  - id: your_test_id
    prompt: "Adversarial prompt"
    expected_behavior: "refuse"  # or "comply"
    description: "What this test checks"
```

## Threshold Tuning

Adjust thresholds based on your chatbot's behavior:

### Semantic Similarity Threshold

- **0.95+**: Very strict - requires near-exact match
- **0.85-0.94**: Strict - similar meaning required
- **0.75-0.84**: Moderate - allows some variation
- **0.60-0.74**: Loose - accepts broader similarity
- **<0.60**: Very loose - not recommended

Set globally in `.env`:
```bash
SEMANTIC_THRESHOLD=0.82
```

Or per-test in YAML:
```yaml
threshold: 0.75
```

### Intent Confidence Threshold

Controls LLM's confidence in intent detection:

- **0.8+**: High confidence required
- **0.5-0.7**: Moderate confidence
- **<0.5**: Low confidence (risky)

Set in `.env`:
```bash
INTENT_CONFIDENCE_THRESHOLD=0.5
```

## MongoDB Integration (Optional)

To store ground truth and test results in MongoDB:

### 1. Install pymongo

Add to `requirements.txt`:
```
pymongo==4.6.0
```

### 2. Add MongoDB config

In `.env`:
```bash
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=chatbot_testing
```

### 3. Create storage module

Create `src/storage/mongodb.py`:

```python
from pymongo import MongoClient
from src.config import settings

def get_mongo_client():
    uri = settings.mongodb_uri
    return MongoClient(uri)

def store_test_result(collection_name: str, result: dict):
    client = get_mongo_client()
    db = client[settings.mongodb_database]
    collection = db[collection_name]
    collection.insert_one(result)
```

### 4. Use in tests

```python
from src.storage.mongodb import store_test_result

# After validation
store_test_result("semantic_results", {
    "test_id": test_id,
    "passed": result.passed,
    "similarity": result.similarity,
    # ... more fields
})
```

## Running Specific Test Types

### Run only semantic tests
```bash
pytest tests/test_semantic_similarity.py -v
```

### Run only intent tests
```bash
pytest tests/test_intent_validation.py -v
```

### Run only injection tests
```bash
pytest tests/test_prompt_injection.py -v
```

### Run specific test case
```bash
pytest tests/test_semantic_similarity.py::test_semantic_similarity[greeting_hello] -v
```

## Parallel Execution

Run tests in parallel with pytest-xdist:

```bash
pip install pytest-xdist
pytest -n auto  # Use all available CPUs
pytest -n 4     # Use 4 workers
```

**Note**: Be mindful of rate limits when running parallel tests with OpenAI API.

## Custom Validators

Create your own validators for specific needs:

### Example: Toxicity Validator

Create `src/validators/toxicity.py`:

```python
from openai import OpenAI
from src.config import settings

def check_toxicity(text: str) -> dict:
    client = OpenAI(api_key=settings.openai.api_key)
    response = client.moderations.create(input=text)
    result = response.results[0]
    return {
        "flagged": result.flagged,
        "categories": result.categories.model_dump(),
        "scores": result.category_scores.model_dump(),
    }
```

Use in tests:

```python
from src.validators.toxicity import check_toxicity

toxicity = check_toxicity(bot_response)
assert not toxicity["flagged"], f"Response flagged for toxicity: {toxicity}"
```

## Video Recording

Videos are recorded by default. To control:

### Disable video recording
```bash
RECORD_VIDEO=false pytest
```

### Access videos
Videos are saved to `artifacts/videos/` and attached to Playwright traces.

## Headless vs Headed Mode

### Run in headless mode (CI-friendly)
```bash
pytest --headed=false
```

### Run in headed mode (debugging)
```bash
pytest --headed
```

### Debug with Playwright Inspector
```bash
PWDEBUG=1 pytest tests/test_semantic_similarity.py::test_semantic_similarity[greeting_hello]
```

## Environment-Specific Configuration

Create multiple `.env` files for different environments:

- `.env.dev`
- `.env.uat`
- `.env.prod`

Load specific env:

```bash
cp .env.dev .env
pytest
```

Or use `python-dotenv` programmatically:

```python
from dotenv import load_dotenv
load_dotenv(".env.uat")
```

## Continuous Testing

Schedule regular test runs in CI:

### GitHub Actions (see .github/workflows/ci.yml)
- Runs on push, PR, and daily schedule
- Uploads artifacts on failure
- Publishes JUnit results

### Jenkins / GitLab CI
Adapt the GitHub Actions workflow to your CI platform.

### Monitoring & Alerts

Integrate with monitoring tools:

```bash
# Example: Send results to Slack webhook
curl -X POST $SLACK_WEBHOOK_URL -H 'Content-Type: application/json' \
  -d '{"text": "Chatbot tests: 15/20 passed"}'
```

## Performance Optimization

### Reduce API Calls

- **Cache embeddings**: Store embeddings for fixed expected answers
- **Batch validation**: Validate multiple responses in one run
- **Use cheaper models**: For intent checks, consider `gpt-3.5-turbo`

### Faster Execution

- Run critical tests first with `pytest -m critical`
- Skip slow tests in rapid feedback loops: `pytest -m "not slow"`
- Use parallel execution (see above)

## Debugging Failed Tests

### View screenshots
```bash
ls artifacts/screenshots/
```

### View logs
```bash
cat artifacts/logs/test.log
```

### View test results JSON
```bash
cat artifacts/logs/test_results.jsonl | jq .
```

### Re-run failed tests
```bash
pytest --lf  # Last failed
pytest --ff  # Failed first
```

## Best Practices

1. **Version control**: Commit `.env.example`, never commit `.env`
2. **Secrets management**: Use CI secrets for `OPENAI_API_KEY`
3. **Regular updates**: Keep test fixtures up-to-date with chatbot changes
4. **Threshold tuning**: Review and adjust thresholds quarterly
5. **Evidence review**: Manually review failed test screenshots/videos
6. **Rate limiting**: Add delays between tests if hitting API limits
7. **Flaky tests**: Investigate and stabilize any intermittently failing tests

## Extending the Framework

### Add new test types

1. Create new YAML fixture file in `tests/data/`
2. Create new test module in `tests/`
3. Implement validator in `src/validators/`
4. Update README and documentation

### Integrate with existing frameworks

This framework can complement:
- **API testing**: Run UI tests after API validation
- **Unit tests**: Ensure backend + frontend consistency
- **Performance tests**: Validate responses under load

### Export results

Generate reports in different formats:

```python
# In tests/conftest.py or custom script
import json

def pytest_sessionfinish(session, exitstatus):
    # Custom reporting logic
    results = collect_results()
    with open("report.json", "w") as f:
        json.dump(results, f)
```

Happy testing! 🚀










