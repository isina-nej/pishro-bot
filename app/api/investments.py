"""Investment API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import AsyncSessionLocal
from app.services.repositories import InvestmentRepository
from app.api.schemas import (
    InvestmentResponse, InvestmentCreate, InvestmentUpdate, 
    APIResponse
)
from typing import List

router = APIRouter(prefix="/api/v1/investments", tags=["investments"])


async def get_db():
    """Get database session."""
    async with AsyncSessionLocal() as session:
        yield session


@router.get("/", response_model=List[InvestmentResponse])
async def list_investments(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    investor_id: int = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get all investments with optional filtering."""
    repo = InvestmentRepository(db)
    
    if investor_id:
        investments = await repo.get_by_investor(investor_id, skip=skip, limit=limit)
    else:
        investments = await repo.get_all(skip=skip, limit=limit)
    
    return investments


@router.get("/{investment_id}", response_model=InvestmentResponse)
async def get_investment(
    investment_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get specific investment."""
    repo = InvestmentRepository(db)
    investment = await repo.get_by_id(investment_id)
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    return investment


@router.post("/", response_model=InvestmentResponse)
async def create_investment(
    investment: InvestmentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new investment."""
    repo = InvestmentRepository(db)
    new_investment = await repo.create(investment)
    return new_investment


@router.put("/{investment_id}", response_model=InvestmentResponse)
async def update_investment(
    investment_id: int,
    investment_update: InvestmentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update investment."""
    repo = InvestmentRepository(db)
    investment = await repo.get_by_id(investment_id)
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    
    updated = await repo.update(investment_id, investment_update.model_dump(exclude_unset=True))
    return updated


@router.delete("/{investment_id}")
async def delete_investment(
    investment_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete investment."""
    repo = InvestmentRepository(db)
    investment = await repo.get_by_id(investment_id)
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    
    await repo.delete(investment_id)
    return APIResponse(success=True, message="Investment deleted successfully")


@router.get("/{investment_id}/details", response_model=dict)
async def get_investment_details(
    investment_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed investment information."""
    repo = InvestmentRepository(db)
    investment = await repo.get_by_id(investment_id)
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    
    # Calculate current value and profit
    current_value = investment.current_value
    profit = current_value - investment.initial_amount
    roi = (profit / investment.initial_amount * 100) if investment.initial_amount > 0 else 0
    
    return {
        **investment.__dict__,
        "current_value": current_value,
        "profit": profit,
        "roi_percentage": roi,
        "investor": investment.investor.name if investment.investor else None
    }
