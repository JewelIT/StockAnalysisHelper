"""
SQLite Repository Implementations

Provides persistent storage using sqlite3 (built-in Python module).
No external dependencies. Safe for production use.

Implements the same repository interface as in-memory versions,
allowing seamless swapping between implementations.
"""

import sqlite3
import threading
import uuid
import json
from datetime import datetime, timezone
from pathlib import Path
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


def utc_timestamp() -> str:
    """Get current UTC time as ISO string"""
    return utc_now().isoformat()


class SqliteConnection:
    """Thread-safe SQLite connection manager"""
    
    def __init__(self, db_path: str = 'vestor.db'):
        self.db_path = db_path
        self._local = threading.local()
        self._lock = threading.RLock()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get thread-local connection"""
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            self._local.connection.row_factory = sqlite3.Row
            # Enable foreign key constraints
            self._local.connection.execute("PRAGMA foreign_keys = ON")
        return self._local.connection
    
    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute query with thread safety"""
        conn = self.get_connection()
        return conn.execute(sql, params)
    
    def commit(self):
        """Commit transaction"""
        conn = self.get_connection()
        conn.commit()
    
    def close(self):
        """Close connection"""
        if hasattr(self._local, 'connection'):
            self._local.connection.close()
            del self._local.connection


class SqliteUserRepository(UserRepository):
    """SQLite User storage"""
    
    def __init__(self, db_conn: SqliteConnection):
        self.db = db_conn
        self._create_table()
    
    def _create_table(self):
        """Create users table if not exists"""
        sql = """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            tier TEXT DEFAULT 'FREE',
            subscription_expires_at TEXT,
            email_verified BOOLEAN DEFAULT 0,
            failed_login_attempts INTEGER DEFAULT 0,
            locked_until TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
        self.db.execute(sql)
        self.db.commit()
    
    def create(self, email: str, username: str, password_hash: str, **kwargs) -> Dict[str, Any]:
        """Create new user"""
        # Check for duplicates
        if self.exists(email=email):
            raise ValueError(f"User with email '{email}' already exists")
        if self.exists(username=username):
            raise ValueError(f"User with username '{username}' already exists")
        
        user_id = str(uuid.uuid4())
        now = utc_timestamp()
        
        sql = """
        INSERT INTO users (id, email, username, password_hash, tier, email_verified, 
                          created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        self.db.execute(sql, (
            user_id, email, username, password_hash,
            kwargs.get('tier', 'FREE'),
            1 if kwargs.get('email_verified') else 0,
            now, now
        ))
        self.db.commit()
        
        return self.get_by_id(user_id)
    
    def get_by_id(self, user_id: Any) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        cursor = self.db.execute("SELECT * FROM users WHERE id = ?", (str(user_id),))
        row = cursor.fetchone()
        return self._row_to_dict(row) if row else None
    
    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        cursor = self.db.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        return self._row_to_dict(row) if row else None
    
    def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        cursor = self.db.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        return self._row_to_dict(row) if row else None
    
    def update(self, user_id: Any, **kwargs) -> Optional[Dict[str, Any]]:
        """Update user"""
        if not self.get_by_id(user_id):
            return None
        
        allowed_fields = {
            'tier', 'subscription_expires_at', 'email_verified',
            'failed_login_attempts', 'locked_until', 'password_hash'
        }
        
        updates = []
        values = []
        for key, value in kwargs.items():
            if key in allowed_fields:
                updates.append(f"{key} = ?")
                values.append(value)
        
        if not updates:
            return self.get_by_id(user_id)
        
        updates.append("updated_at = ?")
        values.append(utc_timestamp())
        values.append(str(user_id))
        
        sql = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        self.db.execute(sql, values)
        self.db.commit()
        
        return self.get_by_id(user_id)
    
    def delete(self, user_id: Any) -> bool:
        """Delete user"""
        cursor = self.db.execute("DELETE FROM users WHERE id = ?", (str(user_id),))
        self.db.commit()
        return cursor.rowcount > 0
    
    def list_all(self) -> List[Dict[str, Any]]:
        """List all users"""
        cursor = self.db.execute("SELECT * FROM users")
        return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def exists(self, email: str = None, username: str = None) -> bool:
        """Check if user exists"""
        if email:
            cursor = self.db.execute("SELECT 1 FROM users WHERE email = ?", (email,))
            return cursor.fetchone() is not None
        if username:
            cursor = self.db.execute("SELECT 1 FROM users WHERE username = ?", (username,))
            return cursor.fetchone() is not None
        return False
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert sqlite3.Row to dict"""
        if row is None:
            return None
        
        user = dict(row)
        # Convert boolean fields
        user['email_verified'] = bool(user.get('email_verified'))
        # Convert timestamps to datetime if not None
        if user.get('subscription_expires_at'):
            user['subscription_expires_at'] = datetime.fromisoformat(user['subscription_expires_at'])
        if user.get('locked_until'):
            user['locked_until'] = datetime.fromisoformat(user['locked_until'])
        if user.get('created_at'):
            user['created_at'] = datetime.fromisoformat(user['created_at'])
        if user.get('updated_at'):
            user['updated_at'] = datetime.fromisoformat(user['updated_at'])
        
        return user


class SqlitePortfolioRepository(PortfolioRepository):
    """SQLite Portfolio storage"""
    
    def __init__(self, db_conn: SqliteConnection):
        self.db = db_conn
        self._create_table()
    
    def _create_table(self):
        """Create portfolios table if not exists"""
        sql = """
        CREATE TABLE IF NOT EXISTS portfolios (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            ticker TEXT NOT NULL,
            quantity REAL,
            purchase_price REAL,
            purchase_date TEXT,
            notes TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
        self.db.execute(sql)
        self.db.commit()
    
    def create(self, user_id: Any, ticker: str, **kwargs) -> Dict[str, Any]:
        """Add stock to portfolio"""
        portfolio_id = str(uuid.uuid4())
        now = utc_timestamp()
        
        sql = """
        INSERT INTO portfolios (id, user_id, ticker, quantity, purchase_price, 
                               purchase_date, notes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        self.db.execute(sql, (
            portfolio_id, str(user_id), ticker,
            kwargs.get('quantity', 1),
            kwargs.get('purchase_price', 0.0),
            kwargs.get('purchase_date'),
            kwargs.get('notes', ''),
            now, now
        ))
        self.db.commit()
        
        return self.get_by_id(portfolio_id)
    
    def get_by_id(self, portfolio_id: Any) -> Optional[Dict[str, Any]]:
        """Get portfolio entry by ID"""
        cursor = self.db.execute("SELECT * FROM portfolios WHERE id = ?", (str(portfolio_id),))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_user_portfolio(self, user_id: Any) -> List[Dict[str, Any]]:
        """Get all stocks in user's portfolio"""
        cursor = self.db.execute(
            "SELECT * FROM portfolios WHERE user_id = ? ORDER BY created_at DESC",
            (str(user_id),)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def update(self, portfolio_id: Any, **kwargs) -> Optional[Dict[str, Any]]:
        """Update portfolio entry"""
        if not self.get_by_id(portfolio_id):
            return None
        
        allowed_fields = {'quantity', 'purchase_price', 'notes'}
        
        updates = []
        values = []
        for key, value in kwargs.items():
            if key in allowed_fields:
                updates.append(f"{key} = ?")
                values.append(value)
        
        if not updates:
            return self.get_by_id(portfolio_id)
        
        updates.append("updated_at = ?")
        values.append(utc_timestamp())
        values.append(str(portfolio_id))
        
        sql = f"UPDATE portfolios SET {', '.join(updates)} WHERE id = ?"
        self.db.execute(sql, values)
        self.db.commit()
        
        return self.get_by_id(portfolio_id)
    
    def delete(self, portfolio_id: Any) -> bool:
        """Remove stock from portfolio"""
        cursor = self.db.execute("DELETE FROM portfolios WHERE id = ?", (str(portfolio_id),))
        self.db.commit()
        return cursor.rowcount > 0
    
    def delete_user_portfolio(self, user_id: Any) -> bool:
        """Clear entire user portfolio"""
        cursor = self.db.execute("DELETE FROM portfolios WHERE user_id = ?", (str(user_id),))
        self.db.commit()
        return True
    
    def list_all(self) -> List[Dict[str, Any]]:
        """List all portfolio entries"""
        cursor = self.db.execute("SELECT * FROM portfolios")
        return [dict(row) for row in cursor.fetchall()]


class SqliteSessionRepository(SessionRepository):
    """SQLite Session storage"""
    
    def __init__(self, db_conn: SqliteConnection):
        self.db = db_conn
        self._create_table()
    
    def _create_table(self):
        """Create sessions table if not exists"""
        sql = """
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            session_token TEXT UNIQUE NOT NULL,
            expires_at TEXT NOT NULL,
            revoked BOOLEAN DEFAULT 0,
            revoked_at TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
        self.db.execute(sql)
        self.db.commit()
    
    def create(self, user_id: Any, session_token: str, expires_at: datetime, **kwargs) -> Dict[str, Any]:
        """Create session"""
        session_id = str(uuid.uuid4())
        now = utc_timestamp()
        
        sql = """
        INSERT INTO sessions (id, user_id, session_token, expires_at, created_at)
        VALUES (?, ?, ?, ?, ?)
        """
        
        self.db.execute(sql, (
            session_id, str(user_id), session_token,
            expires_at.isoformat() if isinstance(expires_at, datetime) else expires_at,
            now
        ))
        self.db.commit()
        
        return self.get_by_id(session_id)
    
    def get_by_id(self, session_id: Any) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        cursor = self.db.execute("SELECT * FROM sessions WHERE id = ?", (str(session_id),))
        row = cursor.fetchone()
        return self._row_to_dict(row) if row else None
    
    def get_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get session by token"""
        cursor = self.db.execute("SELECT * FROM sessions WHERE session_token = ?", (token,))
        row = cursor.fetchone()
        return self._row_to_dict(row) if row else None
    
    def validate_token(self, token: str) -> bool:
        """Check if token is valid and not expired"""
        session = self.get_by_token(token)
        if not session:
            return False
        
        if session['revoked']:
            return False
        
        expires_at = datetime.fromisoformat(session['expires_at'])
        if expires_at < utc_now():
            return False
        
        return True
    
    def revoke(self, token: str) -> bool:
        """Revoke (logout) a session"""
        session = self.get_by_token(token)
        if not session:
            return False
        
        sql = "UPDATE sessions SET revoked = 1, revoked_at = ? WHERE session_token = ?"
        self.db.execute(sql, (utc_timestamp(), token))
        self.db.commit()
        return True
    
    def delete_user_sessions(self, user_id: Any) -> bool:
        """Delete all sessions for a user"""
        cursor = self.db.execute("DELETE FROM sessions WHERE user_id = ?", (str(user_id),))
        self.db.commit()
        return True
    
    def cleanup_expired(self) -> int:
        """Delete expired sessions, return count deleted"""
        now = utc_timestamp()
        cursor = self.db.execute("DELETE FROM sessions WHERE expires_at < ?", (now,))
        self.db.commit()
        return cursor.rowcount
    
    def update(self, session_id: Any, **kwargs) -> Optional[Dict[str, Any]]:
        """Update session"""
        if not self.get_by_id(session_id):
            return None
        
        allowed_fields = {'revoked', 'revoked_at'}
        
        updates = []
        values = []
        for key, value in kwargs.items():
            if key in allowed_fields:
                updates.append(f"{key} = ?")
                values.append(value)
        
        if not updates:
            return self.get_by_id(session_id)
        
        values.append(str(session_id))
        sql = f"UPDATE sessions SET {', '.join(updates)} WHERE id = ?"
        self.db.execute(sql, values)
        self.db.commit()
        
        return self.get_by_id(session_id)
    
    def delete(self, session_id: Any) -> bool:
        """Delete session by ID"""
        cursor = self.db.execute("DELETE FROM sessions WHERE id = ?", (str(session_id),))
        self.db.commit()
        return cursor.rowcount > 0
    
    def list_all(self) -> List[Dict[str, Any]]:
        """List all sessions"""
        cursor = self.db.execute("SELECT * FROM sessions")
        return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert sqlite3.Row to dict with proper type conversions"""
        if row is None:
            return None
        
        session = dict(row)
        session['revoked'] = bool(session.get('revoked'))
        
        if session.get('expires_at'):
            session['expires_at'] = datetime.fromisoformat(session['expires_at'])
        if session.get('revoked_at'):
            session['revoked_at'] = datetime.fromisoformat(session['revoked_at'])
        if session.get('created_at'):
            session['created_at'] = datetime.fromisoformat(session['created_at'])
        
        return session


class SqliteUsageStatsRepository(UsageStatsRepository):
    """SQLite Usage Statistics storage"""
    
    def __init__(self, db_conn: SqliteConnection):
        self.db = db_conn
        self._create_table()
    
    def _create_table(self):
        """Create usage_stats table if not exists"""
        sql = """
        CREATE TABLE IF NOT EXISTS usage_stats (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            date TEXT NOT NULL,
            requests_used INTEGER DEFAULT 0,
            stocks_analyzed INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(user_id, date),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
        self.db.execute(sql)
        self.db.commit()
    
    def create(self, user_id: Any, date: str, **kwargs) -> Dict[str, Any]:
        """Create/reset usage stats for a day"""
        stats_id = str(uuid.uuid4())
        now = utc_timestamp()
        
        sql = """
        INSERT INTO usage_stats (id, user_id, date, requests_used, stocks_analyzed, 
                                created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        self.db.execute(sql, (
            stats_id, str(user_id), date,
            kwargs.get('requests_used', 0),
            kwargs.get('stocks_analyzed', 0),
            now, now
        ))
        self.db.commit()
        
        return self.get_by_id(stats_id)
    
    def get_today(self, user_id: Any) -> Optional[Dict[str, Any]]:
        """Get today's usage stats"""
        today = utc_now().strftime('%Y-%m-%d')
        cursor = self.db.execute(
            "SELECT * FROM usage_stats WHERE user_id = ? AND date = ?",
            (str(user_id), today)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def increment_requests(self, user_id: Any, amount: int = 1) -> Dict[str, Any]:
        """Increment request count for today"""
        stats = self.get_today(user_id)
        if not stats:
            today = utc_now().strftime('%Y-%m-%d')
            stats = self.create(user_id, today)
        
        sql = "UPDATE usage_stats SET requests_used = requests_used + ? WHERE id = ?"
        self.db.execute(sql, (amount, stats['id']))
        self.db.commit()
        
        return self.get_by_id(stats['id'])
    
    def increment_stocks(self, user_id: Any, amount: int = 1) -> Dict[str, Any]:
        """Increment stocks analyzed for today"""
        stats = self.get_today(user_id)
        if not stats:
            today = utc_now().strftime('%Y-%m-%d')
            stats = self.create(user_id, today)
        
        sql = "UPDATE usage_stats SET stocks_analyzed = stocks_analyzed + ? WHERE id = ?"
        self.db.execute(sql, (amount, stats['id']))
        self.db.commit()
        
        return self.get_by_id(stats['id'])
    
    def get_by_id(self, stats_id: Any) -> Optional[Dict[str, Any]]:
        """Get stats by ID"""
        cursor = self.db.execute("SELECT * FROM usage_stats WHERE id = ?", (str(stats_id),))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def update(self, stats_id: Any, **kwargs) -> Optional[Dict[str, Any]]:
        """Update stats"""
        if not self.get_by_id(stats_id):
            return None
        
        allowed_fields = {'requests_used', 'stocks_analyzed'}
        
        updates = []
        values = []
        for key, value in kwargs.items():
            if key in allowed_fields:
                updates.append(f"{key} = ?")
                values.append(value)
        
        if not updates:
            return self.get_by_id(stats_id)
        
        updates.append("updated_at = ?")
        values.append(utc_timestamp())
        values.append(str(stats_id))
        
        sql = f"UPDATE usage_stats SET {', '.join(updates)} WHERE id = ?"
        self.db.execute(sql, values)
        self.db.commit()
        
        return self.get_by_id(stats_id)
    
    def delete(self, stats_id: Any) -> bool:
        """Delete stats"""
        cursor = self.db.execute("DELETE FROM usage_stats WHERE id = ?", (str(stats_id),))
        self.db.commit()
        return cursor.rowcount > 0
    
    def list_all(self) -> List[Dict[str, Any]]:
        """List all stats"""
        cursor = self.db.execute("SELECT * FROM usage_stats")
        return [dict(row) for row in cursor.fetchall()]


class SqliteRepositoryFactory(RepositoryFactory):
    """Factory for SQLite repositories"""
    
    def __init__(self, db_path: str = 'vestor.db'):
        self.db_conn = SqliteConnection(db_path)
        self._user_repo = SqliteUserRepository(self.db_conn)
        self._portfolio_repo = SqlitePortfolioRepository(self.db_conn)
        self._session_repo = SqliteSessionRepository(self.db_conn)
        self._usage_repo = SqliteUsageStatsRepository(self.db_conn)
    
    def get_user_repository(self) -> UserRepository:
        return self._user_repo
    
    def get_portfolio_repository(self) -> PortfolioRepository:
        return self._portfolio_repo
    
    def get_session_repository(self) -> SessionRepository:
        return self._session_repo
    
    def get_usage_stats_repository(self) -> UsageStatsRepository:
        return self._usage_repo
