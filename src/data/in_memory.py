"""
In-Memory Repository Implementations

Provides thread-safe, dict-based storage for development and testing.
Can be swapped with SQLAlchemy repositories later without changing business logic.

Features:
  - Thread-safe operations using locks
  - Automatic ID generation (uuid)
  - Timestamp tracking (created_at, updated_at)
  - Transaction-like operations
  - Easy to test, debug, and understand
"""

import threading
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from .repositories import (
    UserRepository, 
    PortfolioRepository, 
    SessionRepository, 
    UsageStatsRepository, 
    RepositoryFactory
)


def utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(timezone.utc)


class InMemoryUserRepository(UserRepository):
    """In-memory User storage"""
    
    def __init__(self):
        self._users: Dict[str, Dict[str, Any]] = {}  # {user_id: user_dict}
        self._email_index: Dict[str, str] = {}        # {email: user_id}
        self._username_index: Dict[str, str] = {}     # {username: user_id}
        self._lock = threading.RLock()
    
    def _new_id(self) -> str:
        """Generate new user ID"""
        return str(uuid.uuid4())
    
    def create(self, email: str, username: str, password_hash: str, **kwargs) -> Dict[str, Any]:
        """Create new user"""
        with self._lock:
            # Check for duplicates
            if self._email_index.get(email):
                raise ValueError(f"User with email '{email}' already exists")
            if self._username_index.get(username):
                raise ValueError(f"User with username '{username}' already exists")
            
            user_id = self._new_id()
            now = utc_now()
            
            user = {
                'id': user_id,
                'email': email,
                'username': username,
                'password_hash': password_hash,
                'tier': kwargs.get('tier', 'FREE'),
                'subscription_expires_at': kwargs.get('subscription_expires_at'),
                'email_verified': kwargs.get('email_verified', False),
                'failed_login_attempts': 0,
                'locked_until': None,
                'created_at': now,
                'updated_at': now,
            }
            
            self._users[user_id] = user
            self._email_index[email] = user_id
            self._username_index[username] = user_id
            
            return user
    
    def get_by_id(self, user_id: Any) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        with self._lock:
            return self._users.get(str(user_id))
    
    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        with self._lock:
            user_id = self._email_index.get(email)
            if user_id:
                return self._users.get(user_id)
            return None
    
    def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        with self._lock:
            user_id = self._username_index.get(username)
            if user_id:
                return self._users.get(user_id)
            return None
    
    def update(self, user_id: Any, **kwargs) -> Optional[Dict[str, Any]]:
        """Update user"""
        with self._lock:
            user = self._users.get(str(user_id))
            if not user:
                return None
            
            # Allow updating these fields
            allowed_fields = {
                'tier', 'subscription_expires_at', 'email_verified',
                'failed_login_attempts', 'locked_until', 'password_hash'
            }
            
            for key, value in kwargs.items():
                if key in allowed_fields:
                    user[key] = value
            
            user['updated_at'] = utc_now()
            return user
    
    def delete(self, user_id: Any) -> bool:
        """Delete user"""
        with self._lock:
            user_id = str(user_id)
            user = self._users.pop(user_id, None)
            if user:
                self._email_index.pop(user['email'], None)
                self._username_index.pop(user['username'], None)
                return True
            return False
    
    def list_all(self) -> List[Dict[str, Any]]:
        """List all users"""
        with self._lock:
            return list(self._users.values())
    
    def exists(self, email: str = None, username: str = None) -> bool:
        """Check if user exists"""
        with self._lock:
            if email and email in self._email_index:
                return True
            if username and username in self._username_index:
                return True
            return False


