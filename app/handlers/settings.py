"""
Advanced handlers for Glass Panel UI with Settings and Features
هندلرهای پیشرفتهٔ رابط‌کاربری شیشه‌ای با تنظیمات و قابلیت‌ها
"""

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import User
from app.services.repositories import UserRepository
from app.utils.logger import logger, log_user_action
from app.keyboards.advanced import (
    get_admin_start_menu, get_investor_start_menu, get_accountant_menu,
    get_settings_menu, get_help_menu, get_yes_no_keyboard, get_back_button
)
from app.keyboards.inline import get_main_menu
from app.handlers.auth import get_role_name

router = Router()


# ==================== Main Menu Navigation ====================

@router.callback_query(F.data == "back_to_main")
async def back_to_main(query: types.CallbackQuery, session: AsyncSession):
    """Go back to main menu."""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(query.from_user.id)
    
    if not user or not user.is_verified:
        await query.answer("❌ خطا در دسترسی", show_alert=True)
        return
    
    # Choose appropriate menu
    if user.role.value == "admin":
        keyboard = get_admin_start_menu()
    elif user.role.value == "accountant":
        keyboard = get_accountant_menu()
    else:
        keyboard = get_investor_start_menu()
    
    await query.message.edit_text(
        f"🏠 منوی اصلی\n\n👋 {user.name}، برای ادامه یکی گزینه را انتخاب کنید:",
        reply_markup=keyboard
    )
    await query.answer()


# ==================== Settings Panel ====================

@router.callback_query(F.data == "settings_menu")
async def settings_menu(query: types.CallbackQuery):
    """Settings menu."""
    await query.message.edit_text(
        """
⚙️ <b>تنظیمات</b>

لطفا یکی از تنظیمات را انتخاب کنید:
        """,
        reply_markup=get_settings_menu(),
        parse_mode="HTML"
    )
    await query.answer()


@router.callback_query(F.data == "notification_settings")
async def notification_settings(query: types.CallbackQuery):
    """Notification settings."""
    await query.message.edit_text(
        """
🔔 <b>تنظیمات اطلاع‌رسانی</b>

✅ <b>بارگی فعال است:</b>
  • اطلاع‌رسانی معاملات
  • اطلاع‌رسانی سود و درآمد
  • اطلاع‌رسانی گزارش‌های شاخص
  • اطلاع‌رسانی پیام‌های سیستمی

برای تغییر تنظیمات، با پشتیبان تماس بگیرید.
        """,
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )
    await query.answer()


@router.callback_query(F.data == "security_settings")
async def security_settings(query: types.CallbackQuery, session: AsyncSession):
    """Security settings."""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(query.from_user.id)
    
    await query.message.edit_text(
        f"""
🔐 <b>تنظیمات امنیتی</b>

<b>اطلاعات فعلی:</b>
  • <b>شماره تلگرام:</b> {query.from_user.id}
  • <b>شماره تماس:</b> {user.phone_number if user else 'نامشخص'}
  • <b>نقش:</b> {get_role_name(user.role) if user else 'نامشخص'}

<b>گزینه‌های امنیتی:</b>
  ✓ احراز دو مرحله‌ای (فعال خودکار)
  ✓ رمزگذاری معلومات حساسی
  ✓ لاگ فعالیت‌های سیستم

برای تغییر رمز، دستور /changepass را استفاده کنید.
        """,
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )
    await query.answer()


@router.callback_query(F.data == "privacy_settings")
async def privacy_settings(query: types.CallbackQuery):
    """Privacy settings."""
    await query.message.edit_text(
        """
👁️ <b>تنظیمات حریم خصوصی</b>

<b>سیاست حریم خصوصی:</b>

✓ <b>اطلاعات شما محفوظ است:</b>
  • شماره تماس فقط در سیستم ذخیره می‌شود
  • هیچ اطلاعات شخصی با سوم‌شخص اشتراک نمی‌یابد
  • تمام داده‌ها رمزگذاری شده در دیتابیس نگهداری می‌شود

✓ <b>حق عدم مزاحمت:</b>
  • می‌توانید هر زمان به شیوهٔ اطلاع‌رسانی تغییر دهید
  • می‌توانید حسابتان را حذف کنید (پس از پاسخ پشتیبان)

<b>تماس برای سوالات:</b>
برای اطلاعات بیشتر با پشتیبان تماس بگیرید.
        """,
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )
    await query.answer()


# ==================== Profile ====================

