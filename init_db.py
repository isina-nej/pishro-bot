#!/usr/bin/env python3
"""Database initialization script - create tables and seed test data."""

import asyncio
import sys
from pathlib import Path

# Add app to path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir.parent))

from app.database.session import AsyncSessionLocal, engine, Base
from app.models.models import User, Investment, UserRole, ContractType, TransactionType, Transaction
from datetime import date
import jdatetime


async def init_database():
    """Initialize database and create tables."""
    print("🗑️  Dropping existing tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("✅ Tables dropped!\n")
    
    print("🔧 Creating new database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created successfully!")
    
    print("\n📝 Adding seed data (test users)...")
    
    async with AsyncSessionLocal() as session:
        try:
            # Check if test data already exists
            from sqlalchemy import select
            existing_users = await session.execute(select(User).limit(1))
            if existing_users.scalars().first():
                print("⚠️ Test data already exists. Skipping...")
                return
            
            # Create admin user
            admin = User(
                telegram_id=123456789,
                phone_number="09121234567",
                name="دکتر ایرج (مدیر)",
                role=UserRole.ADMIN,
                is_verified=True
            )
            session.add(admin)
            await session.flush()
            
            # Create accountant user
            accountant = User(
                telegram_id=987654321,
                phone_number="09129876543",
                name="حسابدار شرکت",
                role=UserRole.ACCOUNTANT,
                is_verified=True
            )
            session.add(accountant)
            await session.flush()
            
            # Create sample investor
            investor = User(
                telegram_id=111111111,
                phone_number="09121111111",
                name="احمد علی",
                role=UserRole.INVESTOR,
                is_verified=True
            )
            session.add(investor)
            await session.flush()
            
            # Create sample investment
            today = date.today()
            investment = Investment(
                user_id=investor.id,
                contract_type=ContractType.FIXED_RATE,
                initial_amount=1_000_000_000,
                start_date=date(today.year, today.month, 1),
                dividend_rate=0.08  # 8% monthly
            )
            session.add(investment)
            
            await session.commit()
            
            print("\n✅ Seed data added successfully!")
            print("\n📋 Test Credentials:")
            print("━" * 50)
            print("Admin:")
            print(f"  Telegram ID: 123456789")
            print(f"  Phone: 09121234567")
            print(f"  Name: دکتر ایرج (مدیر)")
            print("\nAccountant:")
            print(f"  Telegram ID: 987654321")
            print(f"  Phone: 09129876543")
            print(f"  Name: حسابدار شرکت")
            print("\nInvestor:")
            print(f"  Telegram ID: 111111111")
            print(f"  Phone: 09121111111")
            print(f"  Name: احمد علی")
            print("━" * 50)
            
        except Exception as e:
            print(f"❌ Error adding seed data: {e}")
            await session.rollback()
            raise


async def main():
    """Main entry point."""
    try:
        print("🚀 Pishro Investment Bot - Database Initialization\n")
        
        # Check environment
        from app.config import settings
        print(f"📊 Database URL: {settings.DATABASE_URL}")
        
        await init_database()
        
        print("\n" + "=" * 50)
        print("✅ Database initialization complete!")
        print("=" * 50)
        print("\n📖 Next steps:")
        print("1. Update .env file with Telegram Bot token")
        print("2. Update BOT_TOKEN in .env")
        print("3. Run: python run_bot.py")
        print("4. Test with one of the test credentials above")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
