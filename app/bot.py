import asyncio
import logging
from aiogram import Dispatcher, Bot, types, F
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault
from app.config import settings
from app.database.session import init_db, close_db, AsyncSessionLocal, Base
from app.utils.logger import logger, setup_logger
from app.middleware import DatabaseSessionMiddleware, LoggingMiddleware, ErrorHandlingMiddleware
from sqlalchemy.pool import StaticPool
import sys
from pathlib import Path

# Setup logging
setup_logger("pishro_bot")


class PishroBot:
    """Main Telegram bot application."""
    
    def __init__(self):
        default_bot_props = DefaultBotProperties(parse_mode=ParseMode.HTML)
        self.bot = Bot(token=settings.BOT_TOKEN, default=default_bot_props)
        self.storage = MemoryStorage()
        self.dp = Dispatcher(storage=self.storage)
        self._setup_middleware()
        self._setup_handlers()
    
    def _setup_middleware(self):
        """Register middleware."""
        # Order matters: outer middleware runs first
        self.dp.message.middleware(ErrorHandlingMiddleware())
        self.dp.callback_query.middleware(ErrorHandlingMiddleware())
        
        self.dp.message.middleware(DatabaseSessionMiddleware())
        self.dp.callback_query.middleware(DatabaseSessionMiddleware())
        
        self.dp.message.middleware(LoggingMiddleware())
        self.dp.callback_query.middleware(LoggingMiddleware())
    
    def _setup_handlers(self):
        """Register all bot handlers."""
        from app.handlers import auth, investor, accountant, admin, settings
        
        # Register routers
        self.dp.include_router(auth.router)
        self.dp.include_router(settings.router)
        self.dp.include_router(investor.router)
        self.dp.include_router(accountant.router)
        self.dp.include_router(admin.router)
        
        # Add default error handler
        self.dp.error.register(self._error_handler)
    
    async def _error_handler(self, update: types.Update, exception: Exception):
        """Handle errors globally."""
        logger.error(f"Update {update} caused error: {exception}", exc_info=True)
        
        if update.message:
            try:
                await update.message.answer(
                    "❌ خطای سیستمی رخ داد.\n"
                    "لطفا بعدا دوباره تلاش کنید یا با پشتیبان تماس بگیرید.",
                    parse_mode=ParseMode.HTML
                )
            except Exception as e:
                logger.error(f"Failed to send error message: {e}")
    
    async def setup_default_commands(self):
        """Set up bot commands in Telegram."""
        commands = [
            BotCommand(command="start", description="شروع ربات"),
            BotCommand(command="help", description="راهنمایی"),
            BotCommand(command="logout", description="خروج"),
        ]
        
        await self.bot.set_my_commands(
            commands,
            scope=BotCommandScopeDefault()
        )
        logger.info("Bot commands configured")
    
    async def start_polling(self):
        """Start bot in polling mode."""
        logger.info("Starting bot in polling mode...")
        
        # Initialize database
        try:
            await init_db()
            logger.info("Database initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
        
        # Set up commands
        await self.setup_default_commands()
        logger.info("Bot ready to receive updates!")
        
        try:
            # Start polling
            logger.info("Starting polling loop...")
            await self.dp.start_polling(
                self.bot,
                allowed_updates=self.dp.resolve_used_update_types(),
                skip_updates=False
            )
        finally:
            await close_db()
            await self.bot.session.close()
    
    async def start_webhook(self, path: str = "/webhook", host: str = "localhost", port: int = 8080):
        """Start bot in webhook mode."""
        from aiohttp import web
        
        logger.info(f"Starting bot in webhook mode on {host}:{port}")
        
        # Initialize database
        try:
            await init_db()
            logger.info("Database initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
        
        # Set up commands
        await self.setup_default_commands()
        
        # Set webhook URL
        webhook_url = settings.WEBHOOK_URL or f"http://{host}:{port}{path}"
        try:
            await self.bot.set_webhook_info(
                url=webhook_url,
                allowed_updates=self.dp.resolve_used_update_types()
            )
            logger.info(f"Webhook set to {webhook_url}")
        except Exception as e:
            logger.error(f"Failed to set webhook: {e}")
        
        # Create web app
        app = web.Application()
        
        # Webhook handler
        async def webhook_handler(request: web.Request):
            try:
                update = types.Update(**await request.json())
                await self.dp.feed_update(self.bot, update)
                return web.Response()
            except Exception as e:
                logger.error(f"Webhook error: {e}")
                return web.Response(status=500)
        
        app.router.post(path, webhook_handler)
        
        # Health check
        async def health_check(request: web.Request):
            return web.json_response({"status": "ok"})
        
        app.router.get("/health", health_check)
        
        # Run web server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        logger.info(f"Webhook server started on {host}:{port}")
        
        try:
            # Keep running
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            await runner.cleanup()
            await close_db()
            await self.bot.session.close()


async def main():
    """Main entry point."""
    bot = PishroBot()
    
    # Choose mode based on environment
    # For now, use polling (easier for development)
    await bot.start_polling()


if __name__ == "__main__":
    # Ensure app package is in path
    app_dir = Path(__file__).parent
    sys.path.insert(0, str(app_dir.parent))
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
