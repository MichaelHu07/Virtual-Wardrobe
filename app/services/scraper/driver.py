import logging
import asyncio
from playwright.async_api import async_playwright, Page, BrowserContext
from fake_useragent import UserAgent
from typing import Optional

logger = logging.getLogger(__name__)

class PlaywrightDriver:
    def __init__(self):
        self.ua = UserAgent()

    async def get_page_content(self, url: str) -> Optional[str]:
        async with async_playwright() as p:
            # Stealth config
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox"
                ]
            )
            
            context = await browser.new_context(
                user_agent=self.ua.random,
                viewport={"width": 1920, "height": 1080},
                java_script_enabled=True
            )
            
            # Additional evasion scripts
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            page = await context.new_page()
            
            try:
                logger.info(f"Navigating to {url}")
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                
                # Scroll to trigger lazy loading
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2) # Wait for network requests
                
                content = await page.content()
                return content
                
            except Exception as e:
                logger.error(f"Failed to scrape {url}: {e}")
                return None
            finally:
                await browser.close()

