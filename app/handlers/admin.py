from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import UserRole
from app.services.repositories import UserRepository, InvestmentRepository
from app.services.portfolio_service import PortfolioService
from app.states.forms import ValuationFSM, SearchFSM
from app.utils.logger import logger, log_user_action
from app.utils.formatters import (
    format_currency, format_jalali_date, parse_currency_input
)
from app.keyboards.inline import (
    get_admin_main_menu, get_investor_list_search,
    get_valuation_update_mode_menu, get_back_menu, get_jalali_date_picker,
    get_admin_user_management_menu, get_role_selection_menu
)
from datetime import date, datetime
import jdatetime


router = Router()


async def require_admin(user_id: int, session: AsyncSession) -> bool:
    """Check if user is admin."""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(user_id)
    
    if not user or not user.is_verified:
        return False
    
    return user.role == UserRole.ADMIN


@router.callback_query(F.data == "admin_update_valuation")
async def admin_update_valuation_start(callback: types.CallbackQuery,
                                       state: FSMContext,
                                       session: AsyncSession):
    """Start portfolio valuation update flow."""
    if not await require_admin(callback.from_user.id, session):
        await callback.answer("🚫 فقط ادمین‌ها می‌تونند این کار رو انجام دهند", show_alert=True)
        return
    
    # Go to investor search
    await callback.message.edit_text(
        "📊 <b>بروزرسانی درآمد و دارایی</b>\n\n"
        "سرمایه‌گذار را جستجو کنید:",
        parse_mode="HTML"
    )
    
    await state.set_state(ValuationFSM.waiting_investor_selection)
    await callback.answer()


@router.message(ValuationFSM.waiting_investor_selection)
async def process_valuation_investor_search(message: types.Message,
                                           state: FSMContext,
                                           session: AsyncSession):
    """Process investor search for valuation."""
    query = message.text.strip()
    
    if not query or len(query) < 2:
        await message.answer("❌ لطفا نام یا شماره تماس حداقل 2 کاراکتری وارد کنید.")
        return
    
    user_repo = UserRepository(session)
    results = await user_repo.search_by_name_or_phone(query)
    
    # Filter only investors
    investors = [
        (u.id, u.name, u.phone_number)
        for u in results
        if u.role == UserRole.INVESTOR
    ]
    
    if not investors:
        await message.answer(
            f"❌ نتیجه‌ای برای «{query}» یافت نشد.\n\n"
            "لطفا دوباره تلاش کنید."
        )
        return
    
    # Save search results
    await state.update_data(investor_search_results=investors, search_page=1)
    
    kb = get_investor_list_search(investors, page=1, per_page=5)
    await message.answer(
        f"✅ <b>{len(investors)} نتیجه یافت شد</b>\n\n"
        "سرمایه‌گذار را انتخاب کنید:",
        parse_mode="HTML",
        reply_markup=kb
    )


@router.callback_query(ValuationFSM.waiting_investor_selection, F.data.startswith("select_investor_"))
async def select_investor_for_valuation(callback: types.CallbackQuery,
                                       state: FSMContext,
                                       session: AsyncSession):
    """Investor selected for valuation update."""
    investor_id = int(callback.data.split("_")[2])
    
    user_repo = UserRepository(session)
    investor = await user_repo.get_by_id(investor_id)
    
    if not investor:
        await callback.answer("❌ سرمایه‌گذار یافت نشد", show_alert=True)
        return
    
    # Get investment
    investment_repo = InvestmentRepository(session)
    investments = await investment_repo.get_by_user(investor_id)
    
    if not investments:
        await callback.answer("❌ این کاربر هیچ سرمایه‌گذاری ندارد", show_alert=True)
        return
    
    investment = investments[0]
    portfolio_service = PortfolioService(session)
    summary = await portfolio_service.get_portfolio_summary(investment.id)
    
    # Show current value and ask for update mode
    info_text = (
        f"✅ <b>سرمایه‌گذار انتخاب‌شده:</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>نام:</b> {investor.name}\n"
        f"📱 <b>تماس:</b> {investor.phone_number}\n"
        f"💰 <b>ارزش فعلی:</b> {format_currency(summary['current_value'])}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>روش بروزرسانی را انتخاب کنید:</b>"
    )
    
    await callback.message.edit_text(
        info_text,
        parse_mode="HTML",
        reply_markup=get_valuation_update_mode_menu()
    )
    
    await state.update_data(
        selected_investor_id=investor_id,
        selected_investment_id=investment.id,
        current_value=summary["current_value"]
    )
    await state.set_state(ValuationFSM.waiting_update_mode)
    await callback.answer()


@router.callback_query(ValuationFSM.waiting_update_mode, F.data == "valuation_absolute")
async def valuation_absolute_mode(callback: types.CallbackQuery,
                                  state: FSMContext):
    """Enter absolute value update mode."""
    data = await state.get_data()
    
    await callback.message.edit_text(
        f"💰 <b>ارزش جدید را وارد کنید</b>\n\n"
        f"ارزش فعلی: {format_currency(data['current_value'])}\n\n"
        f"ارزش جدید (به تومان):‌",
        parse_mode="HTML",
        reply_markup=get_back_menu("back_from_value")
    )
    
    await state.update_data(update_mode="absolute")
    await state.set_state(ValuationFSM.waiting_value_input)
    await callback.answer()


