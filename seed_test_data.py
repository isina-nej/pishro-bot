#!/usr/bin/env python3
"""Seed test data into the database."""

import asyncio
import sys
import os
from datetime import datetime, date, timedelta

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete

from app.models.models import User, Investment, Transaction, UserRole, ContractType, TransactionType, InvestmentStatus
from app.config import settings

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def seed_data():
    """Seed test data into the database."""
    
    database_url = settings.DATABASE_URL
    
    # Create engine
    engine = create_async_engine(database_url, echo=False)
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            # Clear existing data
            logger.info("🗑️  Clearing existing data...")
            await session.execute(delete(Transaction))
            await session.execute(delete(Investment))
            await session.execute(delete(User))
            await session.commit()
            
            # Create test users
            logger.info("👥 Creating test users...")
            
            users = [
                User(
                    telegram_id=1399836575,
                    name="مدیر سیستم",
                    phone_number="09100000000",
                    role=UserRole.ADMIN,
                    is_verified=True,
                ),
                User(
                    telegram_id=1399836576,
                    name="علی کیانیان",
                    phone_number="09121234567",
                    role=UserRole.INVESTOR,
                    is_verified=True,
                ),
                User(
                    telegram_id=1399836577,
                    name="سینا احمدی",
                    phone_number="09129876543",
                    role=UserRole.ACCOUNTANT,
                    is_verified=True,
                ),
                User(
                    telegram_id=1399836578,
                    name="محمد رضا صادقی",
                    phone_number="09131111111",
                    role=UserRole.INVESTOR,
                    is_verified=True,
                ),
                User(
                    telegram_id=1399836579,
                    name="فاطمه حسینی",
                    phone_number="09135555555",
                    role=UserRole.INVESTOR,
                    is_verified=True,
                ),
            ]
            
            session.add_all(users)
            await session.commit()
            logger.info(f"✅ Created {len(users)} users")
            
            # Get investor users
            result = await session.execute(
                select(User).where(User.role == UserRole.INVESTOR)
            )
            investors = result.scalars().all()
            
            # Get accountant for recording transactions
            result_acc = await session.execute(
                select(User).where(User.role == UserRole.ACCOUNTANT)
            )
            accountant = result_acc.scalars().first()
            
            # Create test investments
            logger.info("💼 Creating test investments...")
            
            investments = []
            contract_types = [ContractType.FIXED_RATE, ContractType.VARIABLE_HOLDING]
            
            for idx, investor in enumerate(investors):
                for i, contract_type in enumerate(contract_types):
                    start_date = date.today() - timedelta(days=90 - (i * 30))
                    
                    inv = Investment(
                        user_id=investor.id,
                        contract_type=contract_type,
                        initial_amount=(i + 2) * 1_000_000,  # 2M, 3M Toman
                        start_date=start_date,
                        dividend_rate=0.08 if contract_type == ContractType.FIXED_RATE else None,
                        holding_period_months=12 if contract_type == ContractType.VARIABLE_HOLDING else None,
                        status=InvestmentStatus.ACTIVE,
                    )
                    investments.append(inv)
            
            session.add_all(investments)
            await session.commit()
            logger.info(f"✅ Created {len(investments)} investments")
            
            # Create test transactions
            logger.info("💳 Creating test transactions...")
            
            transactions = []
            
            if accountant:
                for investment in investments:
                    # Initial deposit
                    txn1 = Transaction(
                        investment_id=investment.id,
                        type=TransactionType.DEPOSIT,
                        amount=investment.initial_amount,
                        transaction_date=investment.start_date,
                        description=f"واریز اولیهٔ سرمایه‌گذاری",
                        recorded_by=accountant.id,
                    )
                    transactions.append(txn1)
                    
                    # Monthly dividend transactions (if fixed rate)
                    if investment.contract_type == ContractType.FIXED_RATE and investment.dividend_rate:
                        for month in range(1, 4):
                            dividend_amount = investment.initial_amount * investment.dividend_rate
                            txn = Transaction(
                                investment_id=investment.id,
                                type=TransactionType.DIVIDEND,
                                amount=dividend_amount,
                                transaction_date=investment.start_date + timedelta(days=30 * month),
                                description=f"سود ماهیانهٔ ماه {month}",
                                recorded_by=accountant.id,
                            )
                            transactions.append(txn)
                
                session.add_all(transactions)
                await session.commit()
                logger.info(f"✅ Created {len(transactions)} transactions")
            
            # Print summary
            print("\n" + "="*70)
            print("📊 خلاصهٔ دادهٔ تستی:")
            print("="*70)
            print(f"👥 کاربران: {len(users)}")
            for user in users:
                role_fa = {
                    UserRole.ADMIN: "👑 مدیر",
                    UserRole.INVESTOR: "💰 سرمایه‌گذار",
                    UserRole.ACCOUNTANT: "💼 حسابدار",
                }.get(user.role, str(user.role))
                print(f"  • {user.name} ({role_fa}) - {user.phone_number}")
            
            print(f"\n💼 سرمایه‌گذاری‌ها: {len(investments)}")
            for i, inv in enumerate(investments):
                if i == 5:
                    print(f"  ... و {len(investments) - 5} مورد دیگر")
                    break
                contract_type_fa = {
                    ContractType.FIXED_RATE: "سود ثابت ۸٪ ماهیانه",
                    ContractType.VARIABLE_HOLDING: "نگهداری متغیر",
                }.get(inv.contract_type, str(inv.contract_type))
                print(f"  • {contract_type_fa}")
                print(f"    مبلغ: {inv.initial_amount:,.0f} تومان | شروع: {inv.start_date}")
            
            print(f"\n💳 تراکنش‌ها: {len(transactions)}")
            print("="*70 + "\n")
            
            logger.info("✅ دادهٔ تستی با موفقیت ایجاد شد!")
            
        except Exception as e:
            logger.error(f"❌ خطا: {e}", exc_info=True)
            await session.rollback()
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_data())