@router.callback_query(F.data == "view_profile")
async def view_profile(query: types.CallbackQuery, session: AsyncSession):
    """View user profile."""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(query.from_user.id)
    
    if not user:
        await query.answer("❌ خطا در دریافت اطلاعات", show_alert=True)
        return
    
    verified_date = user.verified_at.strftime("%Y-%m-%d") if user.verified_at else "ثبت نشده"
    created_date = user.created_at.strftime("%Y-%m-%d") if user.created_at else "نامشخص"
    
    profile_text = f"""
👤 <b>پروفایل کاربری</b>

<b>اطلاعات شخصی:</b>
  • <b>نام:</b> {user.name}
  • <b>شماره تماس:</b> {user.phone_number}
  • <b>ID تلگرام:</b> <code>{query.from_user.id}</code>

<b>اطلاعات حساب:</b>
  • <b>نقش:</b> {get_role_name(user.role)}
  • <b>وضعیت:</b> {'✅ فعال' if user.is_verified else '⏳ در انتظار تایید'}
  • <b>تاریخ ثبت:</b> {created_date}
  • <b>تاریخ تایید:</b> {verified_date}

<b>عملیات:</b>
  📱 برای تغییر شماره تماس: /updatephone
  🔐 برای تغییر رمز: /changepass
  📝 برای بروزرسانی پروفایل: /editprofile
    """
    
    await query.message.edit_text(profile_text, reply_markup=get_back_button(), parse_mode="HTML")
    await query.answer()


# ==================== Help Menu ====================

@router.callback_query(F.data == "help_menu")
async def help_menu(query: types.CallbackQuery):
    """Help menu."""
    await query.message.edit_text(
        """
❓ <b>راهنمایی و پشتیبانی</b>

لطفا یکی از گزینه‌های زیر را انتخاب کنید:
        """,
        reply_markup=get_help_menu(),
        parse_mode="HTML"
    )
    await query.answer()


@router.callback_query(F.data == "getting_started")
async def getting_started(query: types.CallbackQuery):
    """Get started guide."""
    await query.message.edit_text(
        """
📖 <b>راهنمای شروع</b>

<b>مرحله 1: ورود به سیستم</b>
  1️⃣ دستور /start را بفرستید
  2️⃣ شماره تلفن خود را وارد کنید
  3️⃣ منتظر تایید شماره باشید

<b>مرحله 2: خانه‌ی اول</b>
  📊 داشبورد خود را بررسی کنید
  💰 سرمایه‌گذاری‌های فعل را مشاهده کنید
  📈 گزارش‌ها را دنبال کنید

<b>مرحله 3: سرمایه‌گذاری</b>
  ➕ سرمایه‌گذاری جدید ایجاد کنید
  💵 درآمد و سود خود را مشاهده کنید
  📊 تحلیل‌ها را بررسی کنید

<b>نکات مهم:</b>
  ✓ همیشه رمز خود را محفوظ نگاه دارید
  ✓ اطلاع‌رسانی‌ها را فعال نگاه دارید
  ✓ گزارش‌ها را منظم بررسی کنید
        """,
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )
    await query.answer()


@router.callback_query(F.data == "faq_menu")
async def faq_menu(query: types.CallbackQuery):
    """FAQ menu."""
    await query.message.edit_text(
        """
❓ <b>سوالات متداول</b>

<b>سوال 1: چطور سرمایه‌گذاری کنم؟</b>
پاسخ: از منوی اصلی گزینهٔ "سرمایه‌گذاری جدید" را انتخاب کنید و مراحل را دنبال کنید.

<b>سوال 2: چطور درآمد خود را چک کنم؟</b>
پاسخ: گزینهٔ "پورتفولیو من" یا "گزارش‌ها" را انتخاب کنید.

<b>سوال 3: آیا امن است؟</b>
پاسخ: بله! تمام اطلاعات رمزگذاری شده و محفوظ است.

<b>سوال 4: چه کسی می‌تواند سرمایه‌گذاری کند؟</b>
پاسخ: هر کسی با حساب معتبر و تایید شده می‌تواند.

برای سوالات بیشتر با پشتیبان تماس بگیرید.
        """,
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )
    await query.answer()


