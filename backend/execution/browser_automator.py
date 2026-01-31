from playwright.async_api import async_playwright
import os
from pathlib import Path
from datetime import datetime


class BrowserAutomator:
    """Automatiza o navegador para screenshots e extração de dados"""

    def __init__(self, artifacts_dir: str):
        self.artifacts_dir = Path(artifacts_dir)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    async def screenshot(self, url: str, filename: str = None) -> str:
        """Tira um print de uma URL e salva como artifact"""
        if not filename:
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        filepath = self.artifacts_dir / filename

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url)
            await page.screenshot(path=str(filepath))
            await browser.close()
        
        return str(filepath.absolute())

    async def scrape_text(self, url: str) -> str:
        """Extrai o texto principal de uma página para contexto da IA"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url)
            # Tira scripts, styles e tags irrelevantes
            text = await page.inner_text("body")
            await browser.close()
        return text
