"""
Repository Pattern - Abstract interfaces for data persistence

This module defines the contracts that any persistence layer must implement.
Allows us to:
  - Start with in-memory storage (development/testing)
  - Switch to SQLAlchemy later without changing business logic
  - Support multiple backends (MongoDB, PostgreSQL, etc.)
  
Key Principle: Repositories abstract the WHERE data is stored,
               not the WHAT data is stored.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime


class Repository(ABC):
    """Base repository interface"""
    
    @abstractmethod
    def create(self, **kwargs) -> Any:
        """Create a new entity"""
        pass
    
    @abstractmethod
    def get_by_id(self, entity_id: Any) -> Optional[Any]:
        """Get entity by ID"""
        pass
    
    @abstractmethod
    def update(self, entity_id: Any, **kwargs) -> Optional[Any]:
        """Update an entity"""
        pass
    
    @abstractmethod
    def delete(self, entity_id: Any) -> bool:
        """Delete an entity"""
        pass
    
    @abstractmethod
    def list_all(self) -> List[Any]:
        """List all entities"""
        pass


class UserRepository(Repository):
    """User persistence interface
    
    Contract for any storage implementation.
    """
    
    @abstractmethod
    def create(self, email: str, username: str, password_hash: str, **kwargs) -> Dict[str, Any]:
        """Create new user
        
        Returns:
            User dict with id, email, username, tier, created_at, etc.
            
        Raises:
            ValueError: If email/username already exists
        """
        pass
    
    @abstractmethod
    def get_by_id(self, user_id: Any) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        pass
    
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        pass
    
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        pass
    
    @abstractmethod
    def update(self, user_id: Any, **kwargs) -> Optional[Dict[str, Any]]:
        """Update user (tier, last_login, failed_attempts, etc.)"""
        pass
    
    @abstractmethod
    def delete(self, user_id: Any) -> bool:
        """Delete user and cascade delete related data"""
        pass
    
    @abstractmethod
    def list_all(self) -> List[Dict[str, Any]]:
        """List all users"""
        pass
    
    @abstractmethod
    def exists(self, email: str = None, username: str = None) -> bool:
        """Check if user exists by email or username"""
        pass


class PortfolioRepository(Repository):
    """Portfolio persistence interface"""
    
    @abstractmethod
    def create(self, user_id: Any, ticker: str, **kwargs) -> Dict[str, Any]:
        """Add stock to portfolio"""
        pass
    
    @abstractmethod
    def get_by_id(self, portfolio_id: Any) -> Optional[Dict[str, Any]]:
        """Get portfolio entry by ID"""
        pass
    
    @abstractmethod
    def get_user_portfolio(self, user_id: Any) -> List[Dict[str, Any]]:
        """Get all stocks in user's portfolio"""
        pass
    
    @abstractmethod
    def update(self, portfolio_id: Any, **kwargs) -> Optional[Dict[str, Any]]:
        """Update portfolio entry (quantity, purchase_price, etc.)"""
        pass
    
    @abstractmethod
    def delete(self, portfolio_id: Any) -> bool:
        """Remove stock from portfolio"""
        pass
    
    @abstractmethod
    def delete_user_portfolio(self, user_id: Any) -> bool:
        """Clear entire user portfolio"""
        pass
    
    @abstractmethod
    def list_all(self) -> List[Dict[str, Any]]:
        """List all portfolio entries"""
        pass


class SessionRepository(Repository):
    """Session persistence interface (auth tokens, refresh tokens, etc.)"""
    
    @abstractmethod
    def create(self, user_id: Any, session_token: str, expires_at: datetime, **kwargs) -> Dict[str, Any]:
        """Create session"""
        pass
    
    @abstractmethod
    def get_by_id(self, session_id: Any) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        pass
    
    @abstractmethod
    def get_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get session by token"""
        pass
    
    @abstractmethod
    def validate_token(self, token: str) -> bool:
        """Check if token is valid and not expired"""
        pass
    
    @abstractmethod
    def revoke(self, token: str) -> bool:
        """Revoke (logout) a session"""
        pass
    
    @abstractmethod
    def delete_user_sessions(self, user_id: Any) -> bool:
        """Delete all sessions for a user (logout everywhere)"""
        pass
    
    @abstractmethod
    def cleanup_expired(self) -> int:
        """Delete expired sessions, return count deleted"""
        pass
    
    @abstractmethod
    def list_all(self) -> List[Dict[str, Any]]:
        """List all active sessions"""
        pass


class UsageStatsRepository(Repository):
    """Usage tracking persistence interface"""
    
    @abstractmethod
    def create(self, user_id: Any, date: str, **kwargs) -> Dict[str, Any]:
        """Create/reset usage stats for a day"""
        pass
    
    @abstractmethod
    def get_today(self, user_id: Any) -> Optional[Dict[str, Any]]:
        """Get today's usage stats"""
        pass
    
    @abstractmethod
    def increment_requests(self, user_id: Any, amount: int = 1) -> Dict[str, Any]:
        """Increment request count for today"""
        pass
    
    @abstractmethod
    def increment_stocks(self, user_id: Any, amount: int = 1) -> Dict[str, Any]:
        """Increment stocks analyzed for today"""
        pass
    
    @abstractmethod
    def get_by_id(self, stats_id: Any) -> Optional[Dict[str, Any]]:
        """Get stats by ID"""
        pass
    
    @abstractmethod
    def update(self, stats_id: Any, **kwargs) -> Optional[Dict[str, Any]]:
        """Update stats"""
        pass
    
    @abstractmethod
    def delete(self, stats_id: Any) -> bool:
        """Delete stats"""
        pass
    
    @abstractmethod
    def list_all(self) -> List[Dict[str, Any]]:
        """List all stats"""
        pass


class RepositoryFactory(ABC):
    """Factory for creating repository instances
    
    Allows switching persistence layer globally:
    - Development: InMemoryRepositoryFactory
    - Production: SQLAlchemyRepositoryFactory
    """
    
    @abstractmethod
    def get_user_repository(self) -> UserRepository:
        pass
    
    @abstractmethod
    def get_portfolio_repository(self) -> PortfolioRepository:
        pass
    
    @abstractmethod
    def get_session_repository(self) -> SessionRepository:
        pass
    
    @abstractmethod
    def get_usage_stats_repository(self) -> UsageStatsRepository:
        pass
