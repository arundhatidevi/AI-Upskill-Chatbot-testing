"""Utility for handling option button interactions."""
from playwright.sync_api import Page
from ..config import settings


def click_option_button(page: Page, button_selector: str, button_text: str = "", needs_send: bool = True) -> None:
    """
    Click an option button in the chat interface.
    For some buttons (location/resort selection), clicking fills the input and requires hitting send.
    
    Args:
        page: Playwright page object
        button_selector: CSS selector for the button
        button_text: Optional text for logging
        needs_send: If True, clicks send button after clicking option button (default: True)
    """
    # Count messages before clicking
    messages_before = page.locator(".mimir-chat-message").count()
    
    button = page.locator(button_selector)
    button.wait_for(state="visible", timeout=10000)
    
    # Try normal click first, then force if blocked
    try:
        button.click(timeout=5000)
    except:
        # If blocked by modal/overlay, force click
        button.click(force=True)
    
    # If button fills input, we need to hit send
    if needs_send:
        page.wait_for_timeout(500)  # Wait for input to be filled
        
        # Click send button
        send_button = page.locator(settings.selectors.send_button)
        if send_button.count() > 0 and send_button.is_visible():
            try:
                send_button.click(timeout=5000)
            except:
                send_button.click(force=True)
        else:
            # Fallback: press Enter in input field
            input_area = page.locator(settings.selectors.input_area)
            if input_area.is_visible():
                input_area.press("Enter")
    
    # Wait for new message to appear (timeout after 10 seconds)
    page.wait_for_function(
        f"document.querySelectorAll('.mimir-chat-message').length > {messages_before}",
        timeout=10000
    )
    page.wait_for_timeout(1000)  # Additional wait for message to fully render


def get_available_buttons(page: Page, button_class: str = ".mimir-chip-button") -> list[str]:
    """
    Get list of all visible option buttons.
    
    Args:
        page: Playwright page object
        button_class: CSS class for option buttons
        
    Returns:
        List of button text values
    """
    buttons = page.locator(button_class).all()
    return [btn.inner_text() for btn in buttons if btn.is_visible()]


def verify_button_exists(page: Page, button_selector: str) -> bool:
    """
    Check if a button exists and is visible.
    
    Args:
        page: Playwright page object
        button_selector: CSS selector for the button
        
    Returns:
        True if button exists and is visible
    """
    try:
        button = page.locator(button_selector)
        return button.is_visible()
    except:
        return False

