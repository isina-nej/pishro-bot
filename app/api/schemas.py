"""Pydantic schemas for API responses and requests."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# Enums
class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    ACCOUNTANT = "accountant"
    INVESTOR = "investor"


class InvestmentTypeEnum(str, Enum):
    FIXED_RATE = "fixed_rate"
    PERCENTAGE = "percentage"
    COMPOUND = "compound"


class TransactionTypeEnum(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    PROFIT = "profit"
    REFUND = "refund"


# Base Models
class UserBase(BaseModel):
    name: str
    phone_number: str
    role: UserRoleEnum
    is_verified: bool = False


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    role: Optional[UserRoleEnum] = None


class UserResponse(UserBase):
    id: int
    telegram_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Investment Models
class InvestmentBase(BaseModel):
    user_id: int
    contract_type: str
    initial_amount: float
    start_date: datetime
    dividend_rate: Optional[float] = None
    holding_period_months: Optional[int] = None


class InvestmentCreate(InvestmentBase):
    pass


class InvestmentUpdate(BaseModel):
    contract_type: Optional[str] = None
    dividend_rate: Optional[float] = None
    holding_period_months: Optional[int] = None


class InvestmentResponse(InvestmentBase):
    id: int
    status: str
    cancelled_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Transaction Models
class TransactionBase(BaseModel):
    investment_id: int
    type: str
    amount: float
    transaction_date: datetime
    description: Optional[str] = None
    recorded_by: int


class TransactionCreate(TransactionBase):
    pass


class TransactionResponse(TransactionBase):
    id: int
    recorded_at: datetime

    class Config:
        from_attributes = True


# Valuation Models
class ValuationBase(BaseModel):
    investment_id: int
    new_value: float
    valuation_date: datetime
    reason: Optional[str] = None
    updated_by: int


class ValuationCreate(ValuationBase):
    pass


class ValuationResponse(ValuationBase):
    id: int
    old_value: Optional[float] = None
    profit_percentage: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Dashboard Models
class DashboardStats(BaseModel):
    total_investments: int
    total_capital: float
    total_profit: float
    average_roi: float


class UserStats(BaseModel):
    total_investments: int
    total_invested: float
    total_profit: float
    total_roi: float
    average_roi: float


# Generic Response
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
    error: Optional[str] = None


class PaginatedResponse(BaseModel):
    total: int
    page: int
    limit: int
    data: List[dict]
