#!/usr/bin/env python3
"""Reset bot instance by calling deleteWebhook and closing session."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

async def reset_bot():
    """Reset bot connection."""
    from app.config import settings
    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums.parse_mode import ParseMode
    
    print("🔄 Resetting bot connection...")
    
    default_bot_props = DefaultBotProperties(parse_mode=ParseMode.HTML)
    bot = Bot(token=settings.BOT_TOKEN, default=default_bot_props)
    
    try:
        # Delete webhook if exists
        await bot.delete_webhook()
        print("✅ Webhook deleted")
    except Exception as e:
        print(f"⚠️  Webhook delete: {e}")
    
    try:
        # Close session
        await bot.session.close()
        print("✅ Session closed")
    except Exception as e:
        print(f"⚠️  Session close: {e}")
    
    print("✅ Reset complete!")

if __name__ == "__main__":
    asyncio.run(reset_bot())
