"""Unit tests for AuthenticationService

Tests verify:
- User registration with validation
- Login with security checks
- Session management
- Tier verification
- Subscription validation
- Password change
"""

import pytest
import os
from datetime import datetime, timedelta, timezone
from src.services.authentication import (
    AuthenticationService,
    AuthenticationError,
    InvalidCredentialsError,
    AccountLockedError,
    InvalidTierError,
    SubscriptionExpiredError,
)
from src.data.in_memory import InMemoryRepositoryFactory

# Load test passwords from environment
TEST_PASSWORD_1 = os.getenv("TEST_PASSWORD_1", "MySecure@Pass123")
TEST_PASSWORD_2 = os.getenv("TEST_PASSWORD_2", "FreshKoala@99xZ")


@pytest.fixture
def service():
    """Create authentication service with in-memory repos"""
    factory = InMemoryRepositoryFactory()
    return AuthenticationService(
        user_repository=factory.get_user_repository(),
        session_repository=factory.get_session_repository(),
    )


class TestRegistration:
    """Test user registration"""
    
    def test_register_valid_user(self, service):
        """Register a new user successfully"""
        user, token = service.register(
            email="john@example.com",
            username="john",
            password=TEST_PASSWORD_1
        )
    
    def test_register_invalid_email(self, service):
        """Register with invalid email raises error"""
        with pytest.raises(AuthenticationError):
            service.register(
                email="invalid-email",
                username="user",
                password=TEST_PASSWORD_1
            )
    
    def test_register_duplicate_email(self, service):
        """Registering with duplicate email raises error"""
        service.register(
            email="john@example.com",
            username="john",
            password=TEST_PASSWORD_1
        )
        
        with pytest.raises(AuthenticationError, match="already registered"):
            service.register(
                email="john@example.com",
                username="different",
                password=TEST_PASSWORD_1
            )
    
    def test_register_duplicate_username(self, service):
        """Registering with duplicate username raises error"""
        service.register(
            email="john@example.com",
            username="john",
            password=TEST_PASSWORD_1
        )
        
        with pytest.raises(AuthenticationError, match="already taken"):
            service.register(
                email="different@example.com",
                username="john",
                password=TEST_PASSWORD_1
            )
    
    def test_register_weak_password(self, service):
        """Registering with weak password raises error"""
        with pytest.raises(AuthenticationError, match="Password invalid"):
            service.register(
                email="john@example.com",
                username="john",
                password="weak"
            )
    
    def test_register_short_username(self, service):
        """Username less than 3 chars raises error"""
        with pytest.raises(AuthenticationError, match="at least 3"):
            service.register(
                email="john@example.com",
                username="ab",
                password=TEST_PASSWORD_1
            )


class TestLogin:
    """Test user login"""
    
    @pytest.fixture
    def registered_user(self, service):
        """Register a test user"""
        service.register(
            email="john@example.com",
            username="john",
            password=TEST_PASSWORD_1
        )
    
    def test_login_with_email(self, service, registered_user):
        """Login with email"""
        user, token = service.login("john@example.com", TEST_PASSWORD_1)
        
        assert user['email'] == "john@example.com"
        assert token is not None
        assert len(token) > 0
    
    def test_login_with_username(self, service, registered_user):
        """Login with username"""
        user, token = service.login("john", TEST_PASSWORD_1)
        
        assert user['username'] == "john"
        assert token is not None
    
    def test_login_invalid_email(self, service):
        """Login with non-existent email fails"""
        with pytest.raises(InvalidCredentialsError):
            service.login("nobody@example.com", "AnyPassword@123")
    
    def test_login_wrong_password(self, service, registered_user):
        """Login with wrong password fails"""
        with pytest.raises(InvalidCredentialsError, match="Invalid password"):
            service.login("john@example.com", "WrongPassword@123")
    
    def test_login_locks_account_after_attempts(self, service, registered_user):
        """Account locks after max failed attempts"""
        # Make max failed attempts
        for _ in range(5):
            try:
                service.login("john@example.com", "WrongPassword@123")
            except InvalidCredentialsError:
                pass
        
        # Next attempt should raise AccountLockedError
        with pytest.raises(AccountLockedError):
            service.login("john@example.com", TEST_PASSWORD_1)
    
    def test_login_resets_failed_attempts(self, service, registered_user):
        """Successful login resets failed attempts"""
        # Make 2 failed attempts
        for _ in range(2):
            try:
                service.login("john@example.com", "WrongPassword@123")
            except InvalidCredentialsError:
                pass
        
        # Login successfully
        user, token = service.login("john@example.com", TEST_PASSWORD_1)
        
        # Verify failed attempts reset
        assert user['failed_login_attempts'] == 0


