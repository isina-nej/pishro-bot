from aiogram import Router, F, types
from aiogram.enums.content_type import ContentType
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import User, UserRole
from app.services.repositories import UserRepository
from app.utils.logger import logger, log_user_action, AuthenticationError
from app.utils.formatters import format_phone_number, validate_phone_number_format
from app.keyboards.inline import get_main_menu
from app.states.forms import AuthFSM
from datetime import date
import re


router = Router()


async def get_user_repo(session: AsyncSession) -> UserRepository:
    """Get user repository from session."""
    return UserRepository(session)


async def authenticate_user(user: User) -> bool:
    """Check if user is authenticated and verified."""
    if not user:
        raise AuthenticationError("کاربر یافت نشد", "شما دسترسی ندارید")
    
    if not user.is_verified:
        return False
    
    return True


@router.message(F.command("start"))
async def cmd_start(message: types.Message, state: FSMContext, session: AsyncSession):
    """Handle /start command - entry point for bot."""
    telegram_id = message.from_user.id
    user_repo = UserRepository(session)
    
    # Check if user exists and is verified
    user = await user_repo.get_by_telegram_id(telegram_id)
    
    if user and user.is_verified:
        # User already verified, show main menu
        welcome_msg = f"سلام {user.name}! 👋"
        await message.answer(
            welcome_msg,
            reply_markup=get_main_menu(user.role)
        )
        log_user_action(telegram_id, "start_verified", {"role": user.role.value})
    else:
        # Need phone verification
        await message.answer(
            "سلام! برای استفاده از ربات، لطفا شماره تلفن خود را وارد کنید.\n\n"
            "شکل صحیح: 09121234567",
            reply_markup=types.ReplyKeyboardMarkup(
                keyboard=[[types.KeyboardButton(text="📱 ارسال شماره تماس", request_contact=True)]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
        )
        await state.set_state("waiting_phone")
        log_user_action(telegram_id, "start_unverified", {})


@router.message(F.content_type(ContentType.CONTACT))
async def receive_contact(message: types.Message, state: FSMContext, session: AsyncSession):
    """Handle contact shared via keyboard."""
    phone_number = message.contact.phone_number if message.contact else None
    telegram_id = message.from_user.id
    first_name = message.from_user.first_name or "کاربر"
    
    if not phone_number:
        await message.answer("❌ شماره تماس دریافت نشد. لطفا دوباره تلاش کنید.")
        return
    
    # Format and validate phone
    phone_number = format_phone_number(phone_number)
    if not validate_phone_number_format(phone_number):
        await message.answer(
            "❌ شماره تماس نامعتبر است.\n\n"
            "لطفا یک شماره ایرانی معتبر وارد کنید (مثال: 09121234567)"
        )
        return
    
    user_repo = UserRepository(session)
    
    # Check if this phone is pre-registered in system
    existing_user = await user_repo.get_by_phone(phone_number)
    
    if not existing_user:
        # Phone not registered - access denied
        await message.answer(
            "❌ شموره تماس شما در سیستم ثبت نشده است.\n\n"
            "لطفا با پشتیبان تماس بگیرید.",
            reply_markup=types.ReplyKeyboardRemove()
        )
        log_user_action(telegram_id, "authentication_failed", {"phone": phone_number, "reason": "not_registered"})
        return
    
    # Check if this Telegram ID already has a different account
    existing_telegram_user = await user_repo.get_by_telegram_id(telegram_id)
    if existing_telegram_user and existing_telegram_user.id != existing_user.id:
        await message.answer(
            "❌ این تلگرام قبلا برای حسابی دیگر ثبت شده است.",
            reply_markup=types.ReplyKeyboardRemove()
        )
        log_user_action(
            telegram_id,
            "authentication_failed",
            {"reason": "telegram_already_registered", "existing_user_id": existing_telegram_user.id}
        )
        return
    
    # Verify the user
    user = existing_user
    if not user.is_verified:
        # Update Telegram ID if needed
        user.telegram_id = telegram_id
        
        # Verify user
        await user_repo.verify_user(user.id)
        await session.commit()
        
        success_msg = (
            f"✅ خوش آمدید {user.name}!\n\n"
            f"شما با موفقیت ثبت‌نام کردید.\n"
            f"نقش شما: {get_role_display(user.role)}"
        )
        await message.answer(
            success_msg,
            reply_markup=types.ReplyKeyboardRemove()
        )
        
        # Show main menu
        await message.answer(
            "چه کاری می‌تونم برای شما کنم؟",
            reply_markup=get_main_menu(user.role)
        )
        
        log_user_action(telegram_id, "user_verified", {"role": user.role.value, "phone": phone_number})
    else:
        # Already verified
        await message.answer(
            f"خوش آمدید دوباره {user.name}! 👋",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await message.answer(
            "چه کاری می‌تونم برای شما کنم؟",
            reply_markup=get_main_menu(user.role)
        )
        log_user_action(telegram_id, "user_already_verified", {"role": user.role.value})
    
    await state.clear()


@router.message(F.command("verify"))
async def cmd_verify(message: types.Message, state: FSMContext, session: AsyncSession):
    """Manual verification command (for testing)."""
    # In production, this would be restricted to admins
    await message.answer(
        "📱 لطفا شماره تلفن خود را با فرمت 09121234567 وارد کنید:"
    )
    await state.set_state("waiting_phone_verify")


@router.message(AuthFSM.waiting_phone_verify)
async def process_phone_verify(message: types.Message, state: FSMContext, session: AsyncSession):
    """Process manual phone verification."""
    phone_number = message.text
    
    if not phone_number or not validate_phone_number_format(phone_number):
        await message.answer(
            "❌ شماره تماس نامعتبر است.\n"
            "لطفا فرمت 09121234567 را استفاده کنید."
        )
        return
    
    user_repo = UserRepository(session)
    user = await user_repo.get_by_phone(phone_number)
    
    if not user:
        await message.answer("❌ این شماره در سیستم ثبت نشده است.")
        return
    
    if user.telegram_id != message.from_user.id:
        user.telegram_id = message.from_user.id
    
    await user_repo.verify_user(user.id)
    await session.commit()
    
    await message.answer(f"✅ شما با نام {user.name} تایید شدید.")
    await message.answer(
        "چه کاری می‌تونم برای شما کنم؟",
        reply_markup=get_main_menu(user.role)
    )
    await state.clear()


@router.message(F.command("logout"))
async def cmd_logout(message: types.Message, state: FSMContext):
    """Handle logout."""
    await state.clear()
    await message.answer(
        "👋 شما خارج شدید.",
        reply_markup=types.ReplyKeyboardRemove()
    )


def get_role_display(role: UserRole) -> str:
    """Get Persian display name for role."""
    role_names = {
        UserRole.INVESTOR: "سرمایه‌گذار",
        UserRole.ACCOUNTANT: "حسابدار",
        UserRole.ADMIN: "ادمین",
    }
    return role_names.get(role, "نامشخص")
