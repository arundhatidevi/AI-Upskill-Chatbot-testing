import pytest
import time
import logging
from playwright.sync_api import Page
from src.config import settings
from src.extraction import open_chat_if_needed, send_prompt, read_last_bot_message
from src.utils.performance import measure_response_time, calculate_metrics

logger = logging.getLogger(__name__)


@pytest.mark.parametrize("prompt", [
    "Hello",
    # "I'm looking for a beach campground",
    # "Tell me about Henderson, NY",
    # "What amenities do you offer?",
    # "I want to book a resort"
])
def test_response_time(page: Page, prompt: str):
    """
    Test chatbot response time for various prompts.
    Performance target: < 5 seconds for response
    """
    logger.info(f"Testing response time for prompt: {prompt}")
    
    # Navigate and open chat
    page.goto(settings.base_url)
    page.wait_for_load_state("networkidle")
    open_chat_if_needed(page)
    
    # Skip reset to avoid modal blocking issues (same approach as other tests)
    logger.info("Using existing conversation state (skipping reset to avoid modal blocking)")
    
    # Wait for welcome message and buttons
    page.wait_for_selector(".mimir-chip-button", timeout=5000)
    page.wait_for_timeout(1000)
    
    # Count messages before
    messages_before = page.locator(".mimir-chat-message").count()
    
    # Send prompt and measure bot response time
    start_time = time.time()
    send_prompt(page, prompt)
    
    # Measure response time using utility function
    response_time = measure_response_time(page, messages_before, timeout=10000)
    
    if response_time is None:
        # Timeout occurred
        end_time = time.time()
        response_time = end_time - start_time
        logger.error(f"❌ FAILED - Timeout after {response_time:.2f}s")
        raise AssertionError(f"Response timeout after {response_time:.2f}s")
    
    # Read response
    response = read_last_bot_message(page)
    
    logger.info(f"Response time: {response_time:.2f}s")
    logger.info(f"Response: {response[:100]}...")
    
    # Performance assertions
    assert response_time < 5.0, (
        f"Response too slow!\n"
        f"Prompt: {prompt}\n"
        f"Response time: {response_time:.2f}s\n"
        f"Expected: < 5.0s"
    )
    
    logger.info(f"✅ PASSED - Response time: {response_time:.2f}s < 5.0s")


def test_sequential_latency_and_throughput(page: Page):
   """
    Measures the end-to-end latency and sequential throughput
    for a single user submitting rapid requests.
    """
   prompts = ["Hello"] * 5  # 5 rapid greetings
  
   page.goto(settings.base_url)
   page.wait_for_load_state("networkidle")
   open_chat_if_needed(page)
  
   response_times = []
   start_overall = time.time()
  
   for i, prompt in enumerate(prompts):
       logger.info(f"Request {i+1}/{len(prompts)}")
      
       messages_before = page.locator(".mimir-chat-message").count()
      
       send_prompt(page, prompt)
      
       # Use utility function to measure response time
       elapsed = measure_response_time(page, messages_before, timeout=10000)
      
       if elapsed is not None:
           response_times.append(elapsed)
           logger.info(f"  Request {i+1} completed in {elapsed:.2f}s")
       else:
           logger.warning(f"  Request {i+1} timed out")
  
   total_time = time.time() - start_overall
  
   # Calculate metrics using utility function
   metrics = calculate_metrics(response_times, total_time, len(prompts))
   metrics.log_summary()
   
   # Parameter 1: Each request must complete within 5 seconds (SLA)
   if metrics.response_times:
       assert metrics.max_response_time < 5.0, (
           f"❌ SLA Violation - Max response time {metrics.max_response_time:.2f}s exceeds 5s threshold"
       )
       logger.info(f"  ✅ SLA Check: Max response time {metrics.max_response_time:.2f}s < 5.0s")
   else:
       raise AssertionError("❌ FAILED - No successful requests")
  
   # Parameter 2: Total test time must complete within 30 seconds (throughput)
   assert total_time < 30.0, (
       f"❌ Throughput Violation - Total time {total_time:.2f}s exceeds 30s threshold"
   )
   logger.info(f"  ✅ Throughput Check: Total time {total_time:.2f}s < 30.0s")
  
   assert len(response_times) == len(prompts), "Some requests failed"
   logger.info(f"✅ PASSED - All requests completed within SLA and throughput limits")
