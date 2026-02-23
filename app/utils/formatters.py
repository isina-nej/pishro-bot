from datetime import date, datetime
import jdatetime
from typing import Optional, Tuple


def gregorian_to_jalali(gregorian_date: date) -> jdatetime.date:
    """Convert Gregorian date to Jalali date."""
    if isinstance(gregorian_date, datetime):
        gregorian_date = gregorian_date.date()
    return jdatetime.date.fromgregorian(gregorian_date)


def jalali_to_gregorian(jalali_date: jdatetime.date) -> date:
    """Convert Jalali date to Gregorian date."""
    return jalali_date.togregorian()


def format_jalali_date(gregorian_date: date, format_str: str = "%A %d, %Y") -> str:
    """Format date in Jalali calendar.
    
    Args:
        gregorian_date: Date to format
        format_str: Format string (default: فروردین 1, 1402)
    
    Returns:
        Formatted Persian date string
    """
    jalali_date = gregorian_to_jalali(gregorian_date)
    
    # Persian month names
    month_names_fa = {
        1: "فروردین", 2: "اردیبهشت", 3: "خرداد",
        4: "تیر", 5: "مرداد", 6: "شهریور",
        7: "مهر", 8: "آبان", 9: "آذر",
        10: "دی", 11: "بهمن", 12: "اسفند"
    }
    
    return f"{month_names_fa[jalali_date.month]} {jalali_date.day}, {jalali_date.year}"


def format_currency(amount: float) -> str:
    """Format amount as Persian currency with comma separators.
    
    Args:
        amount: Amount in Toman
    
    Returns:
        Formatted string (e.g., "1,000,000,000 تومان")
    """
    # Format with commas
    formatted_amount = f"{amount:,.0f}" if amount >= 0 else f"({abs(amount):,.0f})"
    return f"{formatted_amount} تومان"


def parse_currency_input(text: str) -> Optional[float]:
    """Parse user input as currency amount.
    
    Args:
        text: User input (e.g., "500000000", "5e8", "500,000,000")
    
    Returns:
        Parsed amount or None if invalid
    """
    try:
        # Remove commas and spaces
        text = text.replace(",", "").replace(" ", "")
        
        # Try to parse as float
        amount = float(text)
        
        # Validate reasonable range (>0, < 100 billion)
        if amount <= 0 or amount > 100_000_000_000:
            return None
        
        return amount
    except ValueError:
        return None


def format_phone_number(phone: str) -> str:
    """Format phone number to standard format (0912XXXXXXXX)."""
    phone = phone.replace(" ", "").replace("-", "").strip()
    
    # Handle international format
    if phone.startswith("+98"):
        phone = "0" + phone[3:]
    elif phone.startswith("98") and not phone.startswith("0"):
        phone = "0" + phone[2:]
    
    return phone


def calculate_portfolio_balance(initial_capital: float, transactions: list) -> float:
    """Calculate current portfolio balance from initial capital and transactions.
    
    Args:
        initial_capital: Initial investment amount
        transactions: List of transaction amounts
    
    Returns:
        Current total balance
    """
    return initial_capital + sum(t.amount for t in transactions)


def calculate_profit_percentage(initial_capital: float, current_value: float) -> float:
    """Calculate profit percentage.
    
    Args:
        initial_capital: Original investment
        current_value: Current portfolio value
    
    Returns:
        Profit percentage (0-100)
    """
    if initial_capital == 0:
        return 0
    return ((current_value - initial_capital) / initial_capital) * 100


def get_persian_numbers(text: str) -> str:
    """Convert English numbers to Persian numbers."""
    persian_digits = {
        '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
        '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
    }
    return ''.join(persian_digits.get(c, c) for c in text)


def get_english_numbers(text: str) -> str:
    """Convert Persian numbers to English numbers."""
    english_digits = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
    }
    return ''.join(english_digits.get(c, c) for c in text)


def validate_phone_number_format(phone: str) -> bool:
    """Validate Iranian phone number format."""
    phone = format_phone_number(phone)
    
    # Should be 11 digits starting with 09
    if len(phone) != 11:
        return False
    if not phone.startswith("09"):
        return False
    if not phone.isdigit():
        return False
    
    return True


def parse_jalali_date_parts(year: int, month: int, day: int) -> Optional[date]:
    """Convert Jalali date parts to Gregorian date.
    
    Args:
        year: Jalali year
        month: Jalali month (1-12)
        day: Jalali day (1-31)
    
    Returns:
        Gregorian date or None if invalid
    """
    try:
        jalali_date = jdatetime.date(year, month, day)
        return jalali_date.togregorian()
    except (ValueError, OverflowError):
        return None
