from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime, timedelta
from app.models.models import Investment, Transaction, Valuation, InvestmentStatus, TransactionType
from app.services.repositories import (
    InvestmentRepository, TransactionRepository, ValuationRepository
)
from app.utils.formatters import calculate_portfolio_balance, calculate_profit_percentage
from typing import Dict, Tuple, Optional, List


class PortfolioService:
    """Business logic for portfolio calculations."""
    
    def __init__(self, session: AsyncSession):
        self.investment_repo = InvestmentRepository(session)
        self.transaction_repo = TransactionRepository(session)
        self.valuation_repo = ValuationRepository(session)
    
    async def get_portfolio_summary(self, investment_id: int) -> Dict:
        """Get complete portfolio summary for an investment.
        
        Returns:
            Dict with keys:
                - initial_capital: Initial investment
                - current_deposits: Sum of all deposits
                - current_withdrawals: Sum of all withdrawals
                - total_transactions_profit: Sum of all dividends
                - current_value: Latest portfolio value
                - profit_percentage: Calculated profit %
                - last_updated: Date of last update
                - contract_type: Investment contract type
        """
        investment = await self.investment_repo.get_by_id(investment_id)
        if not investment:
            return {}
        
        # Get all transactions
        transactions = await self.transaction_repo.get_by_investment(investment_id)
        
        # Calculate sums by transaction type
        deposits = sum(t.amount for t in transactions if t.type == TransactionType.DEPOSIT)
        withdrawals = sum(abs(t.amount) for t in transactions if t.type == TransactionType.WITHDRAWAL)
        profits = sum(t.amount for t in transactions if t.type == TransactionType.DIVIDEND)
        
        # Get latest valuation
        latest_valuation = await self.valuation_repo.get_latest_by_investment(investment_id)
        
        # Calculate current value
        if latest_valuation:
            current_value = latest_valuation.new_value
            last_updated = latest_valuation.valuation_date
        else:
            # Default calculation: initial + deposits - withdrawals + profits
            current_value = investment.initial_amount + deposits - withdrawals + profits
            # Use latest transaction date or start date
            if transactions:
                last_updated = max(t.transaction_date for t in transactions)
            else:
                last_updated = investment.start_date
        
        return {
            "initial_capital": investment.initial_amount,
            "current_deposits": deposits,
            "current_withdrawals": withdrawals,
            "total_transactions_profit": profits,
            "current_value": current_value,
            "profit_percentage": calculate_profit_percentage(
                investment.initial_amount, current_value
            ),
            "last_updated": last_updated,
            "contract_type": investment.contract_type,
            "status": investment.status,
        }
    
    async def calculate_balance_for_date(self, investment_id: int, as_of_date: date) -> float:
        """Calculate portfolio balance as of a specific date."""
        investment = await self.investment_repo.get_by_id(investment_id)
        if not investment:
            return 0
        
        # Get all transactions up to date
        transactions = await self.transaction_repo.get_by_investment(investment_id)
        relevant_txns = [t for t in transactions if t.transaction_date <= as_of_date]
        
        # Sum amounts
        total_amount = investment.initial_amount + sum(t.amount for t in relevant_txns)
        
        return total_amount
    
    async def record_transaction(self, investment_id: int, txn_type: TransactionType,
                                amount: float, transaction_date: date,
                                recorded_by: int, description: str = None) -> Transaction:
        """Record a financial transaction."""
        return await self.transaction_repo.create(
            investment_id=investment_id,
            txn_type=txn_type,
            amount=amount,
            transaction_date=transaction_date,
            recorded_by=recorded_by,
            description=description
        )
    
    async def update_valuation(self, investment_id: int, new_value: float,
                              valuation_date: date, updated_by: int,
                              reason: str = None) -> Valuation:
        """Update portfolio valuation (admin only)."""
        investment = await self.investment_repo.get_by_id(investment_id)
        if not investment:
            return None
        
        # Get current/old value
        old_valuation = await self.valuation_repo.get_latest_by_investment(investment_id)
        old_value = old_valuation.new_value if old_valuation else investment.initial_amount
        
        # Create new valuation record
        valuation = await self.valuation_repo.create(
            investment_id=investment_id,
            new_value=new_value,
            valuation_date=valuation_date,
            updated_by=updated_by,
            old_value=old_value,
            reason=reason
        )
        
        return valuation
    
    async def get_transaction_history(self, investment_id: int, 
                                     limit: int = 20, offset: int = 0) -> Tuple[List[Transaction], int]:
        """Get paginated transaction history."""
        all_transactions = await self.transaction_repo.get_by_investment(investment_id)
        total_count = len(all_transactions)
        
        # Apply pagination
        paginated = all_transactions[offset:offset + limit]
        
        return paginated, total_count
    
    async def get_valuation_history(self, investment_id: int, limit: int = 20) -> List[Valuation]:
        """Get valuation change history."""
        return await self.valuation_repo.get_history_by_investment(investment_id, limit)


class NotificationService:
    """Service for sending notifications to investors."""
    
    # In a real implementation, this would queue messages to Telegram
    # For now, we just define the interface
    
    @staticmethod
    async def notify_transaction_recorded(user_id: int, investment_summary: Dict, 
                                         transaction_type: TransactionType,
                                         amount: float) -> bool:
        """Queue notification for recorded transaction."""
        # TODO: Implement Telegram notification sending
        # This would be called after transaction is saved
        return True
    
    @staticmethod
    async def notify_valuation_updated(user_id: int, old_value: float, 
                                      new_value: float, change_percentage: float) -> bool:
        """Queue notification for portfolio valuation update."""
        # TODO: Implement Telegram notification sending
        return True
    
    @staticmethod
    async def notify_error(user_id: int, error_message: str) -> bool:
        """Queue notification for error."""
        # TODO: Implement error notification
        return True


class AnalyticsService:
    """Service for analytics and reporting."""
    
    def __init__(self, session: AsyncSession):
        self.investment_repo = InvestmentRepository(session)
        self.transaction_repo = TransactionRepository(session)
        self.valuation_repo = ValuationRepository(session)
        self.portfolio_service = PortfolioService(session)
    
    async def get_total_invested_capital(self) -> float:
        """Get total capital across all active investments."""
        # TODO: Implement aggregate query
        return 0
    
    async def get_total_portfolio_value(self) -> float:
        """Get total portfolio value across all investments."""
        # TODO: Implement aggregate query
        return 0
    
    async def get_transaction_count(self, days: int = 30) -> int:
        """Get transaction count in last N days."""
        # TODO: Implement time-based query
        return 0
    
    async def get_daily_active_users(self, days: int = 7) -> int:
        """Get number of active users in last N days."""
        # TODO: Implement user activity tracking
        return 0
