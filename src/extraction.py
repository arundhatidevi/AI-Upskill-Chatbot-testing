from typing import List, Tuple
from playwright.sync_api import Page, expect
from .config import settings
from .utils.normalization import normalize_text


def open_chat_if_needed(page: Page) -> None:
    open_button = page.locator(settings.selectors.open_widget)
    if open_button.count() > 0:
        if open_button.is_visible():
            open_button.click()
            page.wait_for_timeout(2000)  # Wait for chat to open


def send_prompt(page: Page, prompt: str) -> None:
    input_area = page.locator(settings.selectors.input_area)
    expect(input_area).to_be_visible(timeout=10000)
    input_area.fill(prompt)
    page.wait_for_timeout(500)  # Brief wait after typing
    send_button = page.locator(settings.selectors.send_button)
    if send_button.count() > 0 and send_button.is_visible():
        send_button.click()
    else:
        input_area.press("Enter")


def read_messages(page: Page, last_n: int = 1) -> List[Tuple[str, str]]:
    # Wait for at least one message to appear
    page.wait_for_selector(settings.selectors.message_row, timeout=10000)
    
    # Get all message rows directly (no container needed)
    rows = page.locator(settings.selectors.message_row)
    count = rows.count()
    messages: List[Tuple[str, str]] = []
    for i in range(count):
        row = rows.nth(i)
        role = row.get_attribute(settings.selectors.message_role_attr) or ""
        text = row.locator(settings.selectors.message_text).inner_text(timeout=10000)
        messages.append((role, normalize_text(text)))
    if last_n <= 0:
        return []
    return messages[-last_n:]


def read_last_bot_message(page: Page) -> str:
    messages = read_messages(page, last_n=10)
    last_bot = ""
    for role, text in messages:
        role_lower = role.lower()
        # Check for bot/assistant/ai keywords in role attribute or class
        if any(keyword in role_lower for keyword in ["bot", "assistant", "ai", "mimir-bot"]):
            last_bot = text
    if not last_bot and messages:
        # Fallback to very last message
        last_bot = messages[-1][1]
    return last_bot
