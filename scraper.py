"""
Keepa Deal Scraper using Playwright
"""
import asyncio
import json
import logging
import os
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeout
from playwright_stealth import stealth_async

logger = logging.getLogger(__name__)


@dataclass
class Deal:
    """Represents a product deal from Keepa"""
    asin: str
    title: str
    current_price: float
    average_price: float
    discount_percent: float
    product_url: str
    image_url: str
    availability: str = "In Stock"

    @property
    def amazon_cart_url(self) -> str:
        """Generate Amazon add-to-cart URL"""
        return f"https://www.amazon.fr/gp/aws/cart/add.html?ASIN.1={self.asin}&Quantity.1=1"

    @property
    def keepa_url(self) -> str:
        """Generate Keepa product page URL"""
        return f"https://keepa.com/#!product/4-{self.asin}"

    @property
    def lookup_url(self) -> str:
        """Generate Google Shopping lookup URL"""
        return f"https://www.google.com/search?q={self.asin}+price&tbm=shop"

    @property
    def keepa_graph_url(self) -> str:
        """Generate Keepa price history graph URL"""
        return f"https://graph.keepa.com/pricehistory.png?asin={self.asin}&domain=4"


class KeepaScraperEngine:
    """
    Asynchronous web scraper for Keepa deals page
    """

    def __init__(
        self,
        keepa_url: str,
        headless: bool = True,
        use_cookies: bool = False,
        cookies_file: str = "cookies.json"
    ):
        """
        Initialize the scraper engine

        Args:
            keepa_url: URL to Keepa deals page
            headless: Run browser in headless mode
            use_cookies: Whether to load cookies from file
            cookies_file: Path to cookies JSON file
        """
        self.keepa_url = keepa_url
        self.headless = headless
        self.use_cookies = use_cookies
        self.cookies_file = cookies_file

        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def initialize(self) -> None:
        """Initialize Playwright browser and context"""
        try:
            logger.info("Initializing Playwright browser...")
            self.playwright = await async_playwright().start()

            # Launch browser with stealth configuration
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                ]
            )

            # Create context with realistic user agent
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='fr-FR',
                timezone_id='Europe/Paris'
            )

            # Load cookies if enabled
            if self.use_cookies and os.path.exists(self.cookies_file):
                await self._load_cookies()

            # Create page and apply stealth
            self.page = await self.context.new_page()
            await stealth_async(self.page)

            logger.info("Browser initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            await self.cleanup()
            raise

    async def _load_cookies(self) -> None:
        """Load cookies from JSON file"""
        try:
            cookies_path = Path(self.cookies_file)
            if cookies_path.exists():
                with open(cookies_path, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                    await self.context.add_cookies(cookies)
                    logger.info(f"Loaded {len(cookies)} cookies from {self.cookies_file}")
            else:
                logger.warning(f"Cookies file not found: {self.cookies_file}")
        except Exception as e:
            logger.error(f"Failed to load cookies: {e}")

    async def navigate_to_deals(self) -> None:
        """Navigate to Keepa deals page and wait for content"""
        try:
            logger.info(f"Navigating to {self.keepa_url}")
            await self.page.goto(self.keepa_url, wait_until='networkidle', timeout=30000)

            # Wait for the deals table to load
            # Try multiple selectors in case the page structure varies
            selectors_to_try = [
                'div.dealRow',
                'table.dealTable',
                'div[class*="deal"]',
                '#dealTable',
                'div.productTitle'
            ]

            loaded = False
            for selector in selectors_to_try:
                try:
                    await self.page.wait_for_selector(selector, timeout=10000)
                    logger.info(f"Deals loaded (selector: {selector})")
                    loaded = True
                    break
                except PlaywrightTimeout:
                    continue

            if not loaded:
                logger.warning("Could not find standard deal selectors, page may still be loading")
                await asyncio.sleep(5)  # Give extra time for dynamic content

        except PlaywrightTimeout:
            logger.error("Timeout while loading Keepa deals page")
            raise
        except Exception as e:
            logger.error(f"Navigation error: {e}")
            raise

    async def extract_deals(self, min_discount: float = 40.0) -> List[Deal]:
        """
        Extract deal data from the current page

        Args:
            min_discount: Minimum discount percentage to filter deals

        Returns:
            List of Deal objects
        """
        try:
            logger.info("Extracting deals from page...")

            # Execute JavaScript to extract deal data from the DOM
            # This is a generic implementation - adjust selectors based on actual Keepa DOM
            deals_data = await self.page.evaluate("""
                () => {
                    const deals = [];

                    // Try to find deal rows - adjust selectors based on actual DOM
                    const dealElements = document.querySelectorAll('div.dealRow, tr.dealRow, div[class*="deal"]');

                    dealElements.forEach(element => {
                        try {
                            // Extract ASIN (usually in data attributes or links)
                            const asinMatch = element.innerHTML.match(/([A-Z0-9]{10})/);
                            const asin = asinMatch ? asinMatch[1] : null;

                            // Extract title
                            const titleElement = element.querySelector('a[href*="amazon"], .productTitle, .title, h3, h4');
                            const title = titleElement ? titleElement.textContent.trim() : '';

                            // Extract prices (look for price elements)
                            const priceElements = element.querySelectorAll('[class*="price"], .priceValue, span[class*="Price"]');
                            let currentPrice = 0;
                            let averagePrice = 0;

                            // Try to parse prices from text
                            priceElements.forEach(priceEl => {
                                const priceText = priceEl.textContent.replace(/[^0-9.,]/g, '').replace(',', '.');
                                const price = parseFloat(priceText);
                                if (!isNaN(price)) {
                                    if (currentPrice === 0) currentPrice = price;
                                    else if (averagePrice === 0) averagePrice = price;
                                }
                            });

                            // Extract image URL
                            const imgElement = element.querySelector('img');
                            const imageUrl = imgElement ? imgElement.src : '';

                            // Extract product URL
                            const linkElement = element.querySelector('a[href*="amazon"]');
                            const productUrl = linkElement ? linkElement.href : `https://www.amazon.fr/dp/${asin}`;

                            // Calculate discount if we have both prices
                            let discountPercent = 0;
                            if (averagePrice > 0 && currentPrice > 0) {
                                discountPercent = ((averagePrice - currentPrice) / averagePrice) * 100;
                            }

                            if (asin && title) {
                                deals.push({
                                    asin,
                                    title,
                                    currentPrice,
                                    averagePrice,
                                    discountPercent,
                                    productUrl,
                                    imageUrl
                                });
                            }
                        } catch (err) {
                            console.error('Error extracting deal:', err);
                        }
                    });

                    return deals;
                }
            """)

            # Convert to Deal objects and filter
            deals = []
            for data in deals_data:
                try:
                    deal = Deal(
                        asin=data['asin'],
                        title=data['title'][:200],  # Truncate long titles
                        current_price=data['currentPrice'],
                        average_price=data['averagePrice'],
                        discount_percent=data['discountPercent'],
                        product_url=data['productUrl'],
                        image_url=data['imageUrl']
                    )

                    # Filter by minimum discount
                    if deal.discount_percent >= min_discount:
                        deals.append(deal)
                        logger.debug(f"Found deal: {deal.asin} - {deal.discount_percent:.1f}% off")

                except Exception as e:
                    logger.warning(f"Failed to create Deal object: {e}")
                    continue

            logger.info(f"Extracted {len(deals)} deals (filtered by {min_discount}% discount)")
            return deals

        except Exception as e:
            logger.error(f"Failed to extract deals: {e}")
            return []

    async def cleanup(self) -> None:
        """Close browser and cleanup resources"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("Browser cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    async def restart(self) -> None:
        """Restart the browser (useful for recovery from crashes)"""
        logger.info("Restarting browser...")
        await self.cleanup()
        await asyncio.sleep(2)
        await self.initialize()

    async def scrape_deals(self, min_discount: float = 40.0) -> List[Deal]:
        """
        Main scraping method - navigate and extract deals

        Args:
            min_discount: Minimum discount percentage to filter

        Returns:
            List of Deal objects
        """
        try:
            if not self.page:
                await self.initialize()

            await self.navigate_to_deals()
            deals = await self.extract_deals(min_discount)
            return deals

        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            # Attempt to restart browser on failure
            try:
                await self.restart()
            except Exception as restart_error:
                logger.error(f"Failed to restart browser: {restart_error}")
            return []
