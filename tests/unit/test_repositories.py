"""Unit tests for in-memory repositories

Tests verify:
- Thread-safe operations
- CRUD operations work correctly
- Indexing and lookups function properly
- Error handling for duplicates
- Data integrity across operations
"""

import pytest
from datetime import datetime, timezone, timedelta
from src.data import (
    InMemoryUserRepository,
    InMemoryPortfolioRepository,
    InMemorySessionRepository,
    InMemoryUsageStatsRepository,
    InMemoryRepositoryFactory,
)


class TestInMemoryUserRepository:
    """Test user repository implementation"""
    
    @pytest.fixture
    def repo(self):
        return InMemoryUserRepository()
    
    def test_create_user(self, repo):
        """User creation stores all fields"""
        user = repo.create(
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password_123"
        )
        
        assert user['id'] is not None
        assert user['email'] == "test@example.com"
        assert user['username'] == "testuser"
        assert user['password_hash'] == "hashed_password_123"
        assert user['tier'] == 'FREE'
        assert user['email_verified'] is False
        assert user['failed_login_attempts'] == 0
        assert user['locked_until'] is None
        assert user['created_at'] is not None
        assert user['updated_at'] is not None
    
    def test_create_user_with_tier(self, repo):
        """User creation with custom tier"""
        user = repo.create(
            email="premium@example.com",
            username="premium_user",
            password_hash="hash",
            tier="TOP"
        )
        
        assert user['tier'] == "TOP"
    
    def test_create_duplicate_email_raises_error(self, repo):
        """Cannot create two users with same email"""
        repo.create(
            email="duplicate@example.com",
            username="user1",
            password_hash="hash1"
        )
        
        with pytest.raises(ValueError, match="already exists"):
            repo.create(
                email="duplicate@example.com",
                username="user2",
                password_hash="hash2"
            )
    
    def test_create_duplicate_username_raises_error(self, repo):
        """Cannot create two users with same username"""
        repo.create(
            email="user1@example.com",
            username="duplicate",
            password_hash="hash1"
        )
        
        with pytest.raises(ValueError, match="already exists"):
            repo.create(
                email="user2@example.com",
                username="duplicate",
                password_hash="hash2"
            )
    
    def test_get_by_id(self, repo):
        """Retrieve user by ID"""
        created = repo.create(
            email="test@example.com",
            username="testuser",
            password_hash="hash"
        )
        
        found = repo.get_by_id(created['id'])
        assert found is not None
        assert found['email'] == "test@example.com"
    
    def test_get_by_email(self, repo):
        """Retrieve user by email"""
        repo.create(
            email="lookup@example.com",
            username="lookupuser",
            password_hash="hash"
        )
        
        found = repo.get_by_email("lookup@example.com")
        assert found is not None
        assert found['username'] == "lookupuser"
    
    def test_get_by_username(self, repo):
        """Retrieve user by username"""
        repo.create(
            email="test@example.com",
            username="findme",
            password_hash="hash"
        )
        
        found = repo.get_by_username("findme")
        assert found is not None
        assert found['email'] == "test@example.com"
    
    def test_get_nonexistent_returns_none(self, repo):
        """Getting nonexistent user returns None"""
        assert repo.get_by_id("nonexistent") is None
        assert repo.get_by_email("none@example.com") is None
        assert repo.get_by_username("none") is None
    
    def test_update_user(self, repo):
        """Update user tier and failed attempts"""
        user = repo.create(
            email="test@example.com",
            username="testuser",
            password_hash="hash"
        )
        
        updated = repo.update(user['id'], 
                             tier="MIDDLE",
                             failed_login_attempts=3)
        
        assert updated['tier'] == "MIDDLE"
        assert updated['failed_login_attempts'] == 3
        assert updated['updated_at'] > user['created_at']
    
    def test_update_nonexistent_returns_none(self, repo):
        """Updating nonexistent user returns None"""
        result = repo.update("nonexistent", tier="TOP")
        assert result is None
    
    def test_delete_user(self, repo):
        """Delete user removes from all indexes"""
        user = repo.create(
            email="delete@example.com",
            username="deleteuser",
            password_hash="hash"
        )
        
        # Verify user exists
        assert repo.get_by_id(user['id']) is not None
        
        # Delete
        deleted = repo.delete(user['id'])
        assert deleted is True
        
        # Verify removed from all indexes
        assert repo.get_by_id(user['id']) is None
        assert repo.get_by_email("delete@example.com") is None
        assert repo.get_by_username("deleteuser") is None
    
    def test_delete_nonexistent_returns_false(self, repo):
        """Deleting nonexistent user returns False"""
        result = repo.delete("nonexistent")
        assert result is False
    
    def test_list_all_users(self, repo):
        """List all users"""
        repo.create(email="user1@example.com", username="user1", password_hash="hash1")
        repo.create(email="user2@example.com", username="user2", password_hash="hash2")
        repo.create(email="user3@example.com", username="user3", password_hash="hash3")
        
        users = repo.list_all()
        assert len(users) == 3
    
    def test_exists_by_email(self, repo):
        """Check if user exists by email"""
        repo.create(email="exists@example.com", username="user", password_hash="hash")
        
        assert repo.exists(email="exists@example.com") is True
        assert repo.exists(email="notexists@example.com") is False
    
    def test_exists_by_username(self, repo):
        """Check if user exists by username"""
        repo.create(email="test@example.com", username="existsuser", password_hash="hash")
        
        assert repo.exists(username="existsuser") is True
        assert repo.exists(username="notexistsuser") is False