@router.callback_query(ValuationFSM.waiting_update_mode, F.data == "valuation_percentage")
async def valuation_percentage_mode(callback: types.CallbackQuery,
                                   state: FSMContext):
    """Enter profit percentage update mode."""
    await callback.message.edit_text(
        f"📊 <b>درصد سود را وارد کنید</b>\n\n"
        f"مثال: 25 برای 25%",
        parse_mode="HTML",
        reply_markup=get_back_menu("back_from_value")
    )
    
    await state.update_data(update_mode="percentage")
    await state.set_state(ValuationFSM.waiting_value_input)
    await callback.answer()


@router.message(ValuationFSM.waiting_value_input)
async def process_valuation_value(message: types.Message,
                                 state: FSMContext,
                                 session: AsyncSession):
    """Process valuation value input."""
    value_str = message.text.strip()
    
    data = await state.get_data()
    update_mode = data.get("update_mode", "absolute")
    
    try:
        if update_mode == "absolute":
            value = parse_currency_input(value_str)
            if value is None:
                await message.answer(
                    "❌ مبلغ نامعتبر است.\n\n"
                    "لطفا عدد معتبر وارد کنید."
                )
                return
            
            await state.update_data(new_value=value, profit_percentage=None)
            
            # Calculate change
            change = value - data["current_value"]
            change_pct = (change / data["current_value"] * 100) if data["current_value"] > 0 else 0
            
            summary_text = (
                f"من ارزش فعلی: {format_currency(data['current_value'])}\n"
                f"ارزش جدید: {format_currency(value)}\n"
                f"تغییر: {format_currency(change)} ({change_pct:+.2f}%)"
            )
        else:  # percentage
            try:
                profit_pct = float(value_str)
                if profit_pct < -100 or profit_pct > 1000:
                    await message.answer("❌ درصد بیرون محدوده است (حداقل -100، حداکثر 1000)")
                    return
                
                # Calculate new value from percentage
                initial_capital = data["current_value"] / (1 + profit_pct / 100) if profit_pct != -100 else data["current_value"]
                new_value = initial_capital * (1 + profit_pct / 100)
                
                await state.update_data(new_value=new_value, profit_percentage=profit_pct)
                
                change = new_value - data["current_value"]
                summary_text = (
                    f"ارزش فعلی: {format_currency(data['current_value'])}\n"
                    f"درصد سود: {profit_pct:+.2f}%\n"
                    f"ارزش جدید: {format_currency(new_value)}\n"
                    f"تغییر: {format_currency(change)}"
                )
            except ValueError:
                await message.answer("❌ درصد نامعتبر است. لطفا عدد اعشاری وارد کنید (مثال: 25.5)")
                return
        
        # Ask for reason
        await message.answer(
            f"<b>خلاصه تغییرات:</b>\n\n{summary_text}\n\n"
            f"<b>دلیل تغییر (اختیاری):</b>\n\n"
            f"توضیح اضافی ندارید؟",
            parse_mode="HTML",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="⏭️ بدون دلیل", callback_data="skip_reason")],
                    [types.InlineKeyboardButton(text="❌ لغو", callback_data="cancel_action")],
                ]
            )
        )
        
        await state.set_state(ValuationFSM.waiting_reason_input)
        
    except Exception as e:
        logger.error(f"Error processing valuation value: {e}")
        await message.answer("❌ خطا در پردازش مقدار. لطفا دوباره تلاش کنید.")


@router.message(ValuationFSM.waiting_reason_input)
async def process_valuation_reason(message: types.Message,
                                  state: FSMContext):
    """Process valuation reason."""
    reason = message.text.strip()[:500]  # Limit to 500 chars
    
    await state.update_data(reason=reason)
    
    # Show confirmation
    await show_valuation_confirmation(message, state)


@router.callback_query(F.data == "skip_reason", ValuationFSM.waiting_reason_input)
async def skip_valuation_reason(callback: types.CallbackQuery,
                               state: FSMContext):
    """Skip reason."""
    await state.update_data(reason=None)
    
    await show_valuation_confirmation(callback.message, state)
    await callback.answer()


async def show_valuation_confirmation(message_or_update, state: FSMContext):
    """Show valuation confirmation."""
    data = await state.get_data()
    
    confirmation_text = (
        f"📋 <b>بررسی بروزرسانی دارایی</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>ارزش قبلی:</b> {format_currency(data['current_value'])}\n"
        f"<b>ارزش جدید:</b> {format_currency(data['new_value'])}\n"
        f"<b>تغییر:</b> {format_currency(data['new_value'] - data['current_value'])}\n"
        f"<b>دلیل:</b> {data.get('reason', 'ندارد')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"آیا با این بروزرسانی موافق هستید؟"
    )
    
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="✅ تایید و ثبت", callback_data="confirm_valuation"),
                types.InlineKeyboardButton(text="❌ لغو", callback_data="cancel_action"),
            ]
        ]
    )
    
    await message_or_update.edit_text(confirmation_text, parse_mode="HTML", reply_markup=kb)
    await state.set_state(ValuationFSM.waiting_confirmation)


