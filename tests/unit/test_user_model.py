"""Unit tests for User domain model

Tests verify:
- Password hashing and verification (Argon2)
- Password validation (strength requirements)
- Tier system and feature access
- Account lockout mechanism
- Subscription management
- to_dict/from_dict serialization
"""

import pytest
from datetime import datetime, timezone, timedelta
from src.domain import User


class TestUserCreation:
    """Test user creation and initialization"""
    
    def test_create_user_with_required_fields(self):
        """Create user with minimal fields"""
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password"
        )
        
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.tier == 'FREE'
        assert user.email_verified is False
        assert user.failed_login_attempts == 0
        assert user.locked_until is None
    
    def test_create_user_with_custom_tier(self):
        """Create user with custom tier"""
        user = User(
            email="premium@example.com",
            username="premium_user",
            password_hash="hash",
            tier="TOP"
        )
        
        assert user.tier == "TOP"
    
    def test_create_user_invalid_tier_raises_error(self):
        """Creating user with invalid tier raises error"""
        with pytest.raises(ValueError):
            User(
                email="test@example.com",
                username="testuser",
                password_hash="hash",
                tier="INVALID"
            )


class TestPasswordValidation:
    """Test password validation and hashing"""
    
    def test_validate_password_strong(self):
        """Strong password passes validation"""
        is_valid, msg = User.validate_password("MySecure@Pass123")
        assert is_valid is True
    
    def test_validate_password_too_short(self):
        """Too short password fails"""
        is_valid, msg = User.validate_password("Short@1")
        assert is_valid is False
        assert "at least" in msg.lower()
    
    def test_validate_password_no_uppercase(self):
        """Password without uppercase fails"""
        is_valid, msg = User.validate_password("nosecure@pass123")
        assert is_valid is False
        assert "uppercase" in msg.lower()
    
    def test_validate_password_no_lowercase(self):
        """Password without lowercase fails"""
        is_valid, msg = User.validate_password("NOSECURE@PASS123")
        assert is_valid is False
        assert "lowercase" in msg.lower()
    
    def test_validate_password_no_digit(self):
        """Password without digit fails"""
        is_valid, msg = User.validate_password("NoSecure@Pass")
        assert is_valid is False
        assert "digit" in msg.lower()
    
    def test_validate_password_no_special_char(self):
        """Password without special character fails"""
        is_valid, msg = User.validate_password("NoSecurePass123")
        assert is_valid is False
        assert "special" in msg.lower()
    
    def test_validate_password_common_pattern(self):
        """Password with common pattern fails"""
        is_valid, msg = User.validate_password("Password@123")
        assert is_valid is False
        assert "pattern" in msg.lower()
    
    def test_set_password_with_invalid_password_raises_error(self):
        """set_password with invalid password raises error"""
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="dummy"
        )
        
        with pytest.raises(ValueError):
            user.set_password("weak")
    
    def test_set_password_hashes_correctly(self):
        """set_password hashes password with Argon2"""
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="dummy"
        )
        
        password = "MySecure@Pass123"
        user.set_password(password)
        
        # Hash should be different from plaintext
        assert user.password_hash != password
        # Hash should start with Argon2 prefix
        assert user.password_hash.startswith('$argon2')
    
    def test_check_password_correct(self):
        """check_password returns True for correct password"""
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="dummy"
        )
        
        password = "MySecure@Pass123"
        user.set_password(password)
        
        assert user.check_password(password) is True
    
    def test_check_password_incorrect(self):
        """check_password returns False for incorrect password"""
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="dummy"
        )
        
        password = "MySecure@Pass123"
        user.set_password(password)
        
        assert user.check_password("WrongPassword@123") is False
    
    def test_check_password_handles_invalid_hash(self):
        """check_password handles invalid hash gracefully"""
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="not_a_valid_hash"
        )
        
        assert user.check_password("AnyPassword@123") is False


class TestAccountLockout:
    """Test account lockout mechanism"""
    
    def test_is_account_locked_no_lockout(self):
        """Account with no lockout is not locked"""
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hash"
        )
        
        assert user.is_account_locked() is False
    
    def test_is_account_locked_currently_locked(self):
        """Account with future lockout timestamp is locked"""
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hash"
        )
        
        # Lock until future
        future = datetime.now(timezone.utc) + timedelta(hours=1)
        user.locked_until = future
        
        assert user.is_account_locked() is True
    
    def test_is_account_locked_lockout_expired(self):
        """Account with expired lockout is unlocked"""
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hash"
        )
        
        # Lock in past (expired)
        past = datetime.now(timezone.utc) - timedelta(hours=1)
        user.locked_until = past
        
        assert user.is_account_locked() is False
        # Verify auto-unlock happened
        assert user.locked_until is None
        assert user.failed_login_attempts == 0
    
    def test_record_failed_login_increments_counter(self):
        """record_failed_login increments counter"""
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hash"
        )
        
        assert user.failed_login_attempts == 0
        user.record_failed_login()
        assert user.failed_login_attempts == 1
    
    def test_record_failed_login_locks_after_max_attempts(self):
        """record_failed_login locks account after max attempts"""
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hash"
        )
        
        # Record max attempts
        for i in range(User.MAX_FAILED_ATTEMPTS):
            user.record_failed_login()
        
        # Should be locked
        assert user.is_account_locked() is True
        assert user.locked_until is not None
    
    def test_reset_failed_login_attempts(self):
        """reset_failed_login_attempts clears counter and lockout"""
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hash"
        )
        
        # Record failed attempts and lock
        for _ in range(User.MAX_FAILED_ATTEMPTS):
            user.record_failed_login()
        
        assert user.is_account_locked() is True
        
        # Reset
        user.reset_failed_login_attempts()
        
        assert user.failed_login_attempts == 0
        assert user.locked_until is None
        assert user.is_account_locked() is False


