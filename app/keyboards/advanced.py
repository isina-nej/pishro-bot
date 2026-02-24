"""
Advanced Inline Keyboards with Glass Panel Design
صفحه‌کلید پیشرفتهٔ Inline با طراحی پنل شیشه‌ای
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_admin_start_menu() -> InlineKeyboardMarkup:
    """Admin welcome menu with settings."""
    return InlineKeyboardMarkup(inline_keyboard=[
        # Row 1: Main actions
        [
            InlineKeyboardButton(text="📊 داشبورد", callback_data="view_dashboard"),
            InlineKeyboardButton(text="💼 سرمایه‌گذاری‌ها", callback_data="view_investments"),
        ],
        # Row 2: Management
        [
            InlineKeyboardButton(text="👥 مدیریت کاربران", callback_data="manage_users"),
            InlineKeyboardButton(text="📈 گزارش‌ها", callback_data="view_reports"),
        ],
        # Row 3: Settings
        [
            InlineKeyboardButton(text="⚙️ تنظیمات", callback_data="settings_menu"),
            InlineKeyboardButton(text="👤 پروفایل", callback_data="view_profile"),
        ],
        # Row 4: Help & Exit
        [
            InlineKeyboardButton(text="❓ راهنمایی", callback_data="help_menu"),
            InlineKeyboardButton(text="🚪 خروج", callback_data="logout_confirm"),
        ],
    ])


def get_investor_start_menu() -> InlineKeyboardMarkup:
    """Investor welcome menu."""
    return InlineKeyboardMarkup(inline_keyboard=[
        # Row 1: Portfolio
        [
            InlineKeyboardButton(text="💰 پورتفولیو من", callback_data="my_portfolio"),
            InlineKeyboardButton(text="📊 وضعیت سرمایه‌گذاری", callback_data="investment_status"),
        ],
        # Row 2: Actions
        [
            InlineKeyboardButton(text="➕ سرمایه‌گذاری جدید", callback_data="new_investment"),
            InlineKeyboardButton(text="💳 معاملات", callback_data="my_transactions"),
        ],
        # Row 3: Settings
        [
            InlineKeyboardButton(text="⚙️ تنظیمات", callback_data="settings_menu"),
            InlineKeyboardButton(text="👤 پروفایل", callback_data="view_profile"),
        ],
        # Row 4: Help & Exit
        [
            InlineKeyboardButton(text="❓ راهنمایی", callback_data="help_menu"),
            InlineKeyboardButton(text="🚪 خروج", callback_data="logout_confirm"),
        ],
    ])


def get_accountant_menu() -> InlineKeyboardMarkup:
    """Accountant menu."""
    return InlineKeyboardMarkup(inline_keyboard=[
        # Row 1: Reports
        [
            InlineKeyboardButton(text="📑 گزارش معاملات", callback_data="transaction_report"),
            InlineKeyboardButton(text="📊 خلاصه سرمایه‌گذاری‌ها", callback_data="investment_summary"),
        ],
        # Row 2: Analysis
        [
            InlineKeyboardButton(text="💹 تحلیل", callback_data="analysis_menu"),
            InlineKeyboardButton(text="📈 درآمد و هزینه", callback_data="financials"),
        ],
        # Row 3: Settings
        [
            InlineKeyboardButton(text="⚙️ تنظیمات", callback_data="settings_menu"),
            InlineKeyboardButton(text="👤 پروفایل", callback_data="view_profile"),
        ],
        # Row 4: Help & Exit
        [
            InlineKeyboardButton(text="❓ راهنمایی", callback_data="help_menu"),
            InlineKeyboardButton(text="🚪 خروج", callback_data="logout_confirm"),
        ],
    ])


def get_settings_menu() -> InlineKeyboardMarkup:
    """Settings panel with various options."""
    return InlineKeyboardMarkup(inline_keyboard=[
        # Row 1: Notification
        [
            InlineKeyboardButton(text="🔔 اطلاع‌رسانی ها", callback_data="notification_settings"),
            InlineKeyboardButton(text="🌙 حالت شب", callback_data="theme_settings"),
        ],
        # Row 2: Privacy & Security
        [
            InlineKeyboardButton(text="🔐 امنیت", callback_data="security_settings"),
            InlineKeyboardButton(text="👁️ حریم خصوصی", callback_data="privacy_settings"),
        ],
        # Row 3: Language & Region
        [
            InlineKeyboardButton(text="🌐 زبان", callback_data="language_settings"),
            InlineKeyboardButton(text="⏰ منطقهٔ زمانی", callback_data="timezone_settings"),
        ],
        # Row 4: Account
        [
            InlineKeyboardButton(text="🔑 تغییر رمز", callback_data="change_password"),
            InlineKeyboardButton(text="📱 بروزرسانی شماره", callback_data="update_phone"),
        ],
        # Row 5: Navigation
        [
            InlineKeyboardButton(text="◀️ برگشت", callback_data="back_to_main"),
        ],
    ])


def get_help_menu() -> InlineKeyboardMarkup:
    """Help and Documentation menu."""
    return InlineKeyboardMarkup(inline_keyboard=[
        # Row 1: Guides
        [
            InlineKeyboardButton(text="📖 راهنمای شروع", callback_data="getting_started"),
            InlineKeyboardButton(text="💡 نکات مفید", callback_data="tips_tricks"),
        ],
        # Row 2: FAQs
        [
            InlineKeyboardButton(text="❓ سوالات متداول", callback_data="faq_menu"),
            InlineKeyboardButton(text="🆘 حل مسائل", callback_data="troubleshooting"),
        ],
        # Row 3: Contact
        [
            InlineKeyboardButton(text="📞 تماس با پشتیبان", callback_data="contact_support"),
            InlineKeyboardButton(text="📧 درباره ما", callback_data="about_us"),
        ],
        # Row 4: Navigation
        [
            InlineKeyboardButton(text="◀️ برگشت", callback_data="back_to_main"),
        ],
    ])


def get_yes_no_keyboard() -> InlineKeyboardMarkup:
    """Simple Yes/No confirmation keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ بله", callback_data="confirm_yes"),
            InlineKeyboardButton(text="❌ خیر", callback_data="confirm_no"),
        ],
    ])