class TestSession:
    """Test session management"""
    
    @pytest.fixture
    def logged_in(self, service):
        """Register and login a user"""
        service.register(
            email="john@example.com",
            username="john",
            password=TEST_PASSWORD_1
        )
        user, token = service.login("john@example.com", TEST_PASSWORD_1)
        return user, token
    
    def test_validate_session_valid(self, service, logged_in):
        """Valid session validates correctly"""
        user, token = logged_in
        
        validated_user = service.validate_session(token)
        
        assert validated_user is not None
        assert validated_user['email'] == "john@example.com"
    
    def test_validate_session_invalid(self, service):
        """Invalid token doesn't validate"""
        user = service.validate_session("invalid_token")
        assert user is None
    
    def test_logout(self, service, logged_in):
        """Logout revokes session"""
        user, token = logged_in
        
        # Verify session works before logout
        assert service.validate_session(token) is not None
        
        # Logout
        service.logout(token)
        
        # Verify session revoked
        assert service.validate_session(token) is None


class TestTierAndFeatures:
    """Test tier checking and feature access"""
    
    @pytest.fixture
    def user_with_tokens(self, service):
        """Create users of different tiers"""
        service.register(
            email="free@example.com",
            username="free_user",
            password=TEST_PASSWORD_1
        )
        free_user, free_token = service.login("free@example.com", TEST_PASSWORD_1)
        
        return free_user, free_token
    
    def test_check_tier_pass(self, service, user_with_tokens):
        """check_tier passes for same tier"""
        user, token = user_with_tokens
        
        # FREE user checking for FREE tier should pass
        assert service.check_tier(user['id'], 'FREE') is True
    
    def test_check_tier_fail(self, service, user_with_tokens):
        """check_tier fails for higher tier"""
        user, token = user_with_tokens
        
        # FREE user checking for TOP tier should fail
        with pytest.raises(InvalidTierError):
            service.check_tier(user['id'], 'TOP')
    
    def test_can_access_feature(self, service, user_with_tokens):
        """can_access_feature checks tier features"""
        user, token = user_with_tokens
        
        # FREE tier doesn't have chatbot
        assert service.can_access_feature(user['id'], 'chatbot') is False
        # But can upgrade tier
        service.upgrade_user_tier(user['id'], 'TOP')
        assert service.can_access_feature(user['id'], 'chatbot') is True
    
    def test_upgrade_user_tier(self, service, user_with_tokens):
        """Upgrade tier permanently"""
        user, token = user_with_tokens
        
        updated = service.upgrade_user_tier(user['id'], 'MIDDLE')
        
        assert updated['tier'] == 'MIDDLE'
        assert updated['subscription_expires_at'] is None
    
    def test_upgrade_user_tier_with_expiry(self, service, user_with_tokens):
        """Upgrade tier with expiry"""
        user, token = user_with_tokens
        
        updated = service.upgrade_user_tier(user['id'], 'TOP', duration_days=30)
        
        assert updated['tier'] == 'TOP'
        assert updated['subscription_expires_at'] is not None


