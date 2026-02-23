from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import UserRole, TransactionType
from app.services.repositories import UserRepository, InvestmentRepository
from app.services.portfolio_service import PortfolioService
from app.states.forms import TransactionFSM, SearchFSM
from app.utils.logger import logger, log_user_action
from app.utils.formatters import (
    format_currency, format_jalali_date, parse_currency_input,
    parse_jalali_date_parts, get_persian_numbers
)
from app.keyboards.inline import (
    get_accountant_main_menu, get_transaction_type_menu,
    get_confirm_cancel_menu, get_back_menu, get_investor_list_search,
    get_jalali_date_picker
)
from datetime import date, datetime
import jdatetime


router = Router()


async def require_accountant(user_id: int, session: AsyncSession) -> bool:
    """Check if user is accountant or admin."""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(user_id)
    
    if not user or not user.is_verified:
        return False
    
    return user.role in [UserRole.ACCOUNTANT, UserRole.ADMIN]


@router.callback_query(F.data == "record_transaction")
async def record_transaction_start(callback: types.CallbackQuery, 
                                   state: FSMContext,
                                   session: AsyncSession):
    """Start transaction recording flow."""
    if not await require_accountant(callback.from_user.id, session):
        await callback.answer("🚫 دسترسی رد شد", show_alert=True)
        return
    
    # Go to investor search
    await callback.message.edit_text(
        "🔍 <b>جستجو سرمایه‌گذار</b>\n\n"
        "نام یا شماره تماس سرمایه‌گذار را وارد کنید:",
        parse_mode="HTML"
    )
    
    await state.set_state(TransactionFSM.waiting_investor_selection)
    await callback.answer()


@router.message(TransactionFSM.waiting_investor_selection)
async def process_investor_search(message: types.Message,
                                  state: FSMContext,
                                  session: AsyncSession):
    """Process investor search query."""
    query = message.text.strip()
    
    if not query or len(query) < 2:
        await message.answer("❌ لطفا نام یا شماره تماس حداقل 2 کاراکتری وارد کنید.")
        return
    
    user_repo = UserRepository(session)
    
    # Search for investors
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
    
    # Save search results and show first page
    await state.update_data(investor_search_results=investors, search_page=1)
    
    kb = get_investor_list_search(investors, page=1, per_page=5)
    await message.answer(
        f"✅ <b>{len(investors)} نتیجه یافت شد</b>\n\n"
        "سرمایه‌گذار را انتخاب کنید:",
        parse_mode="HTML",
        reply_markup=kb
    )
    
    await state.set_state(TransactionFSM.waiting_investor_selection)


@router.callback_query(F.data.startswith("select_investor_"))
async def select_investor(callback: types.CallbackQuery,
                         state: FSMContext,
                         session: AsyncSession):
    """Investor selected - proceed to transaction type."""
    investor_id = int(callback.data.split("_")[2])
    
    user_repo = UserRepository(session)
    investor = await user_repo.get_by_id(investor_id)
    
    if not investor:
        await callback.answer("❌ سرمایه‌گذار یافت نشد", show_alert=True)
        return
    
    # Get investment overview
    investment_repo = InvestmentRepository(session)
    investments = await investment_repo.get_by_user(investor_id)
    
    if not investments:
        await callback.answer("❌ این کاربر هیچ سرمایه‌گذاری ندارد", show_alert=True)
        return
    
    investment = investments[0]
    portfolio_service = PortfolioService(session)
    summary = await portfolio_service.get_portfolio_summary(investment.id)
    
    # Show investor info and transaction type selection
    info_text = (
        f"✅ <b>سرمایه‌گذار انتخاب‌شده:</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>نام:</b> {investor.name}\n"
        f"📱 <b>تماس:</b> {investor.phone_number}\n"
        f"💰 <b>موجودی فعلی:</b> {format_currency(summary['current_value'])}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>نوع تراکنش را انتخاب کنید:</b>"
    )
    
    await callback.message.edit_text(
        info_text,
        parse_mode="HTML",
        reply_markup=get_transaction_type_menu()
    )
    
    await state.update_data(selected_investor_id=investor_id, selected_investment_id=investment.id)
    await state.set_state(TransactionFSM.waiting_transaction_type)
    await callback.answer()
    
    log_user_action(callback.from_user.id, "select_investor", {"investor_id": investor_id})


