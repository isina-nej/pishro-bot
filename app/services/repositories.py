from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.orm import joinedload
from app.models.models import (
    User, Investment, Transaction, Valuation,
    UserRole, ContractType, TransactionType, InvestmentStatus
)
from typing import Optional, List, Tuple
from datetime import date


class UserRepository:
    """User database operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID."""
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()
    
    async def get_by_phone(self, phone_number: str) -> Optional[User]:
        """Get user by phone number."""
        stmt = select(User).where(User.phone_number == phone_number)
        result = await self.session.execute(stmt)
        return result.scalars().first()
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return await self.session.get(User, user_id)
    
    async def create(self, telegram_id: int, phone_number: str, name: str, 
                    role: UserRole = UserRole.INVESTOR) -> User:
        """Create new user."""
        user = User(
            telegram_id=telegram_id,
            phone_number=phone_number,
            name=name,
            role=role,
            is_verified=False
        )
        self.session.add(user)
        await self.session.flush()
        return user
    
    async def verify_user(self, user_id: int) -> User:
        """Mark user as verified."""
        user = await self.get_by_id(user_id)
        if user:
            user.is_verified = True
            user.verified_at = func.now()
            await self.session.flush()
        return user
    
    async def update_role(self, user_id: int, role: UserRole) -> User:
        """Update user role."""
        user = await self.get_by_id(user_id)
        if user:
            user.role = role
            await self.session.flush()
        return user
    
    async def list_by_role(self, role: UserRole) -> List[User]:
        """Get all users with specific role."""
        stmt = select(User).where(User.role == role).order_by(User.name)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_all(self, skip: int = 0, limit: int = 10) -> List[User]:
        """Get all users with pagination."""
        stmt = select(User).order_by(User.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def search_by_name_or_phone(self, query: str) -> List[User]:
        """Search users by name or phone number."""
        search_term = f"%{query}%"
        stmt = select(User).where(
            or_(
                User.name.ilike(search_term),
                User.phone_number.ilike(search_term)
            )
        ).order_by(User.name).limit(20)
        result = await self.session.execute(stmt)
        return result.scalars().all()


class InvestmentRepository:
    """Investment database operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, investment_id: int) -> Optional[Investment]:
        """Get investment by ID with related data."""
        stmt = select(Investment).where(Investment.id == investment_id).options(
            joinedload(Investment.transactions),
            joinedload(Investment.valuations)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
    
    async def get_by_user(self, user_id: int) -> List[Investment]:
        """Get all investments for a user."""
        stmt = select(Investment).where(
            Investment.user_id == user_id
        ).options(
            joinedload(Investment.transactions),
            joinedload(Investment.valuations)
        ).order_by(Investment.start_date.desc())
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()
    
    async def get_all(self, skip: int = 0, limit: int = 10) -> List[Investment]:
        """Get all investments with pagination."""
        stmt = select(Investment).order_by(Investment.start_date.desc()).offset(skip).limit(limit).options(
            joinedload(Investment.transactions),
            joinedload(Investment.valuations)
        )
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()
    
    async def create(self, user_id: int, contract_type: ContractType, 
                    initial_amount: float, start_date: date,
                    dividend_rate: float = None,
                    holding_period_months: int = None) -> Investment:
        """Create new investment contract."""
        investment = Investment(
            user_id=user_id,
            contract_type=contract_type,
            initial_amount=initial_amount,
            start_date=start_date,
            dividend_rate=dividend_rate,
            holding_period_months=holding_period_months
        )
        self.session.add(investment)
        await self.session.flush()
        return investment
    
    async def update_status(self, investment_id: int, status: InvestmentStatus,
                          cancelled_date: date = None) -> Investment:
        """Update investment status."""
        investment = await self.get_by_id(investment_id)
        if investment:
            investment.status = status
            if cancelled_date:
                investment.cancelled_date = cancelled_date
            await self.session.flush()
        return investment


class TransactionRepository:
    """Transaction (ledger) database operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """Get transaction by ID."""
        stmt = select(Transaction).where(Transaction.id == transaction_id).options(
            joinedload(Transaction.recorder)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
    
    async def get_by_investment(self, investment_id: int,
                               limit: int = None) -> List[Transaction]:
        """Get all transactions for an investment (ordered by date DESC)."""
        stmt = select(Transaction).where(
            Transaction.investment_id == investment_id
        ).options(
            joinedload(Transaction.recorder)
        ).order_by(Transaction.transaction_date.desc())
        
        if limit:
            stmt = stmt.limit(limit)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_all(self, skip: int = 0, limit: int = 10) -> List[Transaction]:
        """Get all transactions with pagination."""
        stmt = select(Transaction).order_by(Transaction.transaction_date.desc()).offset(skip).limit(limit).options(
            joinedload(Transaction.recorder)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def create(self, investment_id: int, txn_type: TransactionType,
                    amount: float, transaction_date: date,
                    recorded_by: int, description: str = None) -> Transaction:
        """Create new transaction."""
        transaction = Transaction(
            investment_id=investment_id,
            type=txn_type,
            amount=amount,
            transaction_date=transaction_date,
            recorded_by=recorded_by,
            description=description
        )
        self.session.add(transaction)
        await self.session.flush()
        return transaction
    
    async def update(self, transaction_id: int, amount: float = None,
                    transaction_date: date = None,
                    description: str = None) -> Transaction:
        """Update transaction."""
        transaction = await self.get_by_id(transaction_id)
        if transaction:
            if amount is not None:
                transaction.amount = amount
            if transaction_date is not None:
                transaction.transaction_date = transaction_date
            if description is not None:
                transaction.description = description
            await self.session.flush()
        return transaction
    
    async def get_by_type(self, investment_id: int, txn_type: TransactionType) -> List[Transaction]:
        """Get transactions of specific type."""
        stmt = select(Transaction).where(
            and_(
                Transaction.investment_id == investment_id,
                Transaction.type == txn_type
            )
        ).order_by(Transaction.transaction_date.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()


class ValuationRepository:
    """Portfolio valuation database operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, valuation_id: int) -> Optional[Valuation]:
        """Get valuation by ID."""
        stmt = select(Valuation).where(Valuation.id == valuation_id).options(
            joinedload(Valuation.updater)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
    
    async def get_latest_by_investment(self, investment_id: int) -> Optional[Valuation]:
        """Get latest valuation for an investment."""
        stmt = select(Valuation).where(
            Valuation.investment_id == investment_id
        ).order_by(Valuation.valuation_date.desc()).limit(1).options(
            joinedload(Valuation.updater)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
    
    async def get_history_by_investment(self, investment_id: int, limit: int = 20) -> List[Valuation]:
        """Get valuation history for an investment."""
        stmt = select(Valuation).where(
            Valuation.investment_id == investment_id
        ).order_by(Valuation.valuation_date.desc()).limit(limit).options(
            joinedload(Valuation.updater)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def create(self, investment_id: int, new_value: float,
                    valuation_date: date, updated_by: int,
                    old_value: float = None,
                    profit_percentage: float = None,
                    reason: str = None) -> Valuation:
        """Create new valuation record."""
        valuation = Valuation(
            investment_id=investment_id,
            old_value=old_value,
            new_value=new_value,
            profit_percentage=profit_percentage,
            valuation_date=valuation_date,
            updated_by=updated_by,
            reason=reason
        )
        self.session.add(valuation)
        await self.session.flush()
        return valuation
    
    async def get_overdue_investments(self, days_threshold: int = 30) -> List[Investment]:
        """Get investments with valuations older than threshold."""
        # Subquery for latest valuation date per investment
        subquery = select(
            func.max(Valuation.valuation_date).label("latest_date")
        ).group_by(Valuation.investment_id).subquery()
        
        stmt = select(Investment).where(
            and_(
                Investment.status == InvestmentStatus.ACTIVE
            )
        ).order_by(Investment.updated_at.desc())
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