class TestInMemoryPortfolioRepository:
    """Test portfolio repository implementation"""
    
    @pytest.fixture
    def repo(self):
        return InMemoryPortfolioRepository()
    
    def test_create_portfolio_entry(self, repo):
        """Add stock to portfolio"""
        entry = repo.create(user_id="user123", ticker="AAPL", quantity=10, purchase_price=150.0)
        
        assert entry['id'] is not None
        assert entry['user_id'] == "user123"
        assert entry['ticker'] == "AAPL"
        assert entry['quantity'] == 10
        assert entry['purchase_price'] == 150.0
        assert entry['created_at'] is not None
    
    def test_get_user_portfolio(self, repo):
        """Get all stocks for a user"""
        repo.create(user_id="user123", ticker="AAPL", quantity=10)
        repo.create(user_id="user123", ticker="GOOGL", quantity=5)
        repo.create(user_id="user456", ticker="MSFT", quantity=20)
        
        portfolio = repo.get_user_portfolio("user123")
        assert len(portfolio) == 2
        tickers = {entry['ticker'] for entry in portfolio}
        assert tickers == {"AAPL", "GOOGL"}
    
    def test_get_user_portfolio_empty(self, repo):
        """Get portfolio for user with no stocks"""
        portfolio = repo.get_user_portfolio("nonexistent")
        assert portfolio == []
    
    def test_update_portfolio_entry(self, repo):
        """Update quantity or price"""
        entry = repo.create(user_id="user123", ticker="AAPL", quantity=10, purchase_price=150.0)
        
        updated = repo.update(entry['id'], quantity=15, purchase_price=155.0)
        assert updated['quantity'] == 15
        assert updated['purchase_price'] == 155.0
    
    def test_delete_portfolio_entry(self, repo):
        """Remove stock from portfolio"""
        entry = repo.create(user_id="user123", ticker="AAPL", quantity=10)
        
        deleted = repo.delete(entry['id'])
        assert deleted is True
        
        # Verify removed
        portfolio = repo.get_user_portfolio("user123")
        assert len(portfolio) == 0
    
    def test_delete_user_portfolio(self, repo):
        """Clear entire user portfolio"""
        repo.create(user_id="user123", ticker="AAPL", quantity=10)
        repo.create(user_id="user123", ticker="GOOGL", quantity=5)
        
        deleted = repo.delete_user_portfolio("user123")
        assert deleted is True
        
        portfolio = repo.get_user_portfolio("user123")
        assert len(portfolio) == 0
    
    def test_list_all_portfolio_entries(self, repo):
        """List all portfolio entries"""
        repo.create(user_id="user1", ticker="AAPL", quantity=10)
        repo.create(user_id="user2", ticker="GOOGL", quantity=5)
        
        all_entries = repo.list_all()
        assert len(all_entries) == 2


