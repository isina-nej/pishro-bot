"""Transaction API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import AsyncSessionLocal
from app.services.repositories import TransactionRepository
from app.api.schemas import (
    TransactionResponse, TransactionCreate, APIResponse
)
from typing import List

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])


async def get_db():
    """Get database session."""
    async with AsyncSessionLocal() as session:
        yield session


@router.get("/", response_model=List[TransactionResponse])
async def list_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    investment_id: int = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get all transactions with optional filtering."""
    repo = TransactionRepository(db)
    
    if investment_id:
        transactions = await repo.get_by_investment(investment_id, skip=skip, limit=limit)
    else:
        transactions = await repo.get_all(skip=skip, limit=limit)
    
    return transactions


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get specific transaction."""
    repo = TransactionRepository(db)
    transaction = await repo.get_by_id(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.post("/", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new transaction."""
    repo = TransactionRepository(db)
    new_transaction = await repo.create(transaction)
    return new_transaction


@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete transaction."""
    repo = TransactionRepository(db)
    transaction = await repo.get_by_id(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    await repo.delete(transaction_id)
    return APIResponse(success=True, message="Transaction deleted successfully")