# Transaction Type Selection
transaction_type_map = {
    "txn_deposit": (TransactionType.DEPOSIT, "➕ واریز سرمایه"),
    "txn_withdrawal": (TransactionType.WITHDRAWAL, "➖ برداشت"),
    "txn_dividend": (TransactionType.DIVIDEND, "💰 سود"),
    "txn_cancellation": (TransactionType.CANCELLATION, "🔴 فسخ قرارداد"),
}


@router.callback_query(TransactionFSM.waiting_transaction_type, F.data.in_(transaction_type_map.keys()))
async def select_transaction_type(callback: types.CallbackQuery,
                                  state: FSMContext):
    """Transaction type selected - ask for amount."""
    txn_type, txn_display = transaction_type_map[callback.data]
    
    await callback.message.edit_text(
        f"<b>{txn_display}</b>\n\n"
        f"مبلغ تراکنش را به تومان وارد کنید:\n"
        f"<i>(مثال: 500000000)</i>",
        parse_mode="HTML",
        reply_markup=get_back_menu("back_from_amount")
    )
    
    await state.update_data(transaction_type=txn_type.value)
    await state.set_state(TransactionFSM.waiting_amount_input)
    await callback.answer()


@router.message(TransactionFSM.waiting_amount_input)
async def process_amount(message: types.Message,
                         state: FSMContext,
                         session: AsyncSession):
    """Process amount input."""
    amount_str = message.text.strip()
    
    # Parse amount
    amount = parse_currency_input(amount_str)
    if amount is None:
        await message.answer(
            "❌ مبلغ نامعتبر است.\n\n"
            "لطفا عدد معتبر وارد کنید (مثال: 500000000)"
        )
        return
    
    # Store amount and ask for date
    await state.update_data(amount=amount)
    
    # Create date picker
    today = datetime.now().date()
    jalali_today = jdatetime.date.fromgregorian(today)
    
    await message.answer(
        "📅 <b>تاریخ تراکنش را انتخاب کنید:</b>",
        parse_mode="HTML",
        reply_markup=get_jalali_date_picker(
            jalali_today.year, jalali_today.month, jalali_today.day
        )
    )
    
    await state.set_state(TransactionFSM.waiting_date_input)


@router.callback_query(TransactionFSM.waiting_date_input, F.data.startswith("date_"))
async def process_date_picker(callback: types.CallbackQuery,
                              state: FSMContext):
    """Handle date picker selections."""
    parts = callback.data.split("_")
    
    data = await state.get_data()
    year = data.get("date_year", jdatetime.datetime.now().year)
    month = data.get("date_month", jdatetime.datetime.now().month)
    day = data.get("date_day", jdatetime.datetime.now().day)
    
    # Update selected date part
    if parts[1] == "year":
        year = int(parts[2])
    elif parts[1] == "month":
        month = int(parts[2])
    elif parts[1] == "day":
        day = int(parts[2])
    
    # Store date parts
    await state.update_data(date_year=year, date_month=month, date_day=day)
    
    # Redraw picker with updated selection
    await callback.message.edit_reply_markup(
        reply_markup=get_jalali_date_picker(year, month, day)
    )
    
    await callback.answer()


@router.callback_query(TransactionFSM.waiting_date_input, F.data.startswith("date_confirm_"))
async def confirm_date(callback: types.CallbackQuery,
                       state: FSMContext):
    """Date confirmed - ask for description."""
    parts = callback.data.split("_")
    year, month, day = int(parts[2]), int(parts[3]), int(parts[4])
    
    # Convert to Gregorian
    jalali_date = jdatetime.date(year, month, day)
    gregorian_date = jalali_date.togregorian()
    
    await state.update_data(transaction_date=gregorian_date)
    
    await callback.message.edit_text(
        f"📝 <b>توضیح (اختیاری)</b>\n\n"
        f"برای تراکنش توضیح اضافی دارید؟",
        parse_mode="HTML",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="⏭️ بدون توضیح", callback_data="skip_description")],
                [types.InlineKeyboardButton(text="❌ لغو", callback_data="cancel_action")],
            ]
        )
    )
    
    await state.set_state(TransactionFSM.waiting_description_input)
    await callback.answer()