class TestInMemorySessionRepository:
    """Test session repository implementation"""
    
    @pytest.fixture
    def repo(self):
        return InMemorySessionRepository()
    
    def test_create_session(self, repo):
        """Create new session"""
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        session = repo.create(
            user_id="user123",
            session_token="token_abc123",
            expires_at=expires_at
        )
        
        assert session['id'] is not None
        assert session['user_id'] == "user123"
        assert session['session_token'] == "token_abc123"
        assert session['revoked'] is False
    
    def test_get_session_by_token(self, repo):
        """Retrieve session by token"""
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        repo.create(user_id="user123", session_token="token_abc", expires_at=expires_at)
        
        session = repo.get_by_token("token_abc")
        assert session is not None
        assert session['user_id'] == "user123"
    
    def test_validate_token_valid(self, repo):
        """Valid token validates successfully"""
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        repo.create(user_id="user123", session_token="valid_token", expires_at=expires_at)
        
        assert repo.validate_token("valid_token") is True
    
    def test_validate_token_expired(self, repo):
        """Expired token fails validation"""
        expires_at = datetime.now(timezone.utc) - timedelta(hours=1)  # Expired
        repo.create(user_id="user123", session_token="expired_token", expires_at=expires_at)
        
        assert repo.validate_token("expired_token") is False
    
    def test_validate_token_nonexistent(self, repo):
        """Nonexistent token fails validation"""
        assert repo.validate_token("nonexistent") is False
    
    def test_validate_token_revoked(self, repo):
        """Revoked token fails validation"""
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        repo.create(user_id="user123", session_token="revoked_token", expires_at=expires_at)
        
        # Revoke it
        repo.revoke("revoked_token")
        
        # Should now fail validation
        assert repo.validate_token("revoked_token") is False
    
    def test_revoke_session(self, repo):
        """Revoke a session"""
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        repo.create(user_id="user123", session_token="revoke_me", expires_at=expires_at)
        
        revoked = repo.revoke("revoke_me")
        assert revoked is True
        
        session = repo.get_by_token("revoke_me")
        assert session['revoked'] is True
        assert session['revoked_at'] is not None
    
    def test_delete_user_sessions(self, repo):
        """Logout everywhere (delete all user sessions)"""
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        repo.create(user_id="user123", session_token="token1", expires_at=expires_at)
        repo.create(user_id="user123", session_token="token2", expires_at=expires_at)
        repo.create(user_id="user456", session_token="token3", expires_at=expires_at)
        
        deleted = repo.delete_user_sessions("user123")
        assert deleted is True
        
        # User123 sessions should be gone
        assert repo.get_by_token("token1") is None
        assert repo.get_by_token("token2") is None
        # But user456 session should remain
        assert repo.get_by_token("token3") is not None
    
    def test_cleanup_expired_sessions(self, repo):
        """Remove all expired sessions"""
        now = datetime.now(timezone.utc)
        
        # Create valid session
        repo.create(user_id="user1", session_token="valid", expires_at=now + timedelta(hours=24))
        
        # Create expired sessions
        repo.create(user_id="user2", session_token="expired1", expires_at=now - timedelta(hours=1))
        repo.create(user_id="user3", session_token="expired2", expires_at=now - timedelta(hours=2))
        
        # Cleanup
        count = repo.cleanup_expired()
        assert count == 2
        
        # Valid should remain
        assert repo.get_by_token("valid") is not None
        # Expired should be gone
        assert repo.get_by_token("expired1") is None
        assert repo.get_by_token("expired2") is None
    
    def test_list_all_sessions(self, repo):
        """List all sessions"""
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        repo.create(user_id="user1", session_token="token1", expires_at=expires_at)
        repo.create(user_id="user2", session_token="token2", expires_at=expires_at)
        
        sessions = repo.list_all()
        assert len(sessions) == 2


