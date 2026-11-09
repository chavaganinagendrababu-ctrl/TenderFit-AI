"""
TenderFit - Browser Manager
Manages the Playwright browser lifecycle, contexts, pages, and anti-crash timeouts.
"""

import logging
from typing import Optional
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, Playwright
from config.settings import settings

logger = logging.getLogger("tenderfit.automation.browser")


class BrowserManager:
    """
    Encapsulates Playwright lifecycle to ensure reliable browser startup,
    proper context isolation, realistic viewport settings, and clean teardown.
    """

    def __init__(self, headless: Optional[bool] = None, timeout: Optional[int] = None):
        self.headless = headless if headless is not None else settings.PLAYWRIGHT_HEADLESS
        self.timeout = timeout or settings.PLAYWRIGHT_TIMEOUT
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None

    def start(self) -> Browser:
        """Launches a Chromium browser instance. Auto-installs Chromium if missing in cloud containers."""
        if not self._browser:
            logger.info(f"Launching Playwright Chromium (headless={self.headless})...")
            self._playwright = sync_playwright().start()
            try:
                self._browser = self._playwright.chromium.launch(
                    headless=self.headless,
                    args=[
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-blink-features=AutomationControlled",
                    ],
                )
            except Exception as e:
                err_text = str(e).lower()
                if "playwright install" in err_text or "executable doesn't exist" in err_text:
                    logger.info("Chromium binary missing. Attempting self-healing 'playwright install chromium'...")
                    import sys, subprocess
                    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
                    self._browser = self._playwright.chromium.launch(
                        headless=self.headless,
                        args=[
                            "--no-sandbox",
                            "--disable-dev-shm-usage",
                            "--disable-blink-features=AutomationControlled",
                        ],
                    )
                else:
                    raise
        return self._browser

    def new_context(self) -> BrowserContext:
        """Creates a browser context configured with realistic browser headers."""
        browser = self.start()
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            accept_downloads=True,
        )
        context.set_default_timeout(self.timeout)
        return context

    def new_page(self) -> tuple[BrowserContext, Page]:
        """Convenience method returning both context and an active page."""
        context = self.new_context()
        page = context.new_page()
        return context, page

    def close(self):
        """Cleanly releases all browser and Playwright process resources."""
        if self._browser:
            try:
                self._browser.close()
            except Exception as e:
                logger.debug(f"Browser close error: {e}")
            self._browser = None

        if self._playwright:
            try:
                self._playwright.stop()
            except Exception as e:
                logger.debug(f"Playwright stop error: {e}")
            self._playwright = None
        logger.info("Playwright browser closed cleanly.")

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

