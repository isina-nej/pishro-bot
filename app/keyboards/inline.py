from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from app.models.models import UserRole

# ============== Main Menus ==============

def get_investor_main_menu() -> InlineKeyboardMarkup:
    """Main menu for investor users."""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💰 وضعیت سرمایه من", callback_data="investor_portfolio_status")],
            [InlineKeyboardButton(text="📜 تاریخچه تراکنش‌ها", callback_data="investor_transaction_history")],
            [InlineKeyboardButton(text="⚙️ تنظیمات", callback_data="settings_menu")],
            [InlineKeyboardButton(text="📞 تماس با پشتیبانی", callback_data="support_contact")],
        ]
    )
    return kb


def get_accountant_main_menu() -> InlineKeyboardMarkup:
    """Main menu for accountant users."""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ ثبت تراکنش جدید", callback_data="record_transaction")],
            [InlineKeyboardButton(text="🔍 جستجو سرمایه‌گذار", callback_data="search_investor")],
            [InlineKeyboardButton(text="✏️ ویرایش تراکنش", callback_data="edit_transaction")],
            [InlineKeyboardButton(text="📜 تاریخچه تراکنش‌ها", callback_data="accountant_transaction_history")],
            [InlineKeyboardButton(text="🚪 خروج", callback_data="logout")],
        ]
    )
    return kb


def get_admin_main_menu() -> InlineKeyboardMarkup:
    """Main menu for admin users."""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💰 وضعیت سرمایه من", callback_data="investor_portfolio_status")],
            [InlineKeyboardButton(text="📊 بروزرسانی درآمد و دارایی", callback_data="admin_update_valuation")],
            [InlineKeyboardButton(text="👥 مدیریت کاربران", callback_data="admin_manage_users")],
            [InlineKeyboardButton(text="📈 گزارشات", callback_data="admin_reports")],
            [InlineKeyboardButton(text="⚙️ تنظیمات سیستم", callback_data="admin_settings")],
            [InlineKeyboardButton(text="🚪 خروج", callback_data="logout")],
        ]
    )
    return kb


# ============== Transaction Flow ==============

def get_transaction_type_menu() -> InlineKeyboardMarkup:
    """Menu for selecting transaction type."""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ واریز", callback_data="txn_deposit"),
                InlineKeyboardButton(text="➖ برداشت", callback_data="txn_withdrawal"),
            ],
            [
                InlineKeyboardButton(text="💰 سود", callback_data="txn_dividend"),
                InlineKeyboardButton(text="🔴 فسخ", callback_data="txn_cancellation"),
            ],
            [InlineKeyboardButton(text="❌ لغو", callback_data="cancel_action")],
        ]
    )
    return kb


def get_confirm_cancel_menu(confirm_data: str = "confirm", cancel_data: str = "cancel") -> InlineKeyboardMarkup:
    """Generic confirm/cancel menu."""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ تایید", callback_data=confirm_data),
                InlineKeyboardButton(text="❌ لغو", callback_data=cancel_data),
            ],
        ]
    )
    return kb


def get_back_menu(back_data: str = "back") -> InlineKeyboardMarkup:
    """Simple back button."""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data=back_data)],
        ]
    )
    return kb


def get_pagination_menu(page: int, total_pages: int, prev_data: str, next_data: str) -> InlineKeyboardMarkup:
    """Pagination controls."""
    buttons = []
    
    if page > 1:
        buttons.append(InlineKeyboardButton(text="◀ قبلی", callback_data=prev_data))
    
    buttons.append(InlineKeyboardButton(text=f"صفحه {page}/{total_pages}", callback_data="noop"))
    
    if page < total_pages:
        buttons.append(InlineKeyboardButton(text="بعدی ▶", callback_data=next_data))
    
    kb = InlineKeyboardMarkup(inline_keyboard=[buttons])
    return kb


# ============== Investor Search Results ==============

def get_investor_list_search(investors: list, page: int = 1, per_page: int = 5):
    """Generate buttons for investor selection.
    
    Args:
        investors: List of (id, name, phone) tuples
        page: Current page number
        per_page: Items per page
    
    Returns:
        InlineKeyboardMarkup with investor buttons
    """
    # Calculate pagination
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    page_investors = investors[start_idx:end_idx]
    
    buttons = []
    for investor_id, name, phone in page_investors:
        buttons.append([
            InlineKeyboardButton(
                text=f"👤 {name} | {phone}",
                callback_data=f"select_investor_{investor_id}"
            )
        ])
    
    # Add pagination
    if len(investors) > per_page:
        pagination_buttons = []
        if page > 1:
            pagination_buttons.append(
                InlineKeyboardButton(text="◀ قبلی", callback_data=f"investor_search_page_{page - 1}")
            )
        pagination_buttons.append(
            InlineKeyboardButton(text=f"{page}/{(len(investors) + per_page - 1) // per_page}", callback_data="noop")
        )
        if end_idx < len(investors):
            pagination_buttons.append(
                InlineKeyboardButton(text="بعدی ▶", callback_data=f"investor_search_page_{page + 1}")
            )
        buttons.append(pagination_buttons)
    
    buttons.append([InlineKeyboardButton(text="❌ لغو", callback_data="cancel_action")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============== Settings ==============

def get_settings_menu() -> InlineKeyboardMarkup:
    """Settings menu for investors."""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔔 مدیریت اطلاع‌رسانی", callback_data="settings_notifications")],
            [InlineKeyboardButton(text="🌐 زبان", callback_data="settings_language")],
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_to_menu")],
        ]
    )
    return kb


