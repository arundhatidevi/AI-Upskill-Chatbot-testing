"""
Performance measurement utilities for chatbot testing.
Contains reusable functions for measuring response times and calculating performance metrics.
"""
import time
import logging
from dataclasses import dataclass
from typing import List, Optional
from playwright.sync_api import Page

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Container for performance measurement results."""
    response_times: List[float]
    total_time: float
    successful_requests: int
    total_requests: int
    
    @property
    def throughput(self) -> float:
        """Calculate requests per second."""
        if self.total_time == 0:
            return 0.0
        return self.total_requests / self.total_time
    
    @property
    def avg_response_time(self) -> Optional[float]:
        """Calculate average response time."""
        if not self.response_times:
            return None
        return sum(self.response_times) / len(self.response_times)
    
    @property
    def max_response_time(self) -> Optional[float]:
        """Get maximum response time."""
        if not self.response_times:
            return None
        return max(self.response_times)
    
    @property
    def min_response_time(self) -> Optional[float]:
        """Get minimum response time."""
        if not self.response_times:
            return None
        return min(self.response_times)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    def log_summary(self) -> None:
        """Log a formatted summary of performance metrics."""
        logger.info(f"\n📊 Performance Metrics:")
        logger.info(f"  Total requests: {self.total_requests}")
        logger.info(f"  Successful: {self.successful_requests}")
        logger.info(f"  Success rate: {self.success_rate:.1f}%")
        logger.info(f"  Total time: {self.total_time:.2f}s")
        logger.info(f"  Throughput: {self.throughput:.2f} requests/sec")
        
        if self.response_times:
            logger.info(f"  Avg response time: {self.avg_response_time:.2f}s")
            logger.info(f"  Max response time: {self.max_response_time:.2f}s")
            logger.info(f"  Min response time: {self.min_response_time:.2f}s")


def measure_response_time(
    page: Page,
    messages_before: int,
    timeout: int = 10000
) -> Optional[float]:
    """
    Measure the time taken for a new message to appear after sending a prompt.
    
    Args:
        page: Playwright page object
        messages_before: Count of messages before sending the prompt
        timeout: Maximum time to wait for response (milliseconds)
    
    Returns:
        Response time in seconds, or None if timeout/error occurred
    """
    start_time = time.time()
    try:
        page.wait_for_function(
            f"document.querySelectorAll('.mimir-chat-message').length > {messages_before}",
            timeout=timeout
        )
        elapsed = time.time() - start_time
        return elapsed
    except Exception as e:
        elapsed = time.time() - start_time
        logger.warning(f"Response measurement timed out after {elapsed:.2f}s: {e}")
        return None


def calculate_metrics(
    response_times: List[float],
    total_time: float,
    total_requests: int
) -> PerformanceMetrics:
    """
    Calculate performance metrics from response time data.
    
    Args:
        response_times: List of individual response times in seconds
        total_time: Total elapsed time for all requests in seconds
        total_requests: Total number of requests attempted
    
    Returns:
        PerformanceMetrics object with calculated metrics
    """
    return PerformanceMetrics(
        response_times=response_times,
        total_time=total_time,
        successful_requests=len(response_times),
        total_requests=total_requests
    )
