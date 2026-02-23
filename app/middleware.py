"""Middleware for dependency injection and request handling."""

from aiogram import BaseMiddleware
from aiogram.types import Update, Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import AsyncSessionLocal
from app.utils.logger import logger


class DatabaseSessionMiddleware(BaseMiddleware):
    """Inject database session into handler context."""
    
    async def __call__(self, handler, event: Update, data: dict):
        """Add database session to handler data."""
        async with AsyncSessionLocal() as session:
            data["session"] = session
            try:
                return await handler(event, data)
            except Exception as e:
                logger.error(f"Error in handler: {e}", exc_info=True)
                await session.rollback()
                raise
            finally:
                await session.close()


class LoggingMiddleware(BaseMiddleware):
    """Log all incoming updates."""
    
    async def __call__(self, handler, event: Update, data: dict):
        """Log update details."""
        if event.message:
            logger.debug(
                f"Message from {event.message.from_user.id}: {event.message.text}"
            )
        elif event.callback_query:
            logger.debug(
                f"Callback from {event.callback_query.from_user.id}: {event.callback_query.data}"
            )
        
        return await handler(event, data)


class RateLimitMiddleware(BaseMiddleware):
    """Rate limiting middleware (basic implementation)."""
    
    def __init__(self):
        self.user_requests = {}
        self.max_requests_per_minute = 20  # Requests per minute
    
    async def __call__(self, handler, event: Update, data: dict):
        """Check rate limit for user."""
        user_id = None
        
        if event.message:
            user_id = event.message.from_user.id
        elif event.callback_query:
            user_id = event.callback_query.from_user.id
        
        if user_id:
            import time
            current_time = time.time()
            
            if user_id not in self.user_requests:
                self.user_requests[user_id] = []
            
            # Remove old requests (older than 60 seconds)
            self.user_requests[user_id] = [
                req_time for req_time in self.user_requests[user_id]
                if current_time - req_time < 60
            ]
            
            # Check limit
            if len(self.user_requests[user_id]) >= self.max_requests_per_minute:
                logger.warning(f"Rate limit exceeded for user {user_id}")
                return  # Drop update
            
            # Add current request
            self.user_requests[user_id].append(current_time)
        
        return await handler(event, data)


class ErrorHandlingMiddleware(BaseMiddleware):
    """Centralized error handling."""
    
    async def __call__(self, handler, event: Update, data: dict):
        """Handle errors with user-friendly responses."""
        try:
            return await handler(event, data)
        except Exception as e:
            logger.error(
                f"Unhandled exception in middleware: {e}",
                exc_info=True,
                extra={"update": event}
            )
            raise
