"""
Helper script to extract cookies from browser for Keepa
Run this once to get past Cloudflare protection
"""
import json
import asyncio
from playwright.async_api import async_playwright


async def extract_cookies():
    """
    Launch browser, let user solve Cloudflare challenge, then save cookies
    """
    print("🍪 Cookie Extraction Tool for Keepa.com")
    print("=" * 50)

    async with async_playwright() as p:
        # Launch browser in non-headless mode
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )

        page = await context.new_page()

        print("\n📝 Instructions:")
        print("1. A browser window will open")
        print("2. Navigate to Keepa and solve any Cloudflare challenge")
        print("3. Once you see the Keepa deals page, return here")
        print("4. Press ENTER to save the cookies\n")

        # Navigate to Keepa
        await page.goto("https://keepa.com/#!deals/4")

        # Wait for user to solve challenge
        input("⏸️  Press ENTER when you've solved the Cloudflare challenge...")

        # Extract all cookies
        cookies = await context.cookies()

        # Save to file
        with open("cookies.json", "w", encoding="utf-8") as f:
            json.dump(cookies, f, indent=2)

        print(f"\n✅ Saved {len(cookies)} cookies to cookies.json")
        print("\n📋 Cookie domains found:")
        for cookie in cookies:
            print(f"  - {cookie['domain']}: {cookie['name']}")

        print("\n✨ You can now set USE_COOKIES=true in your .env file")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(extract_cookies())
