"""
Test script to verify Discord bot and embeds work correctly
Run this to test Discord posting without scraping
"""
import asyncio
import logging
import sys
from dotenv import load_dotenv
import os

from bot import create_bot
from scraper import Deal


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


# Sample test deals
TEST_DEALS = [
    Deal(
        asin="B08L5VR6C3",
        title="PlayStation 5 Console - Edition Standard",
        current_price=399.99,
        average_price=549.99,
        discount_percent=27.27,
        product_url="https://www.amazon.fr/dp/B08L5VR6C3",
        image_url="https://m.media-amazon.com/images/I/51YH7CKLWML._AC_SL1500_.jpg",
        availability="In Stock"
    ),
    Deal(
        asin="B0B1L38KHY",
        title="Apple AirPods Pro (2ème génération) avec Boîtier de Charge MagSafe",
        current_price=199.00,
        average_price=299.00,
        discount_percent=33.44,
        product_url="https://www.amazon.fr/dp/B0B1L38KHY",
        image_url="https://m.media-amazon.com/images/I/61SUj2aKoEL._AC_SL1500_.jpg",
        availability="In Stock"
    ),
    Deal(
        asin="B09G9FPHY6",
        title="Samsung Galaxy S23 Ultra - Smartphone Android 5G",
        current_price=799.00,
        average_price=1399.00,
        discount_percent=42.89,
        product_url="https://www.amazon.fr/dp/B09G9FPHY6",
        image_url="https://m.media-amazon.com/images/I/71gEGh6wf2L._AC_SL1500_.jpg",
        availability="Only 2 left in stock"
    ),
    Deal(
        asin="B0CX23V2ZK",
        title="Dyson V15 Detect Absolute - Aspirateur Balai Sans Fil",
        current_price=449.99,
        average_price=749.99,
        discount_percent=40.00,
        product_url="https://www.amazon.fr/dp/B0CX23V2ZK",
        image_url="https://m.media-amazon.com/images/I/61a+R1QQZIL._AC_SL1500_.jpg",
        availability="In Stock"
    ),
    Deal(
        asin="B0CHXYZ123",
        title="LEGO Creator Expert - Millennium Falcon Star Wars (7541 pièces)",
        current_price=399.99,
        average_price=849.99,
        discount_percent=52.94,
        product_url="https://www.amazon.fr/dp/B0CHXYZ123",
        image_url="https://m.media-amazon.com/images/I/81L5nAQDJmL._AC_SL1500_.jpg",
        availability="In Stock"
    ),
]


async def test_bot():
    """Test the Discord bot with sample deals"""
    load_dotenv()

    print("🤖 Testing Discord Bot")
    print("=" * 50)

    # Get configuration
    token = os.getenv('DISCORD_TOKEN')
    channel_id = int(os.getenv('DISCORD_CHANNEL_ID', 0))

    if not token:
        print("❌ Error: DISCORD_TOKEN not found in .env")
        return

    if not channel_id:
        print("❌ Error: DISCORD_CHANNEL_ID not found in .env")
        return

    print(f"\n📋 Configuration:")
    print(f"  Token: {token[:20]}...")
    print(f"  Channel ID: {channel_id}\n")

    # Create bot
    bot = await create_bot(token, channel_id)

    # Track if bot is ready
    bot_ready = asyncio.Event()

    @bot.event
    async def on_ready():
        """Called when bot is ready"""
        print(f"✅ Bot logged in as: {bot.user.name}")
        print(f"✅ Target channel: {bot.target_channel.name if bot.target_channel else 'NOT FOUND'}\n")
        bot_ready.set()

    # Start bot in background
    bot_task = asyncio.create_task(bot.start(token))

    try:
        # Wait for bot to be ready (with timeout)
        print("⏳ Waiting for bot to connect...")
        await asyncio.wait_for(bot_ready.wait(), timeout=30)

        # Send startup message
        print("📤 Sending startup message...")
        await bot.send_status_message("🧪 Test mode - Posting sample deals")
        await asyncio.sleep(2)

        # Post test deals
        print(f"\n📊 Posting {len(TEST_DEALS)} test deals...\n")
        for i, deal in enumerate(TEST_DEALS, 1):
            print(f"{i}. Posting: {deal.title[:50]}...")
            success = await bot.post_deal(deal)

            if success:
                print(f"   ✅ Posted successfully")
            else:
                print(f"   ❌ Failed to post")

            # Delay between posts to avoid rate limits
            await asyncio.sleep(3)

        # Send completion message
        print("\n📤 Sending completion message...")
        await bot.send_status_message("✅ Test complete - All sample deals posted!")

        print("\n🎉 Test completed successfully!")
        print("\nℹ️  Check your Discord channel to see the embeds")
        print("Press Ctrl+C to stop the bot\n")

        # Keep bot running for a bit
        await asyncio.sleep(10)

    except asyncio.TimeoutError:
        print("\n❌ Error: Bot connection timeout")
        print("Check your DISCORD_TOKEN and bot permissions")

    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.exception("Test failed")

    finally:
        print("\n🧹 Shutting down bot...")
        await bot.close()

        # Cancel bot task
        bot_task.cancel()
        try:
            await bot_task
        except asyncio.CancelledError:
            pass

        print("✅ Cleanup complete\n")


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  DISCORD BOT TEST")
    print("=" * 50 + "\n")

    try:
        asyncio.run(test_bot())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        logger.exception("Fatal error")
        sys.exit(1)

    print("\n" + "=" * 50)
    print("  TEST COMPLETE")
    print("=" * 50 + "\n")
