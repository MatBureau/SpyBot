"""
Discord Bot for Amazon Price Error Monitoring
"""
import logging
from typing import Optional

import discord
from discord import Embed, Color, ButtonStyle
from discord.ui import View, Button
from discord.ext import commands

from scraper import Deal

logger = logging.getLogger(__name__)


class DealButtonsView(View):
    """Discord UI View with action buttons for deals"""

    def __init__(self, deal: Deal):
        super().__init__(timeout=None)  # Buttons never expire
        self.deal = deal

        # Button 1: BuyBox (Green) - Add to cart
        buy_button = Button(
            style=ButtonStyle.success,
            label="BuyBox",
            emoji="🛒",
            url=deal.amazon_cart_url
        )
        self.add_item(buy_button)

        # Button 2: Lookup (Blue) - Search product
        lookup_button = Button(
            style=ButtonStyle.primary,
            label="Lookup",
            emoji="🔍",
            url=deal.lookup_url
        )
        self.add_item(lookup_button)

        # Button 3: Keepa (Gray) - View on Keepa
        keepa_button = Button(
            style=ButtonStyle.secondary,
            label="Keepa",
            emoji="📈",
            url=deal.keepa_url
        )
        self.add_item(keepa_button)


class PriceMonitorBot(commands.Bot):
    """
    Discord bot for monitoring and posting Amazon price errors
    """

    def __init__(self, channel_id: int, *args, **kwargs):
        """
        Initialize the bot

        Args:
            channel_id: Discord channel ID where deals will be posted
        """
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            *args,
            **kwargs
        )

        self.channel_id = channel_id
        self.target_channel: Optional[discord.TextChannel] = None

    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f"Bot logged in as {self.user.name} (ID: {self.user.id})")

        # Get the target channel
        try:
            self.target_channel = self.get_channel(self.channel_id)
            if not self.target_channel:
                self.target_channel = await self.fetch_channel(self.channel_id)

            if self.target_channel:
                logger.info(f"Target channel set: {self.target_channel.name}")
            else:
                logger.error(f"Could not find channel with ID: {self.channel_id}")

        except Exception as e:
            logger.error(f"Error fetching channel: {e}")

    async def post_deal(self, deal: Deal) -> bool:
        """
        Post a deal to the configured Discord channel

        Args:
            deal: Deal object to post

        Returns:
            True if posted successfully, False otherwise
        """
        if not self.target_channel:
            logger.error("Target channel not set, cannot post deal")
            return False

        try:
            # Create rich embed
            embed = self._create_deal_embed(deal)

            # Create button view
            view = DealButtonsView(deal)

            # Send message with embed and buttons
            await self.target_channel.send(embed=embed, view=view)
            logger.info(f"Posted deal: {deal.asin} ({deal.discount_percent:.1f}% off)")
            return True

        except Exception as e:
            logger.error(f"Failed to post deal {deal.asin}: {e}")
            return False

    def _create_deal_embed(self, deal: Deal) -> Embed:
        """
        Create a rich Discord embed for a deal

        Args:
            deal: Deal object

        Returns:
            Discord Embed object
        """
        # Calculate color based on discount (deeper red = better deal)
        if deal.discount_percent >= 70:
            color = Color.dark_red()
        elif deal.discount_percent >= 60:
            color = Color.red()
        elif deal.discount_percent >= 50:
            color = Color.orange()
        else:
            color = Color.blurple()  # Default Discord blue

        # Create embed
        embed = Embed(
            title=deal.title,
            url=deal.product_url,
            description=f"**🚨 Price Error Detected - {deal.discount_percent:.1f}% OFF!**",
            color=color
        )

        # Add fields
        embed.add_field(
            name="🏪 Store",
            value="Amazon FR",
            inline=True
        )

        embed.add_field(
            name="💰 Price",
            value=f"~~€{deal.average_price:.2f}~~ → **€{deal.current_price:.2f}**",
            inline=True
        )

        embed.add_field(
            name="📉 Discount",
            value=f"**-{deal.discount_percent:.1f}%**",
            inline=True
        )

        embed.add_field(
            name="📦 Availability",
            value=deal.availability,
            inline=True
        )

        embed.add_field(
            name="🔖 ASIN",
            value=f"`{deal.asin}`",
            inline=True
        )

        # Add savings calculation
        savings = deal.average_price - deal.current_price
        embed.add_field(
            name="💸 You Save",
            value=f"**€{savings:.2f}**",
            inline=True
        )

        # Set Keepa price history graph as image
        embed.set_image(url=deal.keepa_graph_url)

        # Set thumbnail (product image if available)
        if deal.image_url:
            embed.set_thumbnail(url=deal.image_url)

        # Footer
        embed.set_footer(
            text="Amazon Price Monitor • Powered by Keepa",
            icon_url="https://keepa.com/favicon.ico"
        )

        return embed

    async def send_status_message(self, message: str, error: bool = False) -> None:
        """
        Send a status message to the channel

        Args:
            message: Status message to send
            error: Whether this is an error message
        """
        if not self.target_channel:
            return

        try:
            embed = Embed(
                title="🤖 Bot Status",
                description=message,
                color=Color.red() if error else Color.green()
            )
            await self.target_channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Failed to send status message: {e}")


async def create_bot(token: str, channel_id: int) -> PriceMonitorBot:
    """
    Factory function to create and return the bot instance

    Args:
        token: Discord bot token
        channel_id: Channel ID for posting deals

    Returns:
        Configured PriceMonitorBot instance
    """
    bot = PriceMonitorBot(channel_id=channel_id)
    return bot
