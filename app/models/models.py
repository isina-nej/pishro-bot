from datetime import datetime
from typing import Optional
from enum import Enum
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, 
    ForeignKey, Enum as SQLEnum, Text, Date, Index
)
from sqlalchemy.orm import relationship
from app.database.session import Base


class UserRole(str, Enum):
    """User roles in the system."""
    INVESTOR = "investor"
    ACCOUNTANT = "accountant"
    ADMIN = "admin"


class ContractType(str, Enum):
    """Investment contract types."""
    FIXED_RATE = "fixed_rate"  # 8% monthly fixed
    VARIABLE_HOLDING = "variable_holding"  # Variable periodic holding


class TransactionType(str, Enum):
    """Types of financial transactions."""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    DIVIDEND = "dividend"
    CANCELLATION = "cancellation"


class InvestmentStatus(str, Enum):
    """Status of investment contracts."""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"


class User(Base):
    """User model for investors, accountants, and admins."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.INVESTOR)
    is_verified = Column(Boolean, default=False, nullable=False)
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    investments = relationship("Investment", back_populates="user", cascade="all, delete-orphan")
    transactions_recorded = relationship(
        "Transaction", 
        foreign_keys="Transaction.recorded_by", 
        back_populates="recorder"
    )
    valuations_updated = relationship(
        "Valuation",
        foreign_keys="Valuation.updated_by",
        back_populates="updater"
    )
    
    __table_args__ = (
        Index("idx_telegram_id", "telegram_id"),
        Index("idx_phone_number", "phone_number"),
        Index("idx_role", "role"),
    )


class Investment(Base):
    """Investment contract model."""
    __tablename__ = "investments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    contract_type = Column(SQLEnum(ContractType), nullable=False)
    initial_amount = Column(Float, nullable=False)  # Initial capital in Toman
    start_date = Column(Date, nullable=False)
    dividend_rate = Column(Float, nullable=True)  # 0.08 for 8% monthly (fixed_rate only)
    holding_period_months = Column(Integer, nullable=True)  # For variable_holding
    status = Column(SQLEnum(InvestmentStatus), default=InvestmentStatus.ACTIVE, nullable=False)
    cancelled_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="investments")
    transactions = relationship("Transaction", back_populates="investment", cascade="all, delete-orphan")
    valuations = relationship("Valuation", back_populates="investment", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_status", "status"),
    )


class Transaction(Base):
    """Financial transaction ledger (deposit, withdrawal, dividend, cancellation)."""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    investment_id = Column(Integer, ForeignKey("investments.id", ondelete="CASCADE"), nullable=False)
    type = Column(SQLEnum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)  # Can be negative for withdrawals
    transaction_date = Column(Date, nullable=False)  # Gregorian date stored; display as Jalali
    description = Column(Text, nullable=True)
    recorded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    investment = relationship("Investment", back_populates="transactions")
    recorder = relationship("User", foreign_keys=[recorded_by], back_populates="transactions_recorded")
    
    __table_args__ = (
        Index("idx_investment_id", "investment_id"),
        Index("idx_transaction_date", "transaction_date"),
        Index("idx_type", "type"),
    )


class Valuation(Base):
    """Portfolio valuation updates (for variable holding contracts and manual overrides)."""
    __tablename__ = "valuations"

    id = Column(Integer, primary_key=True, index=True)
    investment_id = Column(Integer, ForeignKey("investments.id", ondelete="CASCADE"), nullable=False)
    old_value = Column(Float, nullable=True)  # Previous portfolio value in Toman
    new_value = Column(Float, nullable=False)  # New portfolio value in Toman
    profit_percentage = Column(Float, nullable=True)  # If set via percentage
    valuation_date = Column(Date, nullable=False)
    reason = Column(Text, nullable=True)  # Optional description
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    investment = relationship("Investment", back_populates="valuations")
    updater = relationship("User", foreign_keys=[updated_by], back_populates="valuations_updated")
    
    __table_args__ = (
        Index("idx_valuation_investment_id", "investment_id"),
        Index("idx_valuation_date", "valuation_date"),
    )
