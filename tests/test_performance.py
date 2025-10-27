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
    
    # Reset chat
    reset_btn = page.locator("[data-testid='mimir-chat-reset-icon']")
    if reset_btn.count() > 0 and reset_btn.is_visible():
        reset_btn.click()
        page.wait_for_timeout(2000)
    
    # Count messages before
    messages_before = page.locator(".mimir-chat-message").count()
    
    # Send prompt and measure time
    start_time = time.time()
    send_prompt(page, prompt)
    
    # Wait for response
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


