"""HTTP Client for API communication from Bot."""

import httpx
import json
from typing import Optional, Dict, Any, List
from app.config import settings

# API base URL
API_BASE_URL = getattr(settings, 'API_URL', 'http://localhost:8000')


class APIClient:
    """HTTP client for API endpoints."""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.timeout = 10.0
    
    async def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to API."""
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            if method.upper() == "GET":
                response = await client.get(url, params=params)
            elif method.upper() == "POST":
                response = await client.post(url, json=data)
            elif method.upper() == "PUT":
                response = await client.put(url, json=data)
            elif method.upper() == "DELETE":
                response = await client.delete(url)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
    
    # USER ENDPOINTS
    async def get_user(self, user_id: int) -> Dict[str, Any]:
        """Get user by ID."""
        return await self.request("GET", f"/api/v1/users/{user_id}")
    
    async def get_user_by_telegram(self, telegram_id: int) -> Dict[str, Any]:
        """Get user by Telegram ID."""
        return await self.request("GET", f"/api/v1/users/telegram/{telegram_id}")
    
    async def get_user_by_phone(self, phone: str) -> Dict[str, Any]:
        """Get user by phone number."""
        return await self.request("GET", f"/api/v1/users/phone/{phone}")
    
    async def create_user(self, name: str, phone: str, role: str) -> Dict[str, Any]:
        """Create new user."""
        return await self.request("POST", "/api/v1/users", data={
            "name": name,
            "phone": phone,
            "role": role
        })
    
    async def update_user(self, user_id: int, **kwargs) -> Dict[str, Any]:
        """Update user."""
        return await self.request("PUT", f"/api/v1/users/{user_id}", data=kwargs)
    
    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user statistics."""
        return await self.request("GET", f"/api/v1/users/{user_id}/stats")
    
    async def list_users(self, skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """List all users."""
        return await self.request("GET", "/api/v1/users", params={"skip": skip, "limit": limit})
    
    # INVESTMENT ENDPOINTS
    async def get_investment(self, investment_id: int) -> Dict[str, Any]:
        """Get investment by ID."""
        return await self.request("GET", f"/api/v1/investments/{investment_id}")
    
    async def create_investment(
        self,
        investor_id: int,
        investment_type: str,
        initial_amount: float,
        rate: Optional[float] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create new investment."""
        return await self.request("POST", "/api/v1/investments", data={
            "investor_id": investor_id,
            "investment_type": investment_type,
            "initial_amount": initial_amount,
            "rate": rate,
            "description": description
        })
    
    async def get_user_investments(self, investor_id: int) -> List[Dict[str, Any]]:
        """Get user's investments."""
        return await self.request(
            "GET",
            "/api/v1/investments",
            params={"investor_id": investor_id}
        )
    
    async def get_investment_details(self, investment_id: int) -> Dict[str, Any]:
        """Get detailed investment info."""
        return await self.request("GET", f"/api/v1/investments/{investment_id}/details")
    
    async def list_investments(self, skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """List all investments."""
        return await self.request("GET", "/api/v1/investments", params={"skip": skip, "limit": limit})
    
    # TRANSACTION ENDPOINTS
    async def create_transaction(
        self,
        investment_id: int,
        transaction_type: str,
        amount: float,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create new transaction."""
        return await self.request("POST", "/api/v1/transactions", data={
            "investment_id": investment_id,
            "transaction_type": transaction_type,
            "amount": amount,
            "description": description
        })
    
    async def get_investment_transactions(self, investment_id: int) -> List[Dict[str, Any]]:
        """Get investment's transactions."""
        return await self.request(
            "GET",
            "/api/v1/transactions",
            params={"investment_id": investment_id}
        )
    
    async def list_transactions(self, skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """List all transactions."""
        return await self.request("GET", "/api/v1/transactions", params={"skip": skip, "limit": limit})


# Global client instance
api_client = APIClient()