class InMemoryPortfolioRepository(PortfolioRepository):
    """In-memory Portfolio storage"""
    
    def __init__(self):
        self._portfolios: Dict[str, Dict[str, Any]] = {}  # {portfolio_id: entry}
        self._user_index: Dict[str, List[str]] = {}       # {user_id: [portfolio_ids]}
        self._lock = threading.RLock()
    
    def _new_id(self) -> str:
        """Generate new portfolio entry ID"""
        return str(uuid.uuid4())
    
    def create(self, user_id: Any, ticker: str, **kwargs) -> Dict[str, Any]:
        """Add stock to portfolio"""
        with self._lock:
            portfolio_id = self._new_id()
            now = utc_now()
            
            entry = {
                'id': portfolio_id,
                'user_id': str(user_id),
                'ticker': ticker,
                'quantity': kwargs.get('quantity', 1),
                'purchase_price': kwargs.get('purchase_price', 0.0),
                'purchase_date': kwargs.get('purchase_date', now),
                'notes': kwargs.get('notes', ''),
                'created_at': now,
                'updated_at': now,
            }
            
            self._portfolios[portfolio_id] = entry
            
            # Update index
            if str(user_id) not in self._user_index:
                self._user_index[str(user_id)] = []
            self._user_index[str(user_id)].append(portfolio_id)
            
            return entry
    
    def get_by_id(self, portfolio_id: Any) -> Optional[Dict[str, Any]]:
        """Get portfolio entry by ID"""
        with self._lock:
            return self._portfolios.get(str(portfolio_id))
    
    def get_user_portfolio(self, user_id: Any) -> List[Dict[str, Any]]:
        """Get all stocks in user's portfolio"""
        with self._lock:
            user_id = str(user_id)
            portfolio_ids = self._user_index.get(user_id, [])
            return [self._portfolios[pid] for pid in portfolio_ids if pid in self._portfolios]
    
    def update(self, portfolio_id: Any, **kwargs) -> Optional[Dict[str, Any]]:
        """Update portfolio entry"""
        with self._lock:
            entry = self._portfolios.get(str(portfolio_id))
            if not entry:
                return None
            
            allowed_fields = {'quantity', 'purchase_price', 'notes'}
            for key, value in kwargs.items():
                if key in allowed_fields:
                    entry[key] = value
            
            entry['updated_at'] = utc_now()
            return entry
    
    def delete(self, portfolio_id: Any) -> bool:
        """Remove stock from portfolio"""
        with self._lock:
            portfolio_id = str(portfolio_id)
            entry = self._portfolios.pop(portfolio_id, None)
            if entry:
                user_id = entry['user_id']
                if user_id in self._user_index:
                    self._user_index[user_id] = [
                        pid for pid in self._user_index[user_id] if pid != portfolio_id
                    ]
                return True
            return False
    
    def delete_user_portfolio(self, user_id: Any) -> bool:
        """Clear entire user portfolio"""
        with self._lock:
            user_id = str(user_id)
            portfolio_ids = self._user_index.get(user_id, [])
            for pid in portfolio_ids:
                self._portfolios.pop(pid, None)
            self._user_index[user_id] = []
            return True
    
    def list_all(self) -> List[Dict[str, Any]]:
        """List all portfolio entries"""
        with self._lock:
            return list(self._portfolios.values())


