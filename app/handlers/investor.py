from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import UserRole
from app.services.repositories import UserRepository, InvestmentRepository
from app.services.portfolio_service import PortfolioService
from app.utils.logger import logger, log_user_action
from app.utils.formatters import format_currency, format_jalali_date
from app.keyboards.inline import get_investor_main_menu, get_pagination_menu, get_back_menu
from datetime import date


router = Router()


async def require_investor(message: types.Message, session: AsyncSession) -> bool:
    """Check if user is investor."""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    
    if not user or not user.is_verified:
        await message.answer("🚫 شما دسترسی ندارید")
        return False
    
    if user.role != UserRole.INVESTOR and user.role != UserRole.ADMIN:
        await message.answer("🚫 این بخش فقط برای سرمایه‌گذاران است")
        return False
    
    return True


@router.callback_query(F.data == "investor_portfolio_status")
async def investor_portfolio_status(callback: types.CallbackQuery, session: AsyncSession):
    """Display investor's portfolio status."""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    
    if not user or not user.is_verified:
        await callback.answer("🚫 شما دسترسی ندارید", show_alert=True)
        return
    
    if user.role not in [UserRole.INVESTOR, UserRole.ADMIN]:
        await callback.answer("🚫 دسترسی رد شد", show_alert=True)
        return
    
    # Get investments for user
    investment_repo = InvestmentRepository(session)
    investments = await investment_repo.get_by_user(user.id)
    
    if not investments:
        await callback.message.edit_text(
            "❌ هیچ سرمایه‌گذاری برای شما ثبت نشده است."
        )
        await callback.answer()
        return
    
    # For now, show first/main investment (in future: support multiple)
    investment = investments[0]
    
    portfolio_service = PortfolioService(session)
    summary = await portfolio_service.get_portfolio_summary(investment.id)
    
    if not summary:
        await callback.message.edit_text("❌ خطا در بارگیری اطلاعات")
        await callback.answer()
        return
    
    # Format message
    contract_type_display = {
        "fixed_rate": "درآمد ثابت 8% ماهانه",
        "variable_holding": "هولد پی‌ریودی متغیر"
    }.get(summary["contract_type"].value, "نامشخص")
    
    message_text = (
        f"💰 <b>وضعیت سرمایه من</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<i>نوع قرارداد:</i> {contract_type_display}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 <b>سرمایه اولیه:</b> {format_currency(summary['initial_capital'])}\n"
        f"➕ <b>واریزهای اضافی:</b> {format_currency(summary['current_deposits'])}\n"
        f"➖ <b>برداشت‌ها:</b> {format_currency(summary['current_withdrawals'])}\n"
        f"💵 <b>سود/درآمد:</b> {format_currency(summary['total_transactions_profit'])}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>💎 ارزش فعلی: {format_currency(summary['current_value'])}</b>\n"
        f"📊 سود: <code>{summary['profit_percentage']:.2f}%</code>\n"
        f"🕐 آخرین بروزرسانی: {format_jalali_date(summary['last_updated'])}\n"
    )
    
    await callback.message.edit_text(
        message_text,
        parse_mode="HTML",
        reply_markup=get_back_menu("investor_portfolio_status")
    )
    
    await callback.answer()
    log_user_action(user.id, "view_portfolio_status", {"investment_id": investment.id})


@router.callback_query(F.data == "investor_transaction_history")
async def investor_transaction_history(callback: types.CallbackQuery, 
                                       state: FSMContext,
                                       session: AsyncSession):
    """Display investor's transaction history with pagination."""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    
    if not user or not user.is_verified:
        await callback.answer("🚫 شما دسترسی ندارید", show_alert=True)
        return
    
    if user.role not in [UserRole.INVESTOR, UserRole.ADMIN]:
        await callback.answer("🚫 دسترسی رد شد", show_alert=True)
        return
    
    # Get first investment (main account)
    investment_repo = InvestmentRepository(session)
    investments = await investment_repo.get_by_user(user.id)
    
    if not investments:
        await callback.message.edit_text("❌ هیچ سرمایه‌گذاری برای شما ثبت نشده است.")
        await callback.answer()
        return
    
    investment = investments[0]
    
    # Get transaction history
    portfolio_service = PortfolioService(session)
    transactions, total_count = await portfolio_service.get_transaction_history(
        investment.id, limit=10, offset=0
    )
    
    if not transactions:
        await callback.message.edit_text(
            "📜 <b>تاریخچه تراکنش‌ها</b>\n\n"
            "❌ هیچ تراکنشی ثبت نشده است.",
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    # Format transactions
    txn_lines = ["📜 <b>تاریخچه تراکنش‌ها</b>\n", "━━━━━━━━━━━━━━━━━"]
    
    txn_type_emoji = {
        "deposit": "➕",
        "withdrawal": "➖",
        "dividend": "💰",
        "cancellation": "🔴"
    }
    
    for txn in transactions:
        emoji = txn_type_emoji.get(txn.type.value, "•")
        date_display = format_jalali_date(txn.transaction_date)
        amount_display = format_currency(txn.amount)
        
        txn_lines.append(
            f"{emoji} {date_display} | {amount_display}\n"
            f"   توضیح: {txn.description or 'ندارد'}"
        )
    
    message_text = "\n".join(txn_lines)
    
    # Save state for pagination
    await state.update_data(investment_id=investment.id, current_page=1, total_transactions=total_count)
    
    await callback.message.edit_text(
        message_text,
        parse_mode="HTML",
        reply_markup=get_back_menu("investor_transaction_history")
    )
    
    await callback.answer()
    log_user_action(user.id, "view_transaction_history", {"investment_id": investment.id})


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery, session: AsyncSession):
    """Return to main menu."""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    
    if not user:
        await callback.answer("❌ خطا در یافتن کاربر", show_alert=True)
        return
    
    from app.keyboards.inline import get_main_menu
    
    await callback.message.edit_text(
        f"سلام {user.name}! 👋\n\n" 
        "چه کاری می‌تونم برای شما کنم؟",
        reply_markup=get_main_menu(user.role)
    )
    await callback.answer()
