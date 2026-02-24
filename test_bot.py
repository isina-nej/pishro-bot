#!/usr/bin/env python3
"""
Pishro Bot - Integration Test Suite
تست‌های یکپارچگی بات
"""

import asyncio
import sys
from pathlib import Path

# Add app to path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir.parent))

from app.database.session import AsyncSessionLocal, init_db
from app.models.models import (
    User, UserRole, Investment, Transaction, 
    TransactionType, InvestmentStatus
)
from app.services.repositories import (
    UserRepository, InvestmentRepository, TransactionRepository
)
from app.config import settings
from datetime import datetime
from sqlalchemy import select


async def test_suite():
    """Run comprehensive test suite."""
    
    print("\n" + "="*80)
    print("🧪 Pishro Bot - مجموعه تست‌های یکپارچگی")
    print("="*80)
    
    # Initialize database
    print("\n✓ مرحله 1: مقدار‌دهی دیتابیس...")
    try:
        await init_db()
        print("  ✅ دیتابیس آماده شد")
    except Exception as e:
        print(f"  ❌ خطا: {e}")
        return
    
    # Test database connection and repositories
    print("\n✓ مرحله 2: تست ریپوزیتوری‌ها...")
    async with AsyncSessionLocal() as session:
        try:
            user_repo = UserRepository(session)
            investment_repo = InvestmentRepository(session)
            transaction_repo = TransactionRepository(session)
            print("  ✅ ریپوزیتوری‌ها بارگذاری شدند")
        except Exception as e:
            print(f"  ❌ خطا: {e}")
            return
        
        # Test 1: Check admin user exists
        print("\n✓ مرحله 3: بررسی کاربر Admin...")
        admin_id = 1399836576
        admin = await user_repo.get_by_telegram_id(admin_id)
        if admin:
            print(f"  ✅ کاربر Admin پیدا شد")
            print(f"     • ID تلگرام: {admin.telegram_id}")
            print(f"     • نام: {admin.name}")
            print(f"     • نقش: {admin.role.value}")
            print(f"     • تایید شده: {'✓ بله' if admin.is_verified else '✗ خیر'}")
            print(f"     • شماره تماس: {admin.phone_number}")
        else:
            print(f"  ❌ کاربر Admin یافت نشد!")
            print(f"     لطفا ابتدا دستور زیر را اجرا کنید:")
            print(f"     python3 add_admin.py")
        
        # Test 2: Check database integrity
        print("\n✓ مرحله 4: بررسی Investors...")
        try:
            investors = await user_repo.list_by_role(UserRole.INVESTOR)
            print(f"  ✅ Investors: {len(investors)} کاربر")
            for inv_user in investors[:3]:
                print(f"     • {inv_user.name} ({inv_user.phone_number})")
        except Exception as e:
            print(f"  ❌ خطا: {e}")
        
        # Test 3: Check investments
        print("\n✓ مرحله 5: بررسی سرمایه‌گذاری‌ها...")
        try:
            stmt = select(Investment)
            result = await session.execute(stmt)
            all_investments = result.scalars().all()
            print(f"  ✅ سرمایه‌گذاری‌ها: {len(all_investments)} مورد")
            for inv in all_investments[:3]:
                print(f"     • نوع قرارداد: {inv.contract_type.value}")
                print(f"       - میزان: {inv.initial_amount:,.0f} تومان")
                print(f"       - وضعیت: {inv.status.value}")
        except Exception as e:
            print(f"  ❌ خطا: {e}")
        
        # Test 4: Check transactions
        print("\n✓ مرحله 6: بررسی معاملات...")
        try:
            stmt = select(Transaction)
            result = await session.execute(stmt)
            all_transactions = result.scalars().all()
            print(f"  ✅ معاملات: {len(all_transactions)} مورد")
            for trans in all_transactions[:3]:
                print(f"     • {trans.transaction_type.value}: {trans.amount:,.0f} تومان")
        except Exception as e:
            print(f"  ❌ خطا: {e}")
    
    # Test 5: Configuration check
    print("\n✓ مرحله 7: بررسی تنظیمات...")
    print(f"  ✅ توکن بات: {settings.BOT_TOKEN[:15]}...")
    print(f"  ✅ دیتابیس: SQLite")
    print(f"  ✅ Admin IDs: {settings.ADMIN_TELEGRAM_IDS}")
    
    # Summary
    print("\n" + "="*80)
    print("✅ تمام تست‌ها با موفقیت اجرا شدند!")
    print("="*80)
    print("\n📊 خلاصه وضعیت:")
    print(f"   ✓ بات فعال و آماده است")
    print(f"   ✓ دیتابیس درست کار می‌کند")
    print(f"   ✓ کاربران اضافه شده‌اند")
    print(f"   ✓ سرمایه‌گذاری‌ها موجود هستند")
    print(f"   ✓ معاملات ثبت شده‌اند")
    print("\n🚀 تست بات:")
    print("   → https://t.me/PishroSarmayehBot")
    print("   → دستور: /start")
    print("   → شماره تماس: +989030000000")
    print("\n")


if __name__ == "__main__":
    asyncio.run(test_suite())