def get_notification_settings_menu(notifications_enabled: bool = True) -> InlineKeyboardMarkup:
    """Notification settings menu."""
    txn_status = "✅" if notifications_enabled else "⬜"
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{txn_status} اطلاع تراکنش‌ها", callback_data="toggle_txn_notifications")],
            [InlineKeyboardButton(text="✅ اطلاع بروزرسانی دارایی", callback_data="toggle_valuation_notifications")],
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_to_menu")],
        ]
    )
    return kb


# ============== Admin Menus ==============

def get_admin_user_management_menu() -> InlineKeyboardMarkup:
    """Admin user management menu."""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ افزودن کاربر جدید", callback_data="admin_add_user")],
            [InlineKeyboardButton(text="➖ حذف کاربر", callback_data="admin_delete_user")],
            [InlineKeyboardButton(text="🔄 تغییر نقش", callback_data="admin_change_role")],
            [InlineKeyboardButton(text="📋 لیست کاربران", callback_data="admin_list_users")],
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_to_menu")],
        ]
    )
    return kb


def get_role_selection_menu() -> InlineKeyboardMarkup:
    """Role selection menu for user management."""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👤 سرمایه‌گذار", callback_data="role_investor")],
            [InlineKeyboardButton(text="💼 حسابدار", callback_data="role_accountant")],
            [InlineKeyboardButton(text="👨‍💼 ادمین", callback_data="role_admin")],
            [InlineKeyboardButton(text="❌ لغو", callback_data="cancel_action")],
        ]
    )
    return kb


def get_valuation_update_mode_menu() -> InlineKeyboardMarkup:
    """Menu for choosing valuation update mode."""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💰 ارزش مطلق", callback_data="valuation_absolute")],
            [InlineKeyboardButton(text="📊 درصد سود", callback_data="valuation_percentage")],
            [InlineKeyboardButton(text="❌ لغو", callback_data="cancel_action")],
        ]
    )
    return kb


# ============== Date Picker ==============

def get_jalali_date_picker(year: int, month: int, day: int):
    """Create Jalali date picker using inline buttons."""
    
    # Persian month names
    months_fa = [
        "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
        "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
    ]
    
    month_names = months_fa[1::3]  # Just show 4 months per row
    
    buttons = []
    
    # Year row
    buttons.append([
        InlineKeyboardButton(text=f"◀ {year-1}", callback_data=f"date_year_{year-1}"),
        InlineKeyboardButton(text=str(year), callback_data="noop"),
        InlineKeyboardButton(text=f"{year+1} ▶", callback_data=f"date_year_{year+1}"),
    ])
    
    # Month selection (show all 12 months)
    month_buttons = []
    for i, month_name in enumerate(months_fa):
        is_selected = (i + 1 == month)
        prefix = "✓ " if is_selected else ""
        month_buttons.append(
            InlineKeyboardButton(
                text=f"{prefix}{month_name}",
                callback_data=f"date_month_{i+1}"
            )
        )
    
    # Add months in rows of 3
    for i in range(0, len(month_buttons), 3):
        buttons.append(month_buttons[i:i+3])
    
    # Day selection (1-31)
    day_buttons = []
    for d in range(1, 32):
        is_selected = (d == day)
        prefix = "✓" if is_selected else ""
        day_buttons.append(
            InlineKeyboardButton(
                text=f"{prefix}{d:02d}",
                callback_data=f"date_day_{d}"
            )
        )
    
    # Add days in rows of 7
    for i in range(0, len(day_buttons), 7):
        buttons.append(day_buttons[i:i+7])
    
    # Confirm button
    buttons.append([
        InlineKeyboardButton(text="✅ تایید", callback_data=f"date_confirm_{year}_{month}_{day}"),
        InlineKeyboardButton(text="❌ لغو", callback_data="cancel_action"),
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============== Help Functions ==============

def get_main_menu(role: UserRole) -> InlineKeyboardMarkup:
    """Get appropriate main menu based on user role."""
    if role == UserRole.INVESTOR:
        return get_investor_main_menu()
    elif role == UserRole.ACCOUNTANT:
        return get_accountant_main_menu()
    elif role == UserRole.ADMIN:
        return get_admin_main_menu()
    else:
        return InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="🏠 خانه", callback_data="back_to_menu")
        ]])