@router.message(TransactionFSM.waiting_description_input)
async def process_description(message: types.Message,
                             state: FSMContext):
    """Process description input."""
    description = message.text.strip()[:500]  # Limit to 500 chars
    
    await state.update_data(description=description)
    
    # Show confirmation screen
    await show_confirmation(message, state)


@router.callback_query(F.data == "skip_description", TransactionFSM.waiting_description_input)
async def skip_description(callback: types.CallbackQuery,
                          state: FSMContext):
    """Skip description."""
    await state.update_data(description=None)
    
    await show_confirmation(callback.message, state)
    await callback.answer()


async def show_confirmation(message_or_update, state: FSMContext):
    """Show transaction confirmation screen."""
    data = await state.get_data()
    
    txn_type_display = {
        "deposit": "➕ واریز",
        "withdrawal": "➖ برداشت",
        "dividend": "💰 سود",
        "cancellation": "🔴 فسخ",
    }.get(data["transaction_type"], "نامشخص")
    
    date_display = format_jalali_date(data["transaction_date"])
    amount_display = format_currency(data["amount"])
    description = data.get("description", "ندارد")
    
    confirmation_text = (
        f"📋 <b>بررسی ثبت تراکنش</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>نوع:</b> {txn_type_display}\n"
        f"<b>مبلغ:</b> {amount_display}\n"
        f"<b>تاریخ:</b> {date_display}\n"
        f"<b>توضیح:</b> {description}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"آیا از صحت اطلاعات اطمینان دارید؟"
    )
    
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="✅ تایید و ثبت", callback_data="confirm_transaction"),
                types.InlineKeyboardButton(text="❌ لغو", callback_data="cancel_action"),
            ]
        ]
    )
    
    await message_or_update.edit_text(confirmation_text, parse_mode="HTML", reply_markup=kb)
    await state.set_state(TransactionFSM.waiting_confirmation)


@router.callback_query(F.data == "confirm_transaction", TransactionFSM.waiting_confirmation)
async def save_transaction(callback: types.CallbackQuery,
                          state: FSMContext,
                          session: AsyncSession):
    """Save transaction to database."""
    data = await state.get_data()
    
    portfolio_service = PortfolioService(session)
    
    try:
        txn_type = TransactionType(data["transaction_type"])
        
        transaction = await portfolio_service.record_transaction(
            investment_id=data["selected_investment_id"],
            txn_type=txn_type,
            amount=data["amount"],
            transaction_date=data["transaction_date"],
            recorded_by=callback.from_user.id,
            description=data.get("description")
        )
        
        await session.commit()
        
        await callback.message.edit_text(
            f"✅ <b>تراکنش ثبت شدبته‌ای</b>\n\n"
            f"شناسه تراکنش: <code>{transaction.id}</code>",
            parse_mode="HTML",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="🏠 بازگشت", callback_data="back_to_menu")],
                ]
            )
        )
        
        log_user_action(
            callback.from_user.id,
            "transaction_recorded",
            {
                "transaction_id": transaction.id,
                "investment_id": data["selected_investment_id"],
                "type": data["transaction_type"],
                "amount": data["amount"]
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to save transaction: {e}")
        await callback.message.edit_text(
            "❌ خطا در ثبت تراکنش.\n\n"
            "لطفا بعدا دوباره تلاش کنید.",
            reply_markup=get_back_menu("back_to_menu")
        )
    
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "cancel_action")
async def cancel_action(callback: types.CallbackQuery,
                       state: FSMContext):
    """Cancel current action."""
    await state.clear()
    
    await callback.message.edit_text(
        "❌ عملیات لغو شد.",
        reply_markup=get_back_menu("back_to_menu")
    )
    await callback.answer()
