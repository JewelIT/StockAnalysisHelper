"""
User Domain Model

Pure Python user class with NO database dependencies.
Encapsulates all user-related business logic:
- Password hashing and verification (Argon2)
- Tier validation and feature access
- Account lockout mechanism
- Subscription management

This is a domain model, not a database model.
It can be persisted to any storage (SQLite, SQLAlchemy, MongoDB, etc.)
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Optional, Set
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError


# Password hasher (Argon2 - OWASP recommended)
_ph = PasswordHasher()


@dataclass
class User:
    """User domain model
    
    Represents a user with authentication, tier management, and account security.
    Pure Python - no database dependencies.
    """
    
    # Identity
    email: str
    username: str
    password_hash: str
    
    # Tier & Subscription
    tier: str = 'FREE'  # 'FREE', 'MIDDLE', 'TOP'
    subscription_expires_at: Optional[datetime] = None
    
    # Security
    email_verified: bool = False
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    
    # Metadata
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Class-level tier definitions (shared across all instances)
    VALID_TIERS = {'FREE', 'MIDDLE', 'TOP'}
    
    TIER_FEATURES = {
        'FREE': {
            'max_stocks_simultaneous': 3,
            'requests_per_day': 20,
            'sentiment_frequency': 'daily',
            'portfolio_storage': False,
            'email_alerts': False,
            'chatbot': False,
            'advanced_insights': False,
        },
        'MIDDLE': {
            'max_stocks_simultaneous': None,  # Unlimited
            'requests_per_day': 500,
            'sentiment_frequency': 'real-time',
            'portfolio_storage': True,
            'email_alerts': True,
            'chatbot': False,
            'advanced_insights': False,
        },
        'TOP': {
            'max_stocks_simultaneous': None,  # Unlimited
            'requests_per_day': None,  # Unlimited
            'sentiment_frequency': 'real-time',
            'portfolio_storage': True,
            'email_alerts': True,
            'chatbot': True,
            'advanced_insights': True,
        },
    }
    
    # Account lockout settings (class-level constants)
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15
    
    # Password policy
    MIN_PASSWORD_LENGTH = 12
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SYMBOL = True
    
    def __post_init__(self):
        """Validate tier and subscription"""
        if self.tier not in self.VALID_TIERS:
            raise ValueError(f"Invalid tier '{self.tier}'. Must be one of {self.VALID_TIERS}")
    
    @staticmethod
    def utc_now() -> datetime:
        """Get current UTC time"""
        return datetime.now(timezone.utc)
    
    def set_password(self, password: str) -> None:
        """Hash and set password using Argon2 (OWASP recommended)
        
        Args:
            password: Plaintext password to hash
            
        Raises:
            ValueError: If password doesn't meet security requirements
        """
        # Validate password strength
        is_valid, message = self.validate_password(password)
        if not is_valid:
            raise ValueError(message)
        
        # Hash with Argon2 (memory-hard, GPU-resistant)
        self.password_hash = _ph.hash(password)
    
    def check_password(self, password: str) -> bool:
        """Verify password against hash using Argon2
        
        Args:
            password: Plaintext password to verify
            
        Returns:
            bool: True if password matches, False otherwise
            
        Note:
            This is timing-resistant (constant-time comparison)
        """
        try:
            _ph.verify(self.password_hash, password)
            return True
        except (VerifyMismatchError, InvalidHashError):
            return False
        except Exception:
            return False
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """Validate password against security policy
        
        Args:
            password: Password to validate
            
        Returns:
            (is_valid, message) tuple
        """
        if len(password) < User.MIN_PASSWORD_LENGTH:
            return False, f'Password must be at least {User.MIN_PASSWORD_LENGTH} characters'
        
        if User.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            return False, 'Password must contain at least one uppercase letter'
        
        if User.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            return False, 'Password must contain at least one lowercase letter'
        
        if User.REQUIRE_DIGIT and not any(c.isdigit() for c in password):
            return False, 'Password must contain at least one digit'
        
        if User.REQUIRE_SYMBOL and not any(c in '!@#$%^&*()-_=+[]{}|;:,.<>?' for c in password):
            return False, 'Password must contain at least one special character (!@#$%^&*)-_=+[]{}|;:,.<>?'
        
        # Check for common patterns
        common_patterns = ['password', '12345', 'qwerty', 'abc123', '111', 'admin']
        if any(pattern in password.lower() for pattern in common_patterns):
            return False, 'Password contains common patterns (too predictable)'
        
        return True, 'Password is valid'
    
    def is_account_locked(self) -> bool:
        """Check if account is locked due to failed login attempts
        
        Returns:
            bool: True if account is currently locked
        """
        if self.locked_until is None:
            return False
        
        # Check if lockout period has expired
        if self.utc_now() >= self.locked_until:
            # Auto-unlock if period expired
            self.locked_until = None
            self.failed_login_attempts = 0
            return False
        
        return True
    
    def record_failed_login(self) -> None:
        """Record a failed login attempt and lock account if needed
        
        Security:
            - After N failed attempts, account is locked
            - Locked account cannot be accessed for specified duration
            - Prevents brute force attacks
        """
        self.failed_login_attempts += 1
        
        if self.failed_login_attempts >= self.MAX_FAILED_ATTEMPTS:
            self.locked_until = self.utc_now() + timedelta(minutes=self.LOCKOUT_DURATION_MINUTES)
    
    def reset_failed_login_attempts(self) -> None:
        """Reset failed login counter after successful login"""
        self.failed_login_attempts = 0
        self.locked_until = None
    
    def can_access_feature(self, feature: str) -> bool:
        """Check if user can access a feature based on tier
        
        Args:
            feature: Feature name to check (e.g., 'chatbot', 'portfolio_storage')
            
        Returns:
            bool: True if user's tier grants access
        """
        if self.tier not in self.TIER_FEATURES:
            return False
        
        tier_features = self.TIER_FEATURES[self.tier]
        return tier_features.get(feature, False)
    
    def is_subscription_active(self) -> bool:
        """Check if subscription is still active
        
        Returns:
            bool: True if subscription is active (or permanent)
        """
        if self.subscription_expires_at is None:
            return True  # Permanent tier (FREE or admin-granted)
        
        return self.utc_now() < self.subscription_expires_at
    
    def get_tier_limits(self) -> dict:
        """Get resource limits for user's tier
        
        Returns:
            dict with limits for this tier
        """
        return self.TIER_FEATURES.get(self.tier, {})
    
    def upgrade_tier(self, new_tier: str, duration_days: Optional[int] = None) -> None:
        """Upgrade user to a new tier
        
        Args:
            new_tier: Target tier ('FREE', 'MIDDLE', 'TOP')
            duration_days: Number of days subscription is valid (None = permanent)
            
        Raises:
            ValueError: If new_tier is invalid
        """
        if new_tier not in self.VALID_TIERS:
            raise ValueError(f"Invalid tier '{new_tier}'. Must be one of {self.VALID_TIERS}")
        
        self.tier = new_tier
        
        if duration_days is None:
            self.subscription_expires_at = None  # Permanent
        else:
            self.subscription_expires_at = self.utc_now() + timedelta(days=duration_days)
    
    def to_dict(self) -> dict:
        """Convert user to dictionary (for API responses, storage, etc.)
        
        Returns:
            dict representation of user
        """
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'password_hash': self.password_hash,
            'tier': self.tier,
            'subscription_expires_at': self.subscription_expires_at.isoformat() if self.subscription_expires_at else None,
            'email_verified': self.email_verified,
            'failed_login_attempts': self.failed_login_attempts,
            'locked_until': self.locked_until.isoformat() if self.locked_until else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Create User from dictionary (for loading from storage)
        
        Args:
            data: Dictionary with user data
            
        Returns:
            User instance
        """
        # Convert ISO format strings back to datetime (or handle already-datetime objects)
        def parse_datetime(value) -> Optional[datetime]:
            if value is None:
                return None
            if isinstance(value, datetime):
                return value
            if isinstance(value, str):
                return datetime.fromisoformat(value)
            return value
        
        return cls(
            id=data.get('id'),
            email=data['email'],
            username=data['username'],
            password_hash=data['password_hash'],
            tier=data.get('tier', 'FREE'),
            subscription_expires_at=parse_datetime(data.get('subscription_expires_at')),
            email_verified=data.get('email_verified', False),
            failed_login_attempts=data.get('failed_login_attempts', 0),
            locked_until=parse_datetime(data.get('locked_until')),
            created_at=parse_datetime(data.get('created_at')),
            updated_at=parse_datetime(data.get('updated_at')),
        )
    
    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username}, tier={self.tier}, email_verified={self.email_verified})"
