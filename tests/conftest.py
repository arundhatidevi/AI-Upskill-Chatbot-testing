import pytest
from pathlib import Path
from playwright.sync_api import Page, Browser
from src.config import settings, _ARTIFACTS_DIR


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context with video recording if enabled."""
    if settings.record_video:
        return {
            **browser_context_args,
            "record_video_dir": str(_ARTIFACTS_DIR / "videos"),
            "record_video_size": {"width": 1280, "height": 720},
        }
    return browser_context_args


@pytest.fixture
def page(page: Page, request):
    """Enhance page fixture with screenshot on failure."""
    yield page
    if request.node.rep_call.failed and settings.screenshot_on_failure:
        screenshot_path = _ARTIFACTS_DIR / "screenshots" / f"{request.node.name}.png"
        page.screenshot(path=str(screenshot_path))


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture test result for screenshot fixture."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)










