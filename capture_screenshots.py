#!/usr/bin/env python3
"""Capture screenshots of ContentForge AI using Playwright"""

import asyncio
import os
from playwright.async_api import async_playwright

SCREENSHOTS_DIR = "/home/claw/.openclaw/workspace/projects/contentforge-ai/docs/screenshots"
BASE_URL = "http://localhost:3000"

urls = {
    "login": f"{BASE_URL}/login",
    "dashboard": BASE_URL,
    "content_new": f"{BASE_URL}/content/new",
    "settings": f"{BASE_URL}/settings",
}

async def capture_screenshots():
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        
        for name, url in urls.items():
            print(f"Capturing {name}...")
            page = await context.new_page()
            await page.goto(url, wait_until="networkidle")
            await asyncio.sleep(2)  # Wait for content to settle
            
            screenshot_path = os.path.join(SCREENSHOTS_DIR, f"{name}.png")
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"Saved: {screenshot_path}")
            await page.close()
        
        await browser.close()
        print("All screenshots captured!")

if __name__ == "__main__":
    asyncio.run(capture_screenshots())
