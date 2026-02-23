import logging
import json
from datetime import datetime
from pathlib import Path


def setup_logger(name: str, log_file: str = "logs/bot.log") -> logging.Logger:
    """Set up structured logging."""
    
    # Create logs directory
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Global logger instance
logger = setup_logger("pishro_bot")


class BotError(Exception):
    """Base exception for bot errors."""
    
    def __init__(self, message: str, user_message: str = None):
        self.message = message
        self.user_message = user_message or message
        super().__init__(self.message)


class AuthenticationError(BotError):
    """User authentication failed."""
    user_message = "شما دسترسی ندارید"


class DatabaseError(BotError):
    """Database operation failed."""
    user_message = "خطا در دسترسی به پایگاه داده"


class ValidationError(BotError):
    """Validation of user input failed."""
    pass


class TelegramAPIError(BotError):
    """Telegram API call failed."""
    user_message = "خطا در ارسال پیام تلگرام"


def log_error(error: Exception, context: dict = None):
    """Log error with context."""
    context = context or {}
    logger.error(
        f"Error: {str(error)}",
        extra={"context": json.dumps(context, default=str)}
    )


def log_database_query(query: str, params: dict = None):
    """Log database queries (only in debug mode)."""
    logger.debug(f"Database query: {query}", extra={"params": params})


def log_user_action(user_id: int, action: str, details: dict = None):
    """Log user actions for audit."""
    details = details or {}
    logger.info(
        f"User action: {action}",
        extra={
            "user_id": user_id,
            "action": action,
            "details": json.dumps(details, default=str)
        }
    )