class InMemorySessionRepository(SessionRepository):
    """In-memory Session storage for auth tokens"""
    
    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}  # {session_id: session}
        self._token_index: Dict[str, str] = {}          # {token: session_id}
        self._user_index: Dict[str, List[str]] = {}     # {user_id: [session_ids]}
        self._lock = threading.RLock()
    
    def _new_id(self) -> str:
        """Generate new session ID"""
        return str(uuid.uuid4())
    
    def create(self, user_id: Any, session_token: str, expires_at: datetime, **kwargs) -> Dict[str, Any]:
        """Create session"""
        with self._lock:
            session_id = self._new_id()
            now = utc_now()
            
            session = {
                'id': session_id,
                'user_id': str(user_id),
                'session_token': session_token,
                'expires_at': expires_at,
                'revoked': False,
                'revoked_at': None,
                'created_at': now,
            }
            
            self._sessions[session_id] = session
            self._token_index[session_token] = session_id
            
            if str(user_id) not in self._user_index:
                self._user_index[str(user_id)] = []
            self._user_index[str(user_id)].append(session_id)
            
            return session
    
    def get_by_id(self, session_id: Any) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        with self._lock:
            return self._sessions.get(str(session_id))
    
    def get_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get session by token"""
        with self._lock:
            session_id = self._token_index.get(token)
            if session_id:
                return self._sessions.get(session_id)
            return None
    
    def validate_token(self, token: str) -> bool:
        """Check if token is valid and not expired"""
        with self._lock:
            session = self.get_by_token(token)
            if not session:
                return False
            
            # Check if revoked
            if session['revoked']:
                return False
            
            # Check if expired
            if session['expires_at'] < utc_now():
                return False
            
            return True
    
    def revoke(self, token: str) -> bool:
        """Revoke (logout) a session"""
        with self._lock:
            session_id = self._token_index.get(token)
            if session_id and session_id in self._sessions:
                session = self._sessions[session_id]
                session['revoked'] = True
                session['revoked_at'] = utc_now()
                return True
            return False
    
    def delete_user_sessions(self, user_id: Any) -> bool:
        """Delete all sessions for a user (logout everywhere)"""
        with self._lock:
            user_id = str(user_id)
            session_ids = self._user_index.get(user_id, [])
            for sid in session_ids:
                session = self._sessions.pop(sid, None)
                if session:
                    self._token_index.pop(session['session_token'], None)
            self._user_index[user_id] = []
            return True
    
    def cleanup_expired(self) -> int:
        """Delete expired sessions, return count deleted"""
        with self._lock:
            now = utc_now()
            expired_ids = [
                sid for sid, session in self._sessions.items()
                if session['expires_at'] < now
            ]
            
            for sid in expired_ids:
                session = self._sessions.pop(sid)
                self._token_index.pop(session['session_token'], None)
            
            return len(expired_ids)
    
    def update(self, session_id: Any, **kwargs) -> Optional[Dict[str, Any]]:
        """Update session (for compatibility with Repository interface)"""
        with self._lock:
            session = self._sessions.get(str(session_id))
            if not session:
                return None
            
            allowed_fields = {'revoked', 'revoked_at'}
            for key, value in kwargs.items():
                if key in allowed_fields:
                    session[key] = value
            
            return session
    
    def delete(self, session_id: Any) -> bool:
        """Delete session by ID"""
        with self._lock:
            session_id = str(session_id)
            session = self._sessions.pop(session_id, None)
            if session:
                self._token_index.pop(session['session_token'], None)
                return True
            return False
    
    def list_all(self) -> List[Dict[str, Any]]:
        """List all sessions"""
        with self._lock:
            return list(self._sessions.values())


class InMemoryUsageStatsRepository(UsageStatsRepository):
    """In-memory Usage Statistics storage"""
    
    def __init__(self):
        self._stats: Dict[str, Dict[str, Any]] = {}  # {stats_id: stats}
        self._user_date_index: Dict[str, str] = {}   # {user_id:YYYY-MM-DD: stats_id}
        self._lock = threading.RLock()
    
    def _new_id(self) -> str:
        """Generate new stats ID"""
        return str(uuid.uuid4())
    
    def _make_key(self, user_id: Any, date: str) -> str:
        """Create user:date index key"""
        return f"{user_id}:{date}"
    
    def create(self, user_id: Any, date: str, **kwargs) -> Dict[str, Any]:
        """Create/reset usage stats for a day"""
        with self._lock:
            stats_id = self._new_id()
            now = utc_now()
            
            stats = {
                'id': stats_id,
                'user_id': str(user_id),
                'date': date,
                'requests_used': kwargs.get('requests_used', 0),
                'stocks_analyzed': kwargs.get('stocks_analyzed', 0),
                'created_at': now,
                'updated_at': now,
            }
            
            self._stats[stats_id] = stats
            self._user_date_index[self._make_key(user_id, date)] = stats_id
            
            return stats
    
    def get_today(self, user_id: Any) -> Optional[Dict[str, Any]]:
        """Get today's usage stats"""
        with self._lock:
            today = utc_now().strftime('%Y-%m-%d')
            key = self._make_key(user_id, today)
            stats_id = self._user_date_index.get(key)
            if stats_id:
                return self._stats.get(stats_id)
            return None
    
    def increment_requests(self, user_id: Any, amount: int = 1) -> Dict[str, Any]:
        """Increment request count for today"""
        with self._lock:
            stats = self.get_today(user_id)
            if not stats:
                # Create today's stats
                today = utc_now().strftime('%Y-%m-%d')
                stats = self.create(user_id, today)
            
            stats['requests_used'] += amount
            stats['updated_at'] = utc_now()
            return stats
    
    def increment_stocks(self, user_id: Any, amount: int = 1) -> Dict[str, Any]:
        """Increment stocks analyzed for today"""
        with self._lock:
            stats = self.get_today(user_id)
            if not stats:
                # Create today's stats
                today = utc_now().strftime('%Y-%m-%d')
                stats = self.create(user_id, today)
            
            stats['stocks_analyzed'] += amount
            stats['updated_at'] = utc_now()
            return stats
    
    def get_by_id(self, stats_id: Any) -> Optional[Dict[str, Any]]:
        """Get stats by ID"""
        with self._lock:
            return self._stats.get(str(stats_id))
    
    def update(self, stats_id: Any, **kwargs) -> Optional[Dict[str, Any]]:
        """Update stats"""
        with self._lock:
            stats = self._stats.get(str(stats_id))
            if not stats:
                return None
            
            allowed_fields = {'requests_used', 'stocks_analyzed'}
            for key, value in kwargs.items():
                if key in allowed_fields:
                    stats[key] = value
            
            stats['updated_at'] = utc_now()
            return stats
    
    def delete(self, stats_id: Any) -> bool:
        """Delete stats"""
        with self._lock:
            stats_id = str(stats_id)
            stats = self._stats.pop(stats_id, None)
            if stats:
                key = self._make_key(stats['user_id'], stats['date'])
                self._user_date_index.pop(key, None)
                return True
            return False
    
    def list_all(self) -> List[Dict[str, Any]]:
        """List all stats"""
        with self._lock:
            return list(self._stats.values())


class InMemoryRepositoryFactory(RepositoryFactory):
    """Factory for in-memory repositories"""
    
    def __init__(self):
        self._user_repo = InMemoryUserRepository()
        self._portfolio_repo = InMemoryPortfolioRepository()
        self._session_repo = InMemorySessionRepository()
        self._usage_repo = InMemoryUsageStatsRepository()
    
    def get_user_repository(self) -> UserRepository:
        return self._user_repo
    
    def get_portfolio_repository(self) -> PortfolioRepository:
        return self._portfolio_repo
    
    def get_session_repository(self) -> SessionRepository:
        return self._session_repo
    
    def get_usage_stats_repository(self) -> UsageStatsRepository:
        return self._usage_repo
