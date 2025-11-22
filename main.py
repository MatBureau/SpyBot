"""
Amazon Price Monitor - Main Entry Point
Monitors Amazon France for price errors via Keepa and posts to Discord
"""
import asyncio
import logging
import os
import sys
from typing import Optional

from dotenv import load_dotenv

from scraper import KeepaScraperEngine, Deal
from bot import PriceMonitorBot, create_bot
from cache import DealCache


# Configure logging
def setup_logging(debug: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if debug else logging.INFO

    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('price_monitor.log', encoding='utf-8')
        ]
    )

    # Reduce noise from discord.py and playwright
    logging.getLogger('discord').setLevel(logging.WARNING)
    logging.getLogger('discord.http').setLevel(logging.WARNING)
    logging.getLogger('playwright').setLevel(logging.WARNING)


logger = logging.getLogger(__name__)


class PriceMonitorApp:
    """Main application orchestrator"""

    def __init__(self):
        """Initialize the application"""
        # Load environment variables
        load_dotenv()

        # Discord configuration
        self.discord_token = os.getenv('DISCORD_TOKEN')
        self.channel_id = int(os.getenv('DISCORD_CHANNEL_ID', 0))

        # Scraper configuration
        self.keepa_url = os.getenv('KEEPA_URL', 'https://keepa.com/#!deals/4')
        self.scraper_interval = int(os.getenv('SCRAPER_INTERVAL', 300))
        self.headless = os.getenv('HEADLESS_MODE', 'true').lower() == 'true'

        # Filter configuration
        self.min_discount = float(os.getenv('MIN_DISCOUNT_PERCENT', 40))
        self.cache_duration = int(os.getenv('CACHE_DURATION_HOURS', 24))

        # Browser configuration
        self.use_cookies = os.getenv('USE_COOKIES', 'false').lower() == 'true'
        self.cookies_file = os.getenv('COOKIES_FILE', 'cookies.json')

        # Debug mode
        debug = os.getenv('DEBUG', 'false').lower() == 'true'
        setup_logging(debug)

        # Validate configuration
        self._validate_config()

        # Initialize components
        self.bot: Optional[PriceMonitorBot] = None
        self.scraper: Optional[KeepaScraperEngine] = None
        self.cache = DealCache(cache_duration_hours=self.cache_duration)

        self.running = False
        self.scraper_task: Optional[asyncio.Task] = None

    def _validate_config(self):
        """Validate required configuration"""
        if not self.discord_token:
            raise ValueError("DISCORD_TOKEN is required in .env file")
        if not self.channel_id:
            raise ValueError("DISCORD_CHANNEL_ID is required in .env file")

        logger.info("Configuration validated successfully")
        logger.info(f"Keepa URL: {self.keepa_url}")
        logger.info(f"Scraper interval: {self.scraper_interval}s")
        logger.info(f"Min discount: {self.min_discount}%")
        logger.info(f"Cache duration: {self.cache_duration}h")
        logger.info(f"Headless mode: {self.headless}")
        logger.info(f"Use cookies: {self.use_cookies}")

    async def initialize(self):
        """Initialize bot and scraper"""
        logger.info("Initializing Price Monitor...")

        # Create bot instance
        self.bot = await create_bot(self.discord_token, self.channel_id)

        # Create scraper instance
        self.scraper = KeepaScraperEngine(
            keepa_url=self.keepa_url,
            headless=self.headless,
            use_cookies=self.use_cookies,
            cookies_file=self.cookies_file
        )

        logger.info("Initialization complete")

    async def scraper_loop(self):
        """Background task that continuously scrapes for deals"""
        logger.info("Starting scraper loop...")

        await asyncio.sleep(10)  # Wait for bot to be ready

        while self.running:
            try:
                logger.info("Starting scraping cycle...")

                # Scrape deals
                deals = await self.scraper.scrape_deals(min_discount=self.min_discount)

                # Process each deal
                for deal in deals:
                    if not self.running:
                        break

                    # Check if already posted
                    if self.cache.is_cached(deal.asin):
                        logger.debug(f"Skipping cached deal: {deal.asin}")
                        continue

                    # Post to Discord
                    success = await self.bot.post_deal(deal)

                    if success:
                        # Add to cache
                        self.cache.add(deal.asin)
                        logger.info(f"Posted new deal: {deal.title[:50]}... ({deal.discount_percent:.1f}% off)")

                        # Small delay between posts to avoid rate limits
                        await asyncio.sleep(2)

                logger.info(f"Scraping cycle complete. Found {len(deals)} deals.")

                # Log cache stats
                stats = self.cache.get_stats()
                logger.debug(f"Cache stats: {stats}")

                # Wait before next cycle
                logger.info(f"Waiting {self.scraper_interval}s until next scan...")
                await asyncio.sleep(self.scraper_interval)

            except asyncio.CancelledError:
                logger.info("Scraper loop cancelled")
                break

            except Exception as e:
                logger.error(f"Error in scraper loop: {e}", exc_info=True)

                # Try to recover
                try:
                    logger.info("Attempting to restart scraper...")
                    await self.scraper.restart()
                    await asyncio.sleep(30)  # Wait before retry
                except Exception as restart_error:
                    logger.error(f"Failed to restart scraper: {restart_error}")
                    await asyncio.sleep(60)  # Longer wait on failure

        logger.info("Scraper loop stopped")

    async def start(self):
        """Start the application"""
        logger.info("Starting Amazon Price Monitor...")
        self.running = True

        try:
            # Initialize components
            await self.initialize()

            # Initialize the scraper browser
            await self.scraper.initialize()

            # Start scraper background task
            self.scraper_task = asyncio.create_task(self.scraper_loop())

            # Send startup message
            await self.bot.send_status_message(
                "✅ Price Monitor is now online and scanning for deals!"
            )

            # Start Discord bot (this blocks until bot is stopped)
            await self.bot.start(self.discord_token)

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
        finally:
            await self.stop()

    async def stop(self):
        """Stop the application gracefully"""
        logger.info("Stopping application...")
        self.running = False

        # Cancel scraper task
        if self.scraper_task and not self.scraper_task.done():
            self.scraper_task.cancel()
            try:
                await self.scraper_task
            except asyncio.CancelledError:
                pass

        # Cleanup scraper
        if self.scraper:
            await self.scraper.cleanup()

        # Close bot
        if self.bot:
            try:
                await self.bot.send_status_message(
                    "🔴 Price Monitor is shutting down..."
                )
            except:
                pass

            await self.bot.close()

        logger.info("Application stopped")


async def main():
    """Main entry point"""
    app = PriceMonitorApp()
    await app.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        sys.exit(1)