class TestSubscription:
    """Test subscription validation"""
    
    def test_is_subscription_expired_no_expiry(self, service):
        """No expiry means subscription not expired"""
        service.register(
            email="john@example.com",
            username="john",
            password=TEST_PASSWORD_1
        )
        user, token = service.login("john@example.com", TEST_PASSWORD_1)
        
        assert service.is_subscription_expired(user['id']) is False
    
    def test_is_subscription_expired_future(self, service):
        """Future expiry means subscription not expired"""
        service.register(
            email="john@example.com",
            username="john",
            password=TEST_PASSWORD_1
        )
        user, token = service.login("john@example.com", TEST_PASSWORD_1)
        
        # Upgrade with 30 day expiry
        service.upgrade_user_tier(user['id'], 'MIDDLE', duration_days=30)
        
        assert service.is_subscription_expired(user['id']) is False
    
    def test_login_expired_subscription_fails(self, service):
        """Login with expired subscription fails"""
        service.register(
            email="john@example.com",
            username="john",
            password=TEST_PASSWORD_1
        )
        
        user_repo = service.user_repo
        user_data = user_repo.get_by_email("john@example.com")
        
        # Manually set subscription to past
        past = datetime.now(timezone.utc) - timedelta(days=1)
        user_repo.update(
            user_data['id'],
            subscription_expires_at=past.isoformat()
        )
        
        # Login should fail
        with pytest.raises(SubscriptionExpiredError):
            service.login("john@example.com", TEST_PASSWORD_1)


class TestPasswordChange:
    """Test password change"""
    
    def test_change_password(self, service):
        """Change password successfully"""
        service.register(
            email="john@example.com",
            username="john",
            password=TEST_PASSWORD_1
        )
        user, token = service.login("john@example.com", TEST_PASSWORD_1)
        
        # Change password
        result = service.change_password(
            user['id'],
            TEST_PASSWORD_1,
            TEST_PASSWORD_2
        )
        
        assert result is True
        
        # Can't login with old password
        with pytest.raises(InvalidCredentialsError):
            service.login("john@example.com", TEST_PASSWORD_1)
        
        # Can login with new password
        user, token = service.login("john@example.com", TEST_PASSWORD_2)
        assert user is not None
    
    def test_change_password_wrong_old(self, service):
        """Changing password with wrong old password fails"""
        service.register(
            email="john@example.com",
            username="john",
            password=TEST_PASSWORD_1
        )
        user, token = service.login("john@example.com", TEST_PASSWORD_1)
        
        with pytest.raises(InvalidCredentialsError, match="Current password"):
            service.change_password(
                user['id'],
                "WrongPassword@123",
                "NewPassword@456"
            )
    
    def test_change_password_weak_new(self, service):
        """Changing to weak password fails"""
        service.register(
            email="john@example.com",
            username="john",
            password=TEST_PASSWORD_1
        )
        user, token = service.login("john@example.com", TEST_PASSWORD_1)
        
        with pytest.raises(AuthenticationError, match="invalid"):
            service.change_password(
                user['id'],
                TEST_PASSWORD_1,
                "weak"
            )


class TestUserInfo:
    """Test getting user information"""
    
    def test_get_user_info(self, service):
        """Get user info by ID"""
        service.register(
            email="john@example.com",
            username="john",
            password=TEST_PASSWORD_1
        )
        user, token = service.login("john@example.com", TEST_PASSWORD_1)
        
        info = service.get_user_info(user['id'])
        
        assert info['email'] == "john@example.com"
        assert info['username'] == "john"
    
    def test_validate_user(self, service):
        """Validate user exists"""
        service.register(
            email="john@example.com",
            username="john",
            password=TEST_PASSWORD_1
        )
        user, token = service.login("john@example.com", TEST_PASSWORD_1)
        
        assert service.validate_user(user['id']) is True
        assert service.validate_user("nonexistent") is False