def get_back_button() -> InlineKeyboardMarkup:
    """Back button only."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="◀️ برگشت", callback_data="back_to_main"),
        ],
    ])


def get_pagination_keyboard(page: int, total_pages: int, prefix: str = "page") -> InlineKeyboardMarkup:
    """Pagination keyboard for lists."""
    buttons = []
    
    # Previous button
    if page > 1:
        buttons.append(InlineKeyboardButton(text="◀️ قبلی", callback_data=f"{prefix}_{page-1}"))
    
    # Page indicator
    buttons.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="page_info"))
    
    # Next button
    if page < total_pages:
        buttons.append(InlineKeyboardButton(text="بعدی ▶️", callback_data=f"{prefix}_{page+1}"))
    
    return InlineKeyboardMarkup(inline_keyboard=[
        buttons,
        [InlineKeyboardButton(text="◀️ برگشت", callback_data="back_to_main")],
    ])


def get_quick_actions() -> InlineKeyboardMarkup:
    """Quick action buttons."""
    return InlineKeyboardMarkup(inline_keyboard=[
        # Row 1: Deposit/Withdraw
        [
            InlineKeyboardButton(text="💵 واریز", callback_data="deposit"),
            InlineKeyboardButton(text="💸 برداشت", callback_data="withdrawal"),
        ],
        # Row 2: View/Report
        [
            InlineKeyboardButton(text="📊 شاخص‌ها", callback_data="metrics"),
            InlineKeyboardButton(text="🔔 اطلاع‌رسانی", callback_data="notifications"),
        ],
        # Row 3: Back
        [
            InlineKeyboardButton(text="◀️ برگشت", callback_data="back_to_main"),
        ],
    ])
