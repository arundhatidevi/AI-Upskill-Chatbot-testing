"""Performance monitoring utilities for chatbot testing."""
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class PerformanceMonitor:
    """Track and report performance metrics."""
    
    def __init__(self, log_file: str = "performance_log.json"):
        self.log_file = Path(log_file)
        self.metrics: List[Dict] = []
    
    def record_response_time(self, test_name: str, prompt: str, response_time: float, 
                            success: bool = True, error: str = None):
        """Record a single response time measurement."""
        metric = {
            "timestamp": datetime.now().isoformat(),
            "test_name": test_name,
            "prompt": prompt,
            "response_time_seconds": round(response_time, 3),
            "success": success,
            "error": error
        }
        self.metrics.append(metric)
    
    def save_metrics(self):
        """Save metrics to JSON file."""
        with open(self.log_file, "a") as f:
            for metric in self.metrics:
                f.write(json.dumps(metric) + "\n")
        self.metrics.clear()
    
    def get_statistics(self, test_name: str = None) -> Dict:
        """Calculate performance statistics from log file."""
        metrics = self._load_metrics()
        
        if test_name:
            metrics = [m for m in metrics if m.get("test_name") == test_name]
        
        if not metrics:
            return {"error": "No metrics found"}
        
        response_times = [m["response_time_seconds"] for m in metrics if m.get("success")]
        success_count = sum(1 for m in metrics if m.get("success"))
        total_count = len(metrics)
        
        return {
            "total_requests": total_count,
            "successful_requests": success_count,
            "failed_requests": total_count - success_count,
            "success_rate": round(success_count / total_count * 100, 2) if total_count > 0 else 0,
            "avg_response_time": round(sum(response_times) / len(response_times), 3) if response_times else 0,
            "min_response_time": round(min(response_times), 3) if response_times else 0,
            "max_response_time": round(max(response_times), 3) if response_times else 0,
            "median_response_time": round(sorted(response_times)[len(response_times)//2], 3) if response_times else 0
        }
    
    def _load_metrics(self) -> List[Dict]:
        """Load metrics from JSON log file."""
        metrics = []
        if self.log_file.exists():
            with open(self.log_file, "r") as f:
                for line in f:
                    try:
                        metrics.append(json.loads(line.strip()))
                    except:
                        pass
        return metrics
    
    def generate_report(self, output_file: str = "performance_report.txt"):
        """Generate a human-readable performance report."""
        stats = self.get_statistics()
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║          CHATBOT PERFORMANCE REPORT                          ║
╚══════════════════════════════════════════════════════════════╝

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

📊 OVERALL STATISTICS
─────────────────────────────────────────────────────────────
Total Requests:       {stats.get('total_requests', 0)}
Successful:           {stats.get('successful_requests', 0)}
Failed:               {stats.get('failed_requests', 0)}
Success Rate:         {stats.get('success_rate', 0)}%

⏱️  RESPONSE TIME METRICS
─────────────────────────────────────────────────────────────
Average:              {stats.get('avg_response_time', 0)}s
Minimum:              {stats.get('min_response_time', 0)}s
Maximum:              {stats.get('max_response_time', 0)}s
Median:               {stats.get('median_response_time', 0)}s

🎯 PERFORMANCE TARGETS
─────────────────────────────────────────────────────────────
Target Response Time: < 5.0s
Current Average:      {stats.get('avg_response_time', 0)}s
Status:               {"✅ MEETING TARGET" if stats.get('avg_response_time', 0) < 5.0 else "❌ BELOW TARGET"}

Target Success Rate:  > 95%
Current Success Rate: {stats.get('success_rate', 0)}%
Status:               {"✅ MEETING TARGET" if stats.get('success_rate', 0) > 95 else "❌ BELOW TARGET"}

═══════════════════════════════════════════════════════════════
"""
        
        with open(output_file, "w") as f:
            f.write(report)
        
        print(report)
        return report


def measure_time(func):
    """Decorator to measure function execution time."""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"⏱️  {func.__name__} took {elapsed:.3f}s")
        return result, elapsed
    return wrapper