class TestInMemoryUsageStatsRepository:
    """Test usage stats repository implementation"""
    
    @pytest.fixture
    def repo(self):
        return InMemoryUsageStatsRepository()
    
    def test_create_stats(self, repo):
        """Create stats for a date"""
        stats = repo.create(user_id="user123", date="2025-10-19")
        
        assert stats['id'] is not None
        assert stats['user_id'] == "user123"
        assert stats['date'] == "2025-10-19"
        assert stats['requests_used'] == 0
        assert stats['stocks_analyzed'] == 0
    
    def test_get_today(self, repo):
        """Get today's stats"""
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        repo.create(user_id="user123", date=today)
        
        stats = repo.get_today("user123")
        assert stats is not None
        assert stats['date'] == today
    
    def test_get_today_nonexistent(self, repo):
        """Get today's stats when none exist"""
        stats = repo.get_today("user123")
        assert stats is None
    
    def test_increment_requests(self, repo):
        """Increment request count"""
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        repo.create(user_id="user123", date=today)
        
        stats = repo.increment_requests("user123", amount=5)
        assert stats['requests_used'] == 5
        
        # Increment again
        stats = repo.increment_requests("user123", amount=3)
        assert stats['requests_used'] == 8
    
    def test_increment_requests_creates_today(self, repo):
        """Increment requests creates today's stats if needed"""
        stats = repo.increment_requests("user123", amount=1)
        assert stats is not None
        assert stats['requests_used'] == 1
    
    def test_increment_stocks(self, repo):
        """Increment stocks analyzed"""
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        repo.create(user_id="user123", date=today)
        
        stats = repo.increment_stocks("user123", amount=2)
        assert stats['stocks_analyzed'] == 2
    
    def test_update_stats(self, repo):
        """Update stats fields"""
        stats = repo.create(user_id="user123", date="2025-10-19")
        
        updated = repo.update(stats['id'], requests_used=10, stocks_analyzed=5)
        assert updated['requests_used'] == 10
        assert updated['stocks_analyzed'] == 5
    
    def test_delete_stats(self, repo):
        """Delete stats entry"""
        stats = repo.create(user_id="user123", date="2025-10-19")
        
        deleted = repo.delete(stats['id'])
        assert deleted is True
        
        # Should be gone
        found = repo.get_by_id(stats['id'])
        assert found is None
    
    def test_list_all_stats(self, repo):
        """List all stats entries"""
        repo.create(user_id="user1", date="2025-10-19")
        repo.create(user_id="user2", date="2025-10-19")
        
        stats = repo.list_all()
        assert len(stats) == 2


class TestInMemoryRepositoryFactory:
    """Test repository factory"""
    
    def test_factory_creates_all_repositories(self):
        """Factory creates all four repository types"""
        factory = InMemoryRepositoryFactory()
        
        user_repo = factory.get_user_repository()
        portfolio_repo = factory.get_portfolio_repository()
        session_repo = factory.get_session_repository()
        usage_repo = factory.get_usage_stats_repository()
        
        assert user_repo is not None
        assert portfolio_repo is not None
        assert session_repo is not None
        assert usage_repo is not None
    
    def test_factory_returns_same_instances(self):
        """Factory returns same instance on multiple calls"""
        factory = InMemoryRepositoryFactory()
        
        user_repo1 = factory.get_user_repository()
        user_repo2 = factory.get_user_repository()
        
        assert user_repo1 is user_repo2
