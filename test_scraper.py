"""
Test script to verify the scraper works correctly
Run this to test scraping without starting the full bot
"""
import asyncio
import logging
import sys
from dotenv import load_dotenv
import os

from scraper import KeepaScraperEngine


# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


async def test_scraper():
    """Test the Keepa scraper"""
    load_dotenv()

    print("🧪 Testing Keepa Scraper")
    print("=" * 50)

    # Configuration
    keepa_url = os.getenv('KEEPA_URL', 'https://keepa.com/#!deals/4')
    headless = os.getenv('HEADLESS_MODE', 'false').lower() == 'true'  # Non-headless for testing
    use_cookies = os.getenv('USE_COOKIES', 'false').lower() == 'true'
    cookies_file = os.getenv('COOKIES_FILE', 'cookies.json')
    min_discount = float(os.getenv('MIN_DISCOUNT_PERCENT', 40))

    print(f"\n📋 Configuration:")
    print(f"  URL: {keepa_url}")
    print(f"  Headless: {headless}")
    print(f"  Use Cookies: {use_cookies}")
    print(f"  Min Discount: {min_discount}%\n")

    # Create scraper
    scraper = KeepaScraperEngine(
        keepa_url=keepa_url,
        headless=headless,
        use_cookies=use_cookies,
        cookies_file=cookies_file
    )

    try:
        print("🚀 Initializing browser...")
        await scraper.initialize()
        print("✅ Browser initialized\n")

        print("🔍 Navigating to Keepa deals page...")
        await scraper.navigate_to_deals()
        print("✅ Page loaded\n")

        print("📊 Extracting deals...")
        deals = await scraper.extract_deals(min_discount=min_discount)
        print(f"✅ Found {len(deals)} deals\n")

        # Display results
        if deals:
            print("🎯 Deals Found:")
            print("-" * 50)
            for i, deal in enumerate(deals, 1):
                print(f"\n{i}. {deal.title[:60]}...")
                print(f"   ASIN: {deal.asin}")
                print(f"   Price: €{deal.current_price:.2f} (was €{deal.average_price:.2f})")
                print(f"   Discount: {deal.discount_percent:.1f}%")
                print(f"   URL: {deal.product_url}")
                print(f"   Graph: {deal.keepa_graph_url}")
        else:
            print("⚠️  No deals found matching criteria")
            print("\nPossible reasons:")
            print("  - Minimum discount threshold too high")
            print("  - Page structure changed (check scraper selectors)")
            print("  - Cloudflare blocking (try using cookies)")
            print("\n💡 Try running with HEADLESS_MODE=false to see the browser")

        # Wait a bit to see the page
        if not headless:
            print("\n⏸️  Browser window is open. Press ENTER to close...")
            input()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.exception("Test failed")

    finally:
        print("\n🧹 Cleaning up...")
        await scraper.cleanup()
        print("✅ Cleanup complete\n")


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  KEEPA SCRAPER TEST")
    print("=" * 50 + "\n")

    try:
        asyncio.run(test_scraper())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        sys.exit(1)

    print("\n" + "=" * 50)
    print("  TEST COMPLETE")
    print("=" * 50 + "\n")
