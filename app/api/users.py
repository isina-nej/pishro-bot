"""User API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import AsyncSessionLocal
from app.services.repositories import UserRepository
from app.api.schemas import (
    UserResponse, UserCreate, UserUpdate, APIResponse, 
    UserStats, UserRoleEnum
)
from typing import List

router = APIRouter(prefix="/api/v1/users", tags=["users"])


async def get_db():
    """Get database session."""
    async with AsyncSessionLocal() as session:
        yield session


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get all users with pagination."""
    repo = UserRepository(db)
    users = await repo.get_all(skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get specific user by ID."""
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/telegram/{telegram_id}", response_model=UserResponse)
async def get_user_by_telegram(
    telegram_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """Get user by Telegram ID."""
    repo = UserRepository(db)
    user = await repo.get_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/phone/{phone}", response_model=UserResponse)
async def get_user_by_phone(
    phone: str,
    db: AsyncSession = Depends(get_db)
):
    """Get user by phone number."""
    repo = UserRepository(db)
    user = await repo.get_by_phone(phone)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new user."""
    repo = UserRepository(db)
    
    # Check if phone already exists
    existing = await repo.get_by_phone(user.phone)
    if existing:
        raise HTTPException(status_code=400, detail="Phone already registered")
    
    new_user = await repo.create(user)
    return new_user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update user."""
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = await repo.update(user_id, user_update.model_dump(exclude_unset=True))
    return updated_user


@router.delete("/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Delete user."""
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await repo.delete(user_id)
    return APIResponse(success=True, message="User deleted successfully")


@router.get("/{user_id}/stats", response_model=UserStats)
async def get_user_stats(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get user statistics including investments and profit."""
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user investments stats
    stats = await repo.get_user_stats(user_id)
    return stats


@router.get("/role/{role}", response_model=List[UserResponse])
async def get_users_by_role(
    role: UserRoleEnum,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get users by role."""
    repo = UserRepository(db)
    users = await repo.get_by_role(role, skip=skip, limit=limit)
    return users
