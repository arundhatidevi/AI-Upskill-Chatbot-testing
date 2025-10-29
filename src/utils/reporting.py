import json
import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class TestReporter:
    """Utility for structured test reporting and evidence collection."""

    def __init__(self, artifacts_dir: Path):
        self.artifacts_dir = artifacts_dir
        self.results_file = artifacts_dir / "logs" / "test_results.jsonl"
        self.results_file.parent.mkdir(parents=True, exist_ok=True)

    def log_test_result(
        self,
        test_id: str,
        test_type: str,
        passed: bool,
        prompt: str,
        response: str,
        details: Dict[str, Any],
    ) -> None:
        """Log a single test result in JSONL format for easy parsing."""
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "test_id": test_id,
            "test_type": test_type,
            "passed": passed,
            "prompt": prompt,
            "response": response,
            "details": details,
        }
        with open(self.results_file, "a") as f:
            f.write(json.dumps(record) + "\n")
        logger.info(f"Logged test result: {test_id} - {'PASS' if passed else 'FAIL'}")

    def generate_summary(self) -> Dict[str, Any]:
        """Generate a summary report from all test results."""
        if not self.results_file.exists():
            return {"total": 0, "passed": 0, "failed": 0}

        results = []
        with open(self.results_file, "r") as f:
            for line in f:
                if line.strip():
                    results.append(json.loads(line))

        total = len(results)
        passed = sum(1 for r in results if r["passed"])
        failed = total - passed

        summary = {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": (passed / total * 100) if total > 0 else 0,
            "results": results,
        }

        # Write summary JSON
        summary_file = self.artifacts_dir / "logs" / "summary.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"Generated summary: {passed}/{total} passed ({summary['pass_rate']:.1f}%)")
        return summary