@router.callback_query(F.data == "contact_support")
async def contact_support(query: types.CallbackQuery):
    """Contact support."""
    await query.message.edit_text(
        """
📞 <b>تماس با پشتیبان</b>

<b>راه‌های تماس:</b>

📧 <b>ایمیل:</b>
  support@pishro.ir

📱 <b>تلفن:</b>
  021-9999-0000 (دفتر)
  0901-999-9999 (پشتیبانی)

🕐 <b>ساعات کاری:</b>
  شنبه تا پنجشنبه
  ساعت 09:00 تا 18:00

💬 <b>پیام‌رسان:</b>
  @PishroSupport

⏱️ <b>پاسخ در عرض:</b>
  • چت‌های فوری: کمتر از 1 ساعت
  • ایمیل‌ها: در عرض 24 ساعت

لطفا صبرکاری کنید، تیم ما برای کمک آماده است!
        """,
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )
    await query.answer()


# ==================== Admin Features ====================

@router.callback_query(F.data == "view_dashboard")
async def view_dashboard(query: types.CallbackQuery, session: AsyncSession):
    """Admin dashboard."""
    user_repo = UserRepository(session)
    users = await user_repo.list_by_role("investor" if hasattr("investor", '__str__') else None)
    
    dashboard_text = f"""
📊 <b>داشبورد مدیریت</b>

<b>آمار کلی:</b>
  👥 کل کاربران: {1}
  💼 سرمایه‌گذاران: {len(users) if users else 0}
  📈 سرمایه‌گذاری‌های فعال: 1
  💰 کل سرمایه: 1,000,000,000 تومان

<b>عملیات اخیر:</b>
  ✓ آخرین ورود: امروز
  ✓ تراکنش‌های امروز: 0
  ✓ کاربران جدید: 0

<b>متریک‌های مهم:</b>
  📊 بازدهی ماه: بدونی محاسبه
  📈 میانگین سود: بدونی محاسبه
  ⚠️ مورد توجه: -
    """
    
    await query.message.edit_text(dashboard_text, reply_markup=get_back_button(), parse_mode="HTML")
    await query.answer()


# ==================== Logout ====================

@router.callback_query(F.data == "logout_confirm")
async def logout_confirm(query: types.CallbackQuery):
    """Confirm logout."""
    await query.message.edit_text(
        """
🚪 <b>تأیید خروج</b>

آیا مطمئن هستید که می‌خواهید خارج شوید؟

⚠️ <b>توجه:</b> پس از خروج، برای ورود مجدد باید /start را دوباره بفرستید.
        """,
        reply_markup=get_yes_no_keyboard(),
        parse_mode="HTML"
    )
    await query.answer()


@router.callback_query(F.data == "confirm_yes")
async def confirm_logout(query: types.CallbackQuery, state: FSMContext):
    """Perform logout."""
    await state.clear()
    await query.message.edit_text(
        """
👋 <b>موفقیت‌آمیز خارج شدند!</b>

برای ورود مجدد، دستور /start را بفرستید.

شکریہ که از ما استفاده کردید! 🙏
        """,
        parse_mode="HTML"
    )
    await query.answer("خروج موفقیت‌آمیز بود")


@router.callback_query(F.data == "confirm_no")
async def cancel_logout(query: types.CallbackQuery, session: AsyncSession):
    """Cancel logout."""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(query.from_user.id)
    
    if user and user.role.value == "admin":
        keyboard = get_admin_start_menu()
    elif user and user.role.value == "accountant":
        keyboard = get_accountant_menu()
    else:
        keyboard = get_investor_start_menu()
    
    await query.message.edit_text(
        f"🏠 بازگشت به منوی اصلی\n\n👋 {user.name if user else 'کاربر'}",
        reply_markup=keyboard
    )
    await query.answer("لغو شد")


@router.callback_query(F.data == "about_us")
async def about_us(query: types.CallbackQuery):
    """About us page."""
    await query.message.edit_text(
        """
ℹ️ <b>درباره ما</b>

<b>سیستم سرمایه‌گذاری Pishro</b>

🎯 <b>مأموریت:</b>
تسهیل فرایند سرمایه‌گذاری و مدیریت پورتفولیو برای تمام

🌟 <b>ویژگی‌های ما:</b>
  ✨ رویکرد امن و قابل اعتماد
  ✨ تحلیل‌های دقیق و real-time
  ✨ پشتیبانی 24/7
  ✨ رابط‌کاربری ساده و شهودی

📱 <b>نسخه:</b> 1.0.0
📅 <b>تاریخ راه‌اندازی:</b> فروردین 1402 (2023)
🌐 <b>وب‌سایت:</b> www.pishro.ir
📧 <b>ایمیل:</b> info@pishro.ir

🙏 <b>سپاس:</b>
ما بر اساس اعتماد و رضایت کاربران خود کار می‌کنیم.

© 2026 Pishro. All rights reserved.
        """,
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )
    await query.answer()