@router.callback_query(F.data == "confirm_valuation", ValuationFSM.waiting_confirmation)
async def save_valuation(callback: types.CallbackQuery,
                        state: FSMContext,
                        session: AsyncSession):
    """Save valuation to database."""
    data = await state.get_data()
    
    portfolio_service = PortfolioService(session)
    
    try:
        today = date.today()
        
        valuation = await portfolio_service.update_valuation(
            investment_id=data["selected_investment_id"],
            new_value=data["new_value"],
            valuation_date=today,
            updated_by=callback.from_user.id,
            reason=data.get("reason")
        )
        
        await session.commit()
        
        await callback.message.edit_text(
            f"✅ <b>دارایی بروزرسانی شد</b>\n\n"
            f"شناسه بروزرسانی: <code>{valuation.id}</code>",
            parse_mode="HTML",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="🏠 بازگشت", callback_data="back_to_menu")],
                ]
            )
        )
        
        log_user_action(
            callback.from_user.id,
            "valuation_updated",
            {
                "valuation_id": valuation.id,
                "investment_id": data["selected_investment_id"],
                "new_value": data["new_value"],
                "old_value": data["current_value"]
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to save valuation: {e}")
        await callback.message.edit_text(
            "❌ خطا در بروزرسانی دارایی.\n\n"
            "لطفا بعدا دوباره تلاش کنید.",
            reply_markup=get_back_menu("back_to_menu")
        )
    
    await state.clear()
    await callback.answer()


# ============== User Management ==============

@router.callback_query(F.data == "admin_manage_users")
async def admin_manage_users(callback: types.CallbackQuery,
                            session: AsyncSession):
    """Admin user management menu."""
    if not await require_admin(callback.from_user.id, session):
        await callback.answer("🚫 دسترسی رد شد", show_alert=True)
        return
    
    await callback.message.edit_text(
        "👥 <b>مدیریت کاربران</b>\n\n"
        "عملیات مورد نظر را انتخاب کنید:",
        parse_mode="HTML",
        reply_markup=get_admin_user_management_menu()
    )
    
    await callback.answer()


@router.callback_query(F.data == "admin_list_users")
async def admin_list_users(callback: types.CallbackQuery,
                          session: AsyncSession):
    """List all users."""
    user_repo = UserRepository(session)
    
    investors = await user_repo.list_by_role(UserRole.INVESTOR)
    accountants = await user_repo.list_by_role(UserRole.ACCOUNTANT)
    admins = await user_repo.list_by_role(UserRole.ADMIN)
    
    users_text = (
        f"<b>👥 لیست کاربران ({len(investors) + len(accountants) + len(admins)} کاربر)</b>\n\n"
    )
    
    if investors:
        users_text += f"<b>سرمایه‌گذاران ({len(investors)}):</b>\n"
        for user in investors[:10]:
            status = "✅" if user.is_verified else "❌"
            users_text += f"{status} {user.name} | {user.phone_number}\n"
        if len(investors) > 10:
            users_text += f"... و {len(investors) - 10} نفر دیگر\n"
        users_text += "\n"
    
    if accountants:
        users_text += f"<b>حسابداران ({len(accountants)}):</b>\n"
        for user in accountants:
            status = "✅" if user.is_verified else "❌"
            users_text += f"{status} {user.name}\n"
        users_text += "\n"
    
    if admins:
        users_text += f"<b>ادمین‌ها ({len(admins)}):</b>\n"
        for user in admins:
            status = "✅" if user.is_verified else "❌"
            users_text += f"{status} {user.name}\n"
    
    await callback.message.edit_text(
        users_text,
        parse_mode="HTML",
        reply_markup=get_back_menu("admin_manage_users")
    )
    
    await callback.answer()


@router.callback_query(F.data == "admin_reports")
async def admin_reports(callback: types.CallbackQuery,
                       session: AsyncSession):
    """Admin reports dashboard."""
    if not await require_admin(callback.from_user.id, session):
        await callback.answer("🚫 دسترسی رد شد", show_alert=True)
        return
    
    user_repo = UserRepository(session)
    
    # Get counts
    investors = await user_repo.list_by_role(UserRole.INVESTOR)
    total_investors = len(investors)
    verified_investors = len([u for u in investors if u.is_verified])
    
    reports_text = (
        f"📈 <b>گزارشات سیستم</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 کل سرمایه‌گذاران: {total_investors}\n"
        f"✅ تایید‌شده: {verified_investors}\n"
        f"❌ تایید نشده: {total_investors - verified_investors}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<i>گزارش‌های بیشتر به‌زودی اضافه می‌شوند...</i>"
    )
    
    await callback.message.edit_text(
        reports_text,
        parse_mode="HTML",
        reply_markup=get_back_menu("back_to_menu")
    )
    
    await callback.answer()
