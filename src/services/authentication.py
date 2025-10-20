"""
Authentication Service

Core authentication logic with dependency injection.
Works with any persistence layer (in-memory, SQLite, SQLAlchemy, etc.)

Orchestrates:
- User registration with validation
- Login with security checks and lockout
- Session management
- Tier verification
- Subscription validation
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple
import secrets

from src.domain import User
from src.data.repositories import UserRepository, SessionRepository


class AuthenticationError(Exception):
    """Base exception for authentication errors"""
    pass


class InvalidCredentialsError(AuthenticationError):
    """Raised when email or password is invalid"""
    pass


class AccountLockedError(AuthenticationError):
    """Raised when account is locked due to failed attempts"""
    pass


class InvalidTierError(AuthenticationError):
    """Raised when user doesn't have required tier"""
    pass


class SubscriptionExpiredError(AuthenticationError):
    """Raised when subscription has expired"""
    pass


class AuthenticationService:
    """Authentication and authorization service
    
    Uses dependency injection for repositories, allowing any persistence
    implementation to be used without changing this service.
    """
    
    # Session configuration
    SESSION_DURATION_HOURS = 24
    SESSION_TOKEN_LENGTH = 32  # bytes for token generation
    
    def __init__(
        self,
        user_repository: UserRepository,
        session_repository: SessionRepository
    ):
        """Initialize service with repository dependencies
        
        Args:
            user_repository: UserRepository implementation
            session_repository: SessionRepository implementation
        """
        self.user_repo = user_repository
        self.session_repo = session_repository
    
    def register(
        self,
        email: str,
        username: str,
        password: str
    ) -> Tuple[dict, str]:
        """Register a new user
        
        Args:
            email: User email (must be unique)
            username: User username (must be unique)
            password: User password (will be validated and hashed)
            
        Returns:
            (user_dict, session_token) tuple
            
        Raises:
            AuthenticationError: If email/username exists or password invalid
        """
        # Validate inputs
        if not email or '@' not in email:
            raise AuthenticationError("Invalid email format")
        if not username or len(username) < 3:
            raise AuthenticationError("Username must be at least 3 characters")
        
        # Check if user exists
        if self.user_repo.exists(email=email):
            raise AuthenticationError("Email already registered")
        if self.user_repo.exists(username=username):
            raise AuthenticationError("Username already taken")
        
        # Create user (password validated in User.set_password)
        try:
            user = User(
                email=email,
                username=username,
                password_hash="dummy",  # Will be overwritten
                tier='FREE'
            )
            user.set_password(password)  # Validates and hashes
            user.created_at = datetime.now(timezone.utc)
            user.updated_at = user.created_at
            
        except ValueError as e:
            raise AuthenticationError(f"Password invalid: {str(e)}")
        
        # Persist user
        user_data = self.user_repo.create(
            email=user.email,
            username=user.username,
            password_hash=user.password_hash,
            tier=user.tier,
            email_verified=user.email_verified
        )
        
        # Create session token (optional on registration, but useful for auto-login)
        session_token = self._generate_session_token()
        expires_at = datetime.now(timezone.utc) + timedelta(hours=self.SESSION_DURATION_HOURS)
        self.session_repo.create(
            user_id=user_data['id'],
            session_token=session_token,
            expires_at=expires_at
        )
        
        return user_data, session_token
    
    def login(
        self,
        email_or_username: str,
        password: str
    ) -> Tuple[dict, str]:
        """Login user and create session
        
        Args:
            email_or_username: Email or username
            password: Password to verify
            
        Returns:
            (user_dict, session_token) tuple
            
        Raises:
            InvalidCredentialsError: If credentials invalid
            AccountLockedError: If account is locked
            SubscriptionExpiredError: If subscription expired
        """
        # Find user
        user_data = self.user_repo.get_by_email(email_or_username)
        if not user_data:
            user_data = self.user_repo.get_by_username(email_or_username)
        
        if not user_data:
            raise InvalidCredentialsError("Invalid email or username")
        
        # Reconstruct user domain object
        user = User.from_dict(user_data)
        
        # Check if locked
        if user.is_account_locked():
            raise AccountLockedError(
                f"Account locked. Try again in {user.LOCKOUT_DURATION_MINUTES} minutes"
            )
        
        # Verify password
        if not user.check_password(password):
            user.record_failed_login()
            self.user_repo.update(
                user.id,
                failed_login_attempts=user.failed_login_attempts,
                locked_until=user.locked_until.isoformat() if user.locked_until else None
            )
            raise InvalidCredentialsError("Invalid password")
        
        # Reset failed attempts on successful login
        user.reset_failed_login_attempts()
        self.user_repo.update(
            user.id,
            failed_login_attempts=user.failed_login_attempts,
            locked_until=None
        )
        
        # Check subscription
        if not user.is_subscription_active():
            raise SubscriptionExpiredError("Your subscription has expired")
        
        # Create session
        session_token = self._generate_session_token()
        expires_at = datetime.now(timezone.utc) + timedelta(hours=self.SESSION_DURATION_HOURS)
        
        session_data = self.session_repo.create(
            user_id=user.id,
            session_token=session_token,
            expires_at=expires_at
        )
        
        return user_data, session_token
    
    def logout(self, session_token: str) -> bool:
        """Logout user by revoking session
        
        Args:
            session_token: Session token to revoke
            
        Returns:
            bool: True if logout successful
        """
        return self.session_repo.revoke(session_token)
    
    def validate_session(self, session_token: str) -> Optional[dict]:
        """Validate session token and return user
        
        Args:
            session_token: Token to validate
            
        Returns:
            User dict if token valid, None otherwise
        """
        if not self.session_repo.validate_token(session_token):
            return None
        
        session = self.session_repo.get_by_token(session_token)
        if not session:
            return None
        
        user = self.user_repo.get_by_id(session['user_id'])
        return user
    
    def validate_user(self, user_id: str) -> bool:
        """Check if user exists and is active
        
        Args:
            user_id: User ID to validate
            
        Returns:
            bool: True if user exists
        """
        user = self.user_repo.get_by_id(user_id)
        return user is not None
    
    def check_tier(self, user_id: str, required_tier: str) -> bool:
        """Check if user has required tier
        
        Args:
            user_id: User ID to check
            required_tier: Required tier ('FREE', 'MIDDLE', 'TOP')
            
        Returns:
            bool: True if user has required tier or higher
            
        Raises:
            InvalidTierError: If user doesn't meet tier requirement
        """
        user_data = self.user_repo.get_by_id(user_id)
        if not user_data:
            raise InvalidTierError("User not found")
        
        user = User.from_dict(user_data)
        
        tier_order = {'FREE': 0, 'MIDDLE': 1, 'TOP': 2}
        user_level = tier_order.get(user.tier, 0)
        required_level = tier_order.get(required_tier, 0)
        
        if user_level < required_level:
            raise InvalidTierError(
                f"Tier '{required_tier}' required, you have '{user.tier}'"
            )
        
        return True
    
    def can_access_feature(self, user_id: str, feature: str) -> bool:
        """Check if user can access a feature
        
        Args:
            user_id: User ID
            feature: Feature name
            
        Returns:
            bool: True if user can access feature
        """
        user_data = self.user_repo.get_by_id(user_id)
        if not user_data:
            return False
        
        user = User.from_dict(user_data)
        return bool(user.can_access_feature(feature))
    
    def is_subscription_expired(self, user_id: str) -> bool:
        """Check if user's subscription is expired
        
        Args:
            user_id: User ID
            
        Returns:
            bool: True if subscription is expired
        """
        user_data = self.user_repo.get_by_id(user_id)
        if not user_data:
            return False
        
        user = User.from_dict(user_data)
        return not user.is_subscription_active()
    
    def upgrade_user_tier(
        self,
        user_id: str,
        new_tier: str,
        duration_days: Optional[int] = None
    ) -> dict:
        """Upgrade user to a new tier
        
        Args:
            user_id: User ID to upgrade
            new_tier: Target tier
            duration_days: Duration in days (None = permanent)
            
        Returns:
            Updated user dict
            
        Raises:
            AuthenticationError: If user not found or tier invalid
        """
        user_data = self.user_repo.get_by_id(user_id)
        if not user_data:
            raise AuthenticationError("User not found")
        
        user = User.from_dict(user_data)
        
        # Validate new tier
        try:
            user.upgrade_tier(new_tier, duration_days)
        except ValueError as e:
            raise AuthenticationError(str(e))
        
        # Persist update
        update_data = {
            'tier': user.tier,
            'subscription_expires_at': user.subscription_expires_at.isoformat() if user.subscription_expires_at else None
        }
        
        updated = self.user_repo.update(user_id, **update_data)
        return updated
    
    def get_user_info(self, user_id: str) -> Optional[dict]:
        """Get user information
        
        Args:
            user_id: User ID
            
        Returns:
            User dict or None if not found
        """
        return self.user_repo.get_by_id(user_id)
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Change user password
        
        Args:
            user_id: User ID
            old_password: Current password (must be correct)
            new_password: New password (will be validated)
            
        Returns:
            bool: True if password changed
            
        Raises:
            InvalidCredentialsError: If old password is wrong
            AuthenticationError: If new password invalid
        """
        user_data = self.user_repo.get_by_id(user_id)
        if not user_data:
            raise AuthenticationError("User not found")
        
        user = User.from_dict(user_data)
        
        # Verify old password
        if not user.check_password(old_password):
            raise InvalidCredentialsError("Current password is incorrect")
        
        # Validate and set new password
        try:
            user.set_password(new_password)
        except ValueError as e:
            raise AuthenticationError(f"New password invalid: {str(e)}")
        
        # Persist new password hash
        self.user_repo.update(user_id, password_hash=user.password_hash)
        
        return True
    
    @staticmethod
    def _generate_session_token(length: int = SESSION_TOKEN_LENGTH) -> str:
        """Generate secure random session token
        
        Args:
            length: Token length in bytes
            
        Returns:
            Hex-encoded random token
        """
        return secrets.token_hex(length)