class TestTierAndFeatures:
    """Test tier system and feature access"""
    
    def test_can_access_feature_free_tier(self):
        """FREE tier can access allowed features"""
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hash",
            tier="FREE"
        )
        
        # FREE tier has sentiment_frequency set (truthy)
        assert user.can_access_feature('sentiment_frequency')
        # But portfolio_storage is False
        assert user.can_access_feature('portfolio_storage') is False
    
    def test_can_access_feature_middle_tier(self):
        """MIDDLE tier can access portfolio"""
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hash",
            tier="MIDDLE"
        )
        
        assert user.can_access_feature('portfolio_storage') is True
        assert user.can_access_feature('email_alerts') is True
        assert user.can_access_feature('chatbot') is False
    
    def test_can_access_feature_top_tier(self):
        """TOP tier can access all features"""
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hash",
            tier="TOP"
        )
        
        assert user.can_access_feature('portfolio_storage') is True
        assert user.can_access_feature('chatbot') is True
        assert user.can_access_feature('advanced_insights') is True
    
    def test_get_tier_limits(self):
        """get_tier_limits returns correct limits"""
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hash",
            tier="FREE"
        )
        
        limits = user.get_tier_limits()
        assert limits['max_stocks_simultaneous'] == 3
        assert limits['requests_per_day'] == 20
    
    def test_upgrade_tier_permanent(self):
        """upgrade_tier with no duration makes permanent"""
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hash",
            tier="FREE"
        )
        
        user.upgrade_tier("MIDDLE")
        
        assert user.tier == "MIDDLE"
        assert user.subscription_expires_at is None
    
    def test_upgrade_tier_with_expiry(self):
        """upgrade_tier with duration sets expiry"""
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hash",
            tier="FREE"
        )
        
        user.upgrade_tier("TOP", duration_days=30)
        
        assert user.tier == "TOP"
        assert user.subscription_expires_at is not None
        # Should be roughly 30 days from now (within 1 day tolerance for timing)
        days_until_expiry = (user.subscription_expires_at - datetime.now(timezone.utc)).days
        assert 29 <= days_until_expiry <= 30
    
    def test_upgrade_tier_invalid_raises_error(self):
        """upgrade_tier with invalid tier raises error"""
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hash"
        )
        
        with pytest.raises(ValueError):
            user.upgrade_tier("INVALID")


class TestSubscription:
    """Test subscription management"""
    
    def test_is_subscription_active_no_expiry(self):
        """Subscription with no expiry is active"""
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hash"
        )
        
        assert user.is_subscription_active() is True
    
    def test_is_subscription_active_future_expiry(self):
        """Subscription with future expiry is active"""
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hash"
        )
        
        future = datetime.now(timezone.utc) + timedelta(days=30)
        user.subscription_expires_at = future
        
        assert user.is_subscription_active() is True
    
    def test_is_subscription_active_expired(self):
        """Subscription with past expiry is inactive"""
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hash"
        )
        
        past = datetime.now(timezone.utc) - timedelta(days=1)
        user.subscription_expires_at = past
        
        assert user.is_subscription_active() is False


class TestSerialization:
    """Test to_dict and from_dict"""
    
    def test_to_dict(self):
        """to_dict serializes user to dictionary"""
        user = User(
            id="user-123",
            email="test@example.com",
            username="testuser",
            password_hash="hash",
            tier="MIDDLE",
            email_verified=True
        )
        
        data = user.to_dict()
        
        assert data['id'] == "user-123"
        assert data['email'] == "test@example.com"
        assert data['username'] == "testuser"
        assert data['tier'] == "MIDDLE"
        assert data['email_verified'] is True
    
    def test_from_dict(self):
        """from_dict creates user from dictionary"""
        data = {
            'id': 'user-123',
            'email': 'test@example.com',
            'username': 'testuser',
            'password_hash': 'hash',
            'tier': 'TOP',
            'email_verified': True,
            'failed_login_attempts': 2,
        }
        
        user = User.from_dict(data)
        
        assert user.id == 'user-123'
        assert user.email == 'test@example.com'
        assert user.tier == 'TOP'
        assert user.failed_login_attempts == 2
    
    def test_roundtrip_serialization(self):
        """to_dict -> from_dict preserves data"""
        original = User(
            id="user-456",
            email="john@example.com",
            username="john",
            password_hash="hash",
            tier="MIDDLE",
            email_verified=True,
            failed_login_attempts=1
        )
        
        data = original.to_dict()
        restored = User.from_dict(data)
        
        assert restored.id == original.id
        assert restored.email == original.email
        assert restored.username == original.username
        assert restored.tier == original.tier
        assert restored.email_verified == original.email_verified
        assert restored.failed_login_attempts == original.failed_login_attempts


class TestRepr:
    """Test string representation"""
    
    def test_repr(self):
        """__repr__ provides useful representation"""
        user = User(
            id="user-789",
            email="test@example.com",
            username="testuser",
            password_hash="hash",
            tier="TOP"
        )
        
        repr_str = repr(user)
        
        assert "User" in repr_str
        assert "testuser" in repr_str
        assert "TOP" in repr_str
