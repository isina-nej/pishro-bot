#!/usr/bin/env python3
"""اضافه کردن کاربر Admin جدید به دیتابیس"""

import asyncio
import sys
from dotenv import load_dotenv
from app.database.session import AsyncSessionLocal, init_db
from app.models.models import User
from app.services.repositories import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession

load_dotenv()

async def add_admin_user():
    """اضافه کردن کاربر Admin جدید"""
    
    # Initialize database
    await init_db()
    
    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)
        
        # چک کردن اگر کاربر قبلا وجود دارد
        existing_user = await user_repo.get_by_telegram_id(1399836576)
        if existing_user:
            print(f"✅ کاربر '{existing_user.username}' قبلا به عنوان {existing_user.role} وجود دارد")
            return
        
        # ایجاد کاربر جدید
        new_user = User(
            telegram_id=1399836576,
            name="سینا صادقی (مدیر)",
            phone_number="+989030000000",
            role="admin",
            is_verified=True
        )
        
        session.add(new_user)
        await session.commit()
        
        print(f"""
✅ کاربر Admin اضافه شد!

📋 جزئیات:
   ID تلگرام: 1399836576
   نام کاربری: SinaAdmin
   نقش: Admin
   وضعیت: تایید شده ✓
   شماره موبایل: 09120000000

🚀 الان می‌تونی به بات رفتی و با /start شروع کنی!
        """)

if __name__ == "__main__":
    asyncio.run(add_admin_user())
