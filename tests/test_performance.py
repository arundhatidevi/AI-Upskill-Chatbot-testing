import pytest
import time
import logging
from playwright.sync_api import Page
from src.config import settings
from src.extraction import open_chat_if_needed, send_prompt, read_last_bot_message

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
    
    # Wait for bot's response to appear in UI (measures response time + render time)
    # For accurate response time measurement, we wait for the message to appear
    try:
        page.wait_for_function(
            f"document.querySelectorAll('.mimir-chat-message').length > {messages_before}",
            timeout=10000
        )
        end_time = time.time()
        response_time = end_time - start_time
        
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
        
    except Exception as e:
        end_time = time.time()
        response_time = end_time - start_time
        logger.error(f"❌ FAILED - Timeout or error after {response_time:.2f}s: {e}")
        raise


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
      
       start = time.time()
       send_prompt(page, prompt)
      
       try:
           page.wait_for_function(
               f"document.querySelectorAll('.mimir-chat-message').length > {messages_before}",
               timeout=10000
           )
           elapsed = time.time() - start
           response_times.append(elapsed)
           logger.info(f"  Request {i+1} completed in {elapsed:.2f}s")
       except:
           logger.warning(f"  Request {i+1} timed out")
  
   total_time = time.time() - start_overall
  
   logger.info(f"\n📊 Load Test Results:")
   logger.info(f"  Total requests: {len(prompts)}")
   logger.info(f"  Successful: {len(response_times)}")
   logger.info(f"  Total time: {total_time:.2f}s")
   throughput = len(prompts) / total_time
   logger.info(f"  Throughput: {throughput:.2f} requests/sec")
   
   # Calculate average and max response times
   if response_times:
       avg_time = sum(response_times) / len(response_times)
       max_time = max(response_times)
       logger.info(f"  Avg per request: {avg_time:.2f}s")
       logger.info(f"  Max response time: {max_time:.2f}s")
       
       # Parameter 1: Each request must complete within 5 seconds (SLA)
       assert max_time < 5.0, (
           f"❌ SLA Violation - Max response time {max_time:.2f}s exceeds 5s threshold"
       )
       logger.info(f"  ✅ SLA Check: Max response time {max_time:.2f}s < 5.0s")
   else:
       raise AssertionError("❌ FAILED - No successful requests")
  
   # Parameter 2: Total test time must complete within 30 seconds (throughput)
   assert total_time < 30.0, (
       f"❌ Throughput Violation - Total time {total_time:.2f}s exceeds 30s threshold"
   )
   logger.info(f"  ✅ Throughput Check: Total time {total_time:.2f}s < 30.0s")
  
   assert len(response_times) == len(prompts), "Some requests failed"
   logger.info(f"✅ PASSED - All requests completed within SLA and throughput limits")
