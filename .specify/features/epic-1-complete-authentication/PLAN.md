# PLAN: Epic 1 - Complete Authentication & Tier-Based Access Control

**Epic ID**: Epic 1  
**Status**: READY FOR IMPLEMENTATION  
**Estimated Duration**: 10-12 days  
**Starting Point**: feature/authentication-tier-system branch (~40% complete)

---

## 🎯 Implementation Strategy

### Approach
- **Test-First Development**: Write tests before implementation
- **Incremental Delivery**: Each phase produces deployable increments
- **Clean Architecture**: Repository Pattern + Dependency Injection from the start
- **Database First**: Complete schema and migrations before business logic
- **Security by Default**: Input validation, password hashing, CSRF protection built-in

### Migration Strategy (Strangler Fig Pattern)
Since ~40% exists on feature branch, we'll:
1. Audit existing auth code first (Day 1)
2. Extract reusable components
3. Build new features alongside existing code
4. Gradually replace old patterns with Repository/DI
5. Remove legacy auth code only when new system is proven

---

## 📅 Phase-by-Phase Implementation Plan

## **Phase 1: Foundation & User Management (Days 1-3)**

### **Day 1: Database & Repository Setup**

#### Morning: Schema Design & Migrations
**Files to Create:**
- `src/data/migrations/001_create_users_table.sql`
- `src/data/migrations/002_create_sessions_table.sql`
- `src/data/migrations/003_create_user_activity_log.sql`
- `src/data/schema.sql` (consolidated schema)

**Database Schema:**
```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    subscription_tier VARCHAR(20) DEFAULT 'free',
    is_active BOOLEAN DEFAULT 1,
    email_verified BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Sessions table
CREATE TABLE user_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Activity log
CREATE TABLE user_activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    action VARCHAR(100) NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_tier ON users(subscription_tier);
CREATE INDEX idx_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_activity_user_id ON user_activity_log(user_id);
```

**Files to Create:**
- `src/data/models/user.py` - SQLAlchemy User model
- `src/data/models/session.py` - SQLAlchemy Session model
- `src/data/models/__init__.py` - Model exports

**Tests to Write:**
- `tests/data/test_user_model.py` - User model validation tests
- `tests/data/test_migrations.py` - Migration rollback tests

**Acceptance Criteria:**
- ✅ All tables created with proper constraints
- ✅ Migrations are reversible (up/down)
- ✅ SQLAlchemy models map correctly to schema
- ✅ Foreign keys cascade properly

#### Afternoon: Repository Layer
**Files to Create:**
- `src/data/repositories/user_repository.py`
- `src/data/repositories/session_repository.py`
- `src/data/repositories/base_repository.py`
- `src/data/repositories/__init__.py`

**Interface (user_repository.py):**
```python
from abc import ABC, abstractmethod
from typing import Optional, List
from src.data.models.user import User

class IUserRepository(ABC):
    @abstractmethod
    def create(self, email: str, password_hash: str, full_name: str) -> User:
        pass
    
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        pass
    
    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        pass
    
    @abstractmethod
    def update_tier(self, user_id: int, tier: str) -> bool:
        pass
    
    @abstractmethod
    def update_last_login(self, user_id: int) -> bool:
        pass
    
    @abstractmethod
    def verify_email(self, user_id: int) -> bool:
        pass
    
    @abstractmethod
    def deactivate(self, user_id: int) -> bool:
        pass

class UserRepository(IUserRepository):
    def __init__(self, db_session):
        self.db = db_session
    
    # Implementation...
```

**Tests to Write:**
- `tests/data/repositories/test_user_repository.py` - Full CRUD + edge cases
- `tests/data/repositories/test_session_repository.py` - Session lifecycle

**Acceptance Criteria:**
- ✅ All repository methods tested with in-memory SQLite
- ✅ Proper error handling for duplicate emails
- ✅ Transaction rollback on failures
- ✅ Connection pooling configured

---

### **Day 2: Authentication Service**

#### Morning: Password & Token Security
**Files to Create:**
- `src/core/auth/password_service.py`
- `src/core/auth/token_service.py`
- `src/core/auth/__init__.py`

**Implementation (password_service.py):**
```python
import bcrypt
import secrets
from typing import Tuple

class PasswordService:
    """Secure password hashing and verification"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt with salt"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            password_hash.encode('utf-8')
        )
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate cryptographically secure random token"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, str]:
        """Validate password meets security requirements"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        if not any(c.isupper() for c in password):
            return False, "Password must contain uppercase letter"
        if not any(c.islower() for c in password):
            return False, "Password must contain lowercase letter"
        if not any(c.isdigit() for c in password):
            return False, "Password must contain number"
        return True, "Password is strong"
```

**Tests to Write:**
- `tests/core/auth/test_password_service.py` - Hash/verify, strength validation
- `tests/core/auth/test_token_service.py` - Token generation, expiry

**Acceptance Criteria:**
- ✅ bcrypt with 12 rounds (OWASP compliant)
- ✅ Password strength enforced (8+ chars, mixed case, numbers)
- ✅ Tokens are cryptographically secure (secrets module)
- ✅ All edge cases tested (None, empty, Unicode)

#### Afternoon: Authentication Service
**Files to Create:**
- `src/core/auth/authentication_service.py`
- `src/core/auth/exceptions.py`

**Implementation (authentication_service.py):**
```python
from datetime import datetime, timedelta
from typing import Optional, Tuple
from src.data.repositories.user_repository import IUserRepository
from src.data.repositories.session_repository import ISessionRepository
from src.core.auth.password_service import PasswordService
from src.core.auth.exceptions import *

class AuthenticationService:
    """Handles user registration, login, session management"""
    
    def __init__(
        self,
        user_repo: IUserRepository,
        session_repo: ISessionRepository,
        password_service: PasswordService
    ):
        self.user_repo = user_repo
        self.session_repo = session_repo
        self.password_service = password_service
    
    def register(
        self,
        email: str,
        password: str,
        full_name: str
    ) -> Tuple[bool, str]:
        """Register new user with validation"""
        # Validate email
        if not self._is_valid_email(email):
            raise InvalidEmailError(f"Invalid email: {email}")
        
        # Check if user exists
        if self.user_repo.find_by_email(email):
            raise UserAlreadyExistsError(f"User {email} already exists")
        
        # Validate password strength
        valid, message = self.password_service.validate_password_strength(password)
        if not valid:
            raise WeakPasswordError(message)
        
        # Hash password and create user
        password_hash = self.password_service.hash_password(password)
        user = self.user_repo.create(email, password_hash, full_name)
        
        return True, f"User {user.id} created successfully"
    
    def login(
        self,
        email: str,
        password: str,
        ip_address: Optional[str] = None
    ) -> Tuple[str, int]:
        """Authenticate user and create session"""
        user = self.user_repo.find_by_email(email)
        
        if not user:
            raise UserNotFoundError(f"No user found with email {email}")
        
        if not user.is_active:
            raise UserDeactivatedError("Account is deactivated")
        
        if not self.password_service.verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid credentials")
        
        # Create session
        session_token = self.password_service.generate_secure_token()
        expires_at = datetime.utcnow() + timedelta(days=7)
        
        self.session_repo.create(user.id, session_token, expires_at)
        self.user_repo.update_last_login(user.id)
        
        return session_token, user.id
    
    def logout(self, session_token: str) -> bool:
        """Invalidate session"""
        return self.session_repo.delete(session_token)
    
    def validate_session(self, session_token: str) -> Optional[int]:
        """Validate session and return user_id"""
        session = self.session_repo.find_by_token(session_token)
        
        if not session:
            return None
        
        if session.expires_at < datetime.utcnow():
            self.session_repo.delete(session_token)
            return None
        
        return session.user_id
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
```

**Tests to Write:**
- `tests/core/auth/test_authentication_service.py` - Full registration/login flow
- `tests/core/auth/test_session_validation.py` - Session expiry, invalid tokens

**Acceptance Criteria:**
- ✅ Registration validates email format
- ✅ Login fails gracefully with clear errors
- ✅ Sessions expire after 7 days
- ✅ Deactivated users cannot log in
- ✅ All exceptions tested

---

### **Day 3: Flask Routes & Dependency Injection**

#### Morning: DI Container Setup
**Files to Create:**
- `src/core/di/container.py`
- `src/core/di/__init__.py`

**Implementation (container.py):**
```python
from dataclasses import dataclass
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from src.data.repositories.user_repository import UserRepository
from src.data.repositories.session_repository import SessionRepository
from src.core.auth.password_service import PasswordService
from src.core.auth.authentication_service import AuthenticationService
from src.core.auth.authorization_service import AuthorizationService

@dataclass
class ServiceContainer:
    """Dependency Injection Container"""
    
    # Repositories
    user_repository: UserRepository
    session_repository: SessionRepository
    
    # Services
    password_service: PasswordService
    authentication_service: AuthenticationService
    authorization_service: AuthorizationService
    
    @classmethod
    def create(cls, database_url: str):
        """Factory method to create configured container"""
        # Database setup
        engine = create_engine(database_url)
        session_factory = sessionmaker(bind=engine)
        db_session = scoped_session(session_factory)
        
        # Repositories
        user_repo = UserRepository(db_session)
        session_repo = SessionRepository(db_session)
        
        # Services
        password_service = PasswordService()
        auth_service = AuthenticationService(user_repo, session_repo, password_service)
        authz_service = AuthorizationService(user_repo)
        
        return cls(
            user_repository=user_repo,
            session_repository=session_repo,
            password_service=password_service,
            authentication_service=auth_service,
            authorization_service=authz_service
        )
```

**Tests to Write:**
- `tests/core/di/test_container.py` - Container initialization, singleton behavior

#### Afternoon: Flask Routes
**Files to Create:**
- `src/web/routes/auth.py` - Authentication routes
- `src/web/decorators/auth_required.py` - Session validation decorator
- `src/web/forms/registration_form.py` - WTForms validation

**Implementation (auth.py):**
```python
from flask import Blueprint, request, jsonify, session
from src.core.di.container import ServiceContainer
from src.core.auth.exceptions import *

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Inject container via Flask app config
def get_container():
    from flask import current_app
    return current_app.config['SERVICE_CONTAINER']

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register new user"""
    data = request.get_json()
    container = get_container()
    
    try:
        success, message = container.authentication_service.register(
            email=data['email'],
            password=data['password'],
            full_name=data.get('full_name', '')
        )
        return jsonify({'success': True, 'message': message}), 201
    
    except (InvalidEmailError, WeakPasswordError, UserAlreadyExistsError) as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and create session"""
    data = request.get_json()
    container = get_container()
    
    try:
        session_token, user_id = container.authentication_service.login(
            email=data['email'],
            password=data['password'],
            ip_address=request.remote_addr
        )
        
        # Store session token in Flask session (cookie-based)
        session['session_token'] = session_token
        session['user_id'] = user_id
        
        return jsonify({
            'success': True,
            'session_token': session_token,
            'user_id': user_id
        }), 200
    
    except (UserNotFoundError, InvalidCredentialsError, UserDeactivatedError) as e:
        return jsonify({'success': False, 'error': str(e)}), 401
    
    except Exception as e:
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user and invalidate session"""
    container = get_container()
    session_token = session.get('session_token')
    
    if session_token:
        container.authentication_service.logout(session_token)
    
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out'}), 200

@auth_bp.route('/validate', methods=['GET'])
def validate_session():
    """Check if current session is valid"""
    container = get_container()
    session_token = session.get('session_token')
    
    if not session_token:
        return jsonify({'valid': False}), 401
    
    user_id = container.authentication_service.validate_session(session_token)
    
    if user_id:
        return jsonify({'valid': True, 'user_id': user_id}), 200
    else:
        session.clear()
        return jsonify({'valid': False}), 401
```

**Decorator (auth_required.py):**
```python
from functools import wraps
from flask import session, jsonify, current_app

def auth_required(f):
    """Decorator to require valid session"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_token = session.get('session_token')
        
        if not session_token:
            return jsonify({'error': 'Authentication required'}), 401
        
        container = current_app.config['SERVICE_CONTAINER']
        user_id = container.authentication_service.validate_session(session_token)
        
        if not user_id:
            session.clear()
            return jsonify({'error': 'Invalid or expired session'}), 401
        
        # Attach user_id to kwargs for use in route
        kwargs['user_id'] = user_id
        return f(*args, **kwargs)
    
    return decorated_function
```

**Tests to Write:**
- `tests/web/routes/test_auth_routes.py` - All endpoints, error cases
- `tests/web/decorators/test_auth_required.py` - Decorator behavior

**Acceptance Criteria:**
- ✅ All routes return proper HTTP status codes
- ✅ Session tokens stored in secure cookies (httpOnly, secure)
- ✅ CSRF protection enabled via Flask-WTF
- ✅ Integration tests with test client

---

## **Phase 2: Tier-Based Authorization (Days 4-5)**

### **Day 4: Tier Definitions & Authorization Service**

#### Morning: Tier Configuration
**Files to Create:**
- `src/config/tiers.py` - Tier definitions and feature flags
- `src/core/auth/tier_config.py` - Tier validation

**Implementation (tiers.py):**
```python
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List

class SubscriptionTier(Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

@dataclass
class TierFeatures:
    """Feature flags for each tier"""
    max_tickers_per_analysis: int
    max_daily_analyses: int
    max_concurrent_chat_sessions: int
    advanced_ai_models: bool
    api_access: bool
    export_formats: List[str]
    data_retention_days: int
    priority_support: bool

# Tier feature matrix
TIER_FEATURES: Dict[SubscriptionTier, TierFeatures] = {
    SubscriptionTier.FREE: TierFeatures(
        max_tickers_per_analysis=1,
        max_daily_analyses=3,
        max_concurrent_chat_sessions=1,
        advanced_ai_models=False,
        api_access=False,
        export_formats=['json'],
        data_retention_days=7,
        priority_support=False
    ),
    SubscriptionTier.BASIC: TierFeatures(
        max_tickers_per_analysis=5,
        max_daily_analyses=20,
        max_concurrent_chat_sessions=3,
        advanced_ai_models=True,
        api_access=False,
        export_formats=['json', 'csv'],
        data_retention_days=30,
        priority_support=False
    ),
    SubscriptionTier.PREMIUM: TierFeatures(
        max_tickers_per_analysis=20,
        max_daily_analyses=100,
        max_concurrent_chat_sessions=10,
        advanced_ai_models=True,
        api_access=True,
        export_formats=['json', 'csv', 'pdf'],
        data_retention_days=365,
        priority_support=True
    ),
    SubscriptionTier.ENTERPRISE: TierFeatures(
        max_tickers_per_analysis=100,
        max_daily_analyses=-1,  # unlimited
        max_concurrent_chat_sessions=-1,  # unlimited
        advanced_ai_models=True,
        api_access=True,
        export_formats=['json', 'csv', 'pdf', 'excel'],
        data_retention_days=-1,  # unlimited
        priority_support=True
    )
}
```

#### Afternoon: Authorization Service
**Files to Create:**
- `src/core/auth/authorization_service.py`
- `src/data/repositories/usage_repository.py` - Track daily usage

**Implementation (authorization_service.py):**
```python
from src.data.repositories.user_repository import IUserRepository
from src.data.repositories.usage_repository import IUsageRepository
from src.config.tiers import SubscriptionTier, TIER_FEATURES
from src.core.auth.exceptions import InsufficientPermissionsError

class AuthorizationService:
    """Handles tier-based access control"""
    
    def __init__(
        self,
        user_repo: IUserRepository,
        usage_repo: IUsageRepository
    ):
        self.user_repo = user_repo
        self.usage_repo = usage_repo
    
    def check_feature_access(
        self,
        user_id: int,
        feature: str
    ) -> bool:
        """Check if user's tier allows feature"""
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return False
        
        tier = SubscriptionTier(user.subscription_tier)
        features = TIER_FEATURES[tier]
        
        return getattr(features, feature, False)
    
    def check_analysis_limit(self, user_id: int) -> bool:
        """Check if user has remaining analyses today"""
        user = self.user_repo.find_by_id(user_id)
        tier = SubscriptionTier(user.subscription_tier)
        features = TIER_FEATURES[tier]
        
        if features.max_daily_analyses == -1:
            return True  # Unlimited
        
        today_count = self.usage_repo.get_today_analysis_count(user_id)
        return today_count < features.max_daily_analyses
    
    def increment_usage(self, user_id: int, usage_type: str):
        """Track usage for rate limiting"""
        self.usage_repo.record_usage(user_id, usage_type)
    
    def get_tier_info(self, user_id: int) -> dict:
        """Get user's tier and feature limits"""
        user = self.user_repo.find_by_id(user_id)
        tier = SubscriptionTier(user.subscription_tier)
        features = TIER_FEATURES[tier]
        
        return {
            'tier': tier.value,
            'features': {
                'max_tickers': features.max_tickers_per_analysis,
                'max_daily_analyses': features.max_daily_analyses,
                'advanced_ai': features.advanced_ai_models,
                'api_access': features.api_access,
                'export_formats': features.export_formats
            },
            'usage': {
                'analyses_today': self.usage_repo.get_today_analysis_count(user_id)
            }
        }
```

**Tests to Write:**
- `tests/core/auth/test_authorization_service.py` - Tier checks, usage limits
- `tests/data/repositories/test_usage_repository.py` - Usage tracking

**Acceptance Criteria:**
- ✅ All tier limits enforced correctly
- ✅ Usage tracking persists across sessions
- ✅ Unlimited tiers handled properly (-1 value)

---

### **Day 5: Tier-Gating Decorators & UI Integration**

#### Morning: Feature Gating Decorators
**Files to Create:**
- `src/web/decorators/tier_required.py`
- `src/web/decorators/usage_limit.py`

**Implementation (tier_required.py):**
```python
from functools import wraps
from flask import jsonify, current_app

def tier_required(feature: str):
    """Decorator to check if user's tier allows feature"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = kwargs.get('user_id')
            if not user_id:
                return jsonify({'error': 'Authentication required'}), 401
            
            container = current_app.config['SERVICE_CONTAINER']
            authz_service = container.authorization_service
            
            if not authz_service.check_feature_access(user_id, feature):
                return jsonify({
                    'error': f'Feature "{feature}" requires higher tier',
                    'upgrade_url': '/pricing'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def usage_limit(limit_type: str):
    """Decorator to enforce daily usage limits"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = kwargs.get('user_id')
            container = current_app.config['SERVICE_CONTAINER']
            authz_service = container.authorization_service
            
            if not authz_service.check_analysis_limit(user_id):
                tier_info = authz_service.get_tier_info(user_id)
                return jsonify({
                    'error': 'Daily analysis limit reached',
                    'limit': tier_info['features']['max_daily_analyses'],
                    'upgrade_url': '/pricing'
                }), 429
            
            # Proceed with request and increment usage
            response = f(*args, **kwargs)
            authz_service.increment_usage(user_id, limit_type)
            
            return response
        
        return decorated_function
    return decorator
```

**Usage in routes:**
```python
from src.web.decorators.auth_required import auth_required
from src.web.decorators.tier_required import tier_required, usage_limit

@analysis_bp.route('/analyze', methods=['POST'])
@auth_required
@usage_limit('analysis')
@tier_required('advanced_ai_models')
def advanced_analysis(user_id: int):
    # Only users with advanced_ai_models feature can access
    pass
```

**Tests to Write:**
- `tests/web/decorators/test_tier_required.py` - Feature gating
- `tests/web/decorators/test_usage_limit.py` - Rate limiting

#### Afternoon: Frontend Integration
**Files to Create:**
- `static/js/auth.js` - Authentication UI logic
- `templates/login.html` - Login form
- `templates/register.html` - Registration form
- `templates/profile.html` - User profile with tier info

**Implementation (auth.js):**
```javascript
// Authentication utilities
const Auth = {
    async register(email, password, fullName) {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, password, full_name: fullName})
        });
        return await response.json();
    },
    
    async login(email, password) {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, password})
        });
        
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('user_id', data.user_id);
            return data;
        }
        throw new Error('Login failed');
    },
    
    async logout() {
        await fetch('/api/auth/logout', {method: 'POST'});
        localStorage.removeItem('user_id');
        window.location.href = '/login';
    },
    
    async checkSession() {
        const response = await fetch('/api/auth/validate');
        return response.ok;
    },
    
    async getTierInfo() {
        const response = await fetch('/api/auth/tier-info');
        return await response.json();
    }
};

// Show tier limits in UI
async function displayTierLimits() {
    const tierInfo = await Auth.getTierInfo();
    document.getElementById('tier-name').textContent = tierInfo.tier.toUpperCase();
    document.getElementById('analyses-remaining').textContent = 
        tierInfo.features.max_daily_analyses - tierInfo.usage.analyses_today;
}
```

**Acceptance Criteria:**
- ✅ Login/register forms have client-side validation
- ✅ Tier limits displayed in user profile
- ✅ Upgrade prompts shown when limits hit
- ✅ Session persists across page refreshes

---

## **Phase 3: Profile Management & Admin Tools (Days 6-7)**

### **Day 6: User Profile Management**

#### Morning: Profile Service & Routes
**Files to Create:**
- `src/core/auth/profile_service.py`
- `src/web/routes/profile.py`

**Implementation (profile_service.py):**
```python
from typing import Optional
from src.data.repositories.user_repository import IUserRepository
from src.core.auth.password_service import PasswordService

class ProfileService:
    """User profile management"""
    
    def __init__(
        self,
        user_repo: IUserRepository,
        password_service: PasswordService
    ):
        self.user_repo = user_repo
        self.password_service = password_service
    
    def get_profile(self, user_id: int) -> dict:
        """Get user profile data"""
        user = self.user_repo.find_by_id(user_id)
        return {
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'tier': user.subscription_tier,
            'email_verified': user.email_verified,
            'created_at': user.created_at.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None
        }
    
    def update_profile(
        self,
        user_id: int,
        full_name: Optional[str] = None
    ) -> bool:
        """Update user profile"""
        return self.user_repo.update_profile(user_id, full_name)
    
    def change_password(
        self,
        user_id: int,
        current_password: str,
        new_password: str
    ) -> bool:
        """Change user password with current password verification"""
        user = self.user_repo.find_by_id(user_id)
        
        # Verify current password
        if not self.password_service.verify_password(current_password, user.password_hash):
            raise InvalidCredentialsError("Current password is incorrect")
        
        # Validate new password
        valid, message = self.password_service.validate_password_strength(new_password)
        if not valid:
            raise WeakPasswordError(message)
        
        # Hash and update
        new_hash = self.password_service.hash_password(new_password)
        return self.user_repo.update_password(user_id, new_hash)
    
    def deactivate_account(self, user_id: int) -> bool:
        """Soft delete user account"""
        return self.user_repo.deactivate(user_id)
```

**Tests to Write:**
- `tests/core/auth/test_profile_service.py` - Profile CRUD operations
- `tests/web/routes/test_profile_routes.py` - Profile endpoints

#### Afternoon: Admin Panel (Basic)
**Files to Create:**
- `src/web/routes/admin.py` - Admin routes
- `src/web/decorators/admin_required.py` - Admin auth decorator
- `templates/admin/users.html` - User management UI

**Implementation (admin_required.py):**
```python
def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = kwargs.get('user_id')
        container = current_app.config['SERVICE_CONTAINER']
        user = container.user_repository.find_by_id(user_id)
        
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function
```

**Admin Routes (admin.py):**
```python
@admin_bp.route('/users', methods=['GET'])
@auth_required
@admin_required
def list_users(user_id: int):
    """List all users (admin only)"""
    container = get_container()
    users = container.user_repository.get_all()
    
    return jsonify({
        'users': [
            {
                'id': u.id,
                'email': u.email,
                'tier': u.subscription_tier,
                'is_active': u.is_active,
                'created_at': u.created_at.isoformat()
            }
            for u in users
        ]
    })

@admin_bp.route('/users/<int:target_user_id>/tier', methods=['PUT'])
@auth_required
@admin_required
def update_user_tier(user_id: int, target_user_id: int):
    """Update user tier (admin only)"""
    data = request.get_json()
    container = get_container()
    
    success = container.user_repository.update_tier(target_user_id, data['tier'])
    return jsonify({'success': success})
```

**Acceptance Criteria:**
- ✅ Only admins can access admin routes
- ✅ Admin can view all users
- ✅ Admin can change user tiers
- ✅ Admin actions logged in activity log

---

### **Day 7: Email Verification & Password Reset**

#### Full Day: Email Flows
**Files to Create:**
- `src/core/auth/email_service.py` - Email sending
- `src/web/routes/password_reset.py` - Reset flow routes
- `templates/emails/verify_email.html` - Verification email template
- `templates/emails/reset_password.html` - Reset email template

**Implementation (email_service.py):**
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict
from src.core.auth.token_service import TokenService

class EmailService:
    """Send transactional emails"""
    
    def __init__(self, smtp_config: Dict):
        self.smtp_host = smtp_config['host']
        self.smtp_port = smtp_config['port']
        self.smtp_user = smtp_config['user']
        self.smtp_password = smtp_config['password']
        self.from_email = smtp_config['from_email']
    
    def send_verification_email(self, to_email: str, token: str):
        """Send email verification link"""
        verify_url = f"https://yourapp.com/verify?token={token}"
        
        html = f"""
        <h2>Verify Your Email</h2>
        <p>Click the link below to verify your email address:</p>
        <a href="{verify_url}">Verify Email</a>
        <p>This link expires in 24 hours.</p>
        """
        
        self._send_email(to_email, "Verify Your Email", html)
    
    def send_password_reset_email(self, to_email: str, token: str):
        """Send password reset link"""
        reset_url = f"https://yourapp.com/reset-password?token={token}"
        
        html = f"""
        <h2>Reset Your Password</h2>
        <p>Click the link below to reset your password:</p>
        <a href="{reset_url}">Reset Password</a>
        <p>This link expires in 1 hour.</p>
        """
        
        self._send_email(to_email, "Reset Your Password", html)
    
    def _send_email(self, to_email: str, subject: str, html_body: str):
        """Internal method to send email via SMTP"""
        msg = MIMEMultipart('alternative')
        msg['From'] = self.from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)
        
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
```

**Password Reset Flow:**
1. User requests reset → Email with token sent
2. User clicks link → Token validated
3. User enters new password → Password updated

**Tests to Write:**
- `tests/core/auth/test_email_service.py` - Email sending (mock SMTP)
- `tests/web/routes/test_password_reset.py` - Reset flow end-to-end

**Acceptance Criteria:**
- ✅ Verification tokens expire after 24 hours
- ✅ Reset tokens expire after 1 hour
- ✅ Tokens are single-use only
- ✅ Email templates are mobile-responsive

---

## **Phase 4: Migration & Integration (Days 8-9)**

### **Day 8: Strangler Fig Migration**

#### Morning: Identify Legacy Auth Code
**Files to Audit:**
- Grep for: `session['user']`, `@login_required`, old auth patterns
- Check: `src/web/routes/*.py` for unprotected routes

**Migration Steps:**
1. Replace old `@login_required` with new `@auth_required`
2. Update all routes to use DI container
3. Remove legacy session handling

#### Afternoon: Protect Existing Routes
**Files to Modify:**
- `src/web/routes/analysis.py` - Add `@auth_required` and tier gating
- `src/web/routes/chat.py` - Add `@auth_required` and usage limits
- `src/web/routes/main.py` - Add tier checks where needed

**Example Migration:**
```python
# BEFORE
@analysis_bp.route('/analyze', methods=['POST'])
def analyze():
    # No auth check
    pass

# AFTER
@analysis_bp.route('/analyze', methods=['POST'])
@auth_required
@usage_limit('analysis')
@tier_required('advanced_ai_models')
def analyze(user_id: int):
    # Now protected with auth, usage limits, and tier gating
    pass
```

**Tests to Update:**
- All existing integration tests need session tokens
- Update fixtures to create authenticated test users

**Acceptance Criteria:**
- ✅ No routes accessible without authentication
- ✅ All tier limits enforced on existing features
- ✅ All tests pass with new auth system

---

### **Day 9: Frontend Integration & E2E Testing**

#### Morning: Update Frontend to Use Auth
**Files to Modify:**
- `static/js/app.js` - Add auth checks before API calls
- `templates/base.html` - Add login/logout links, user menu
- All templates - Show/hide features based on tier

**Example JavaScript:**
```javascript
// Before making API call
async function analyzeStock(ticker) {
    // Check authentication
    if (!await Auth.checkSession()) {
        window.location.href = '/login';
        return;
    }
    
    // Make authenticated request
    const response = await fetch('/api/analysis/analyze', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ticker})
    });
    
    if (response.status === 403) {
        // Tier limit hit
        const data = await response.json();
        showUpgradePrompt(data.upgrade_url);
    }
    
    // Handle response...
}
```

#### Afternoon: End-to-End Integration Tests
**Files to Create:**
- `tests/e2e/test_user_journey_free_tier.py`
- `tests/e2e/test_user_journey_premium_tier.py`
- `tests/e2e/test_upgrade_flow.py`

**Test Scenarios:**
```python
def test_free_tier_user_journey():
    """Complete flow: register → login → analyze (3x) → hit limit → upgrade prompt"""
    # 1. Register new free tier user
    # 2. Login
    # 3. Analyze 3 stocks (max for free tier)
    # 4. Try 4th analysis → expect 429 with upgrade prompt
    # 5. Logout
    pass

def test_tier_upgrade_flow():
    """Admin upgrades user tier → user gets new limits"""
    # 1. Free tier user hits limit
    # 2. Admin changes tier to premium
    # 3. User refreshes → sees new limits
    # 4. User can now analyze more stocks
    pass
```

**Acceptance Criteria:**
- ✅ All user journeys pass end-to-end
- ✅ Tier limits enforced in real browser tests
- ✅ Upgrade prompts appear at right times

---

## **Phase 5: Polish & Documentation (Days 10-12)**

### **Day 10: Security Hardening**

**Tasks:**
- [ ] Enable Flask-WTF CSRF protection on all forms
- [ ] Add rate limiting to login endpoint (Flask-Limiter)
- [ ] Secure cookies: httpOnly, secure, SameSite=Lax
- [ ] Add Content-Security-Policy headers
- [ ] Run bandit security scan: `bandit -r src/`
- [ ] Run safety check: `safety check`

**Files to Create:**
- `src/web/middleware/security_headers.py` - CSP headers
- `src/config/security.py` - Security configuration

---

### **Day 11: Performance & Monitoring**

**Tasks:**
- [ ] Add database indexes (see Day 1 schema)
- [ ] Enable SQLAlchemy query logging
- [ ] Add authentication metrics (login attempts, session duration)
- [ ] Test with 100 concurrent users (locust load test)

**Files to Create:**
- `tests/performance/test_auth_load.py` - Load testing script

---

### **Day 12: Documentation & Handoff**

**Files to Create:**
- `docs/AUTH_SETUP.md` - Setup instructions
- `docs/AUTH_API.md` - API documentation (OpenAPI spec)
- `docs/TIER_CONFIGURATION.md` - How to add/modify tiers
- `.specify/features/epic-1-complete-authentication/TASKS.md` - Task checklist

**Documentation Includes:**
- Database schema diagram
- Authentication flow diagrams (registration, login, session validation)
- API endpoint documentation with examples
- Tier configuration guide

---

## 📊 Success Metrics

### Functional Requirements
- ✅ All 5 user stories implemented and tested
- ✅ 100% test coverage for auth module
- ✅ All 17 acceptance criteria met
- ✅ No security vulnerabilities (bandit + safety)

### Non-Functional Requirements
- ✅ Login response time < 200ms
- ✅ Session validation < 50ms
- ✅ Supports 100 concurrent users
- ✅ Zero data breaches (encrypted passwords, secure sessions)

### Business Metrics
- ✅ Users can self-register (reduces support burden)
- ✅ Tier limits enforced (enables monetization)
- ✅ Upgrade prompts shown (conversion funnel ready)
- ✅ Admin can manage users (operational efficiency)

---

## 🔒 Definition of Done

### Code Quality
- [ ] All tests passing (unit + integration + E2E)
- [ ] Test coverage ≥ 95% for auth module
- [ ] No critical/high security issues (bandit, safety)
- [ ] All code reviewed and merged to main

### Documentation
- [ ] API documentation published
- [ ] Setup guide verified by fresh install
- [ ] Tier configuration guide validated
- [ ] Architecture diagrams created

### Deployment
- [ ] Database migrations tested (up + down)
- [ ] Environment variables documented
- [ ] Monitoring/logging configured
- [ ] Rollback plan documented

---

## 🚧 Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Migration breaks existing features | HIGH | Strangler Fig pattern, feature flags, rollback plan |
| Performance degradation with auth checks | MEDIUM | Database indexes, session caching, load testing |
| Email deliverability issues | MEDIUM | Use reputable SMTP (SendGrid/Mailgun), test before launch |
| Session hijacking | HIGH | Secure cookies, short expiry, IP validation option |
| Password reset abuse | MEDIUM | Rate limiting, CAPTCHA, email verification |

---

## 📋 Next Steps After Epic 1

Once Epic 1 is complete:
1. **Epic 2: Security Hardening** - OWASP compliance, penetration testing
2. **Epic 4: Payment Integration** - Stripe subscriptions, webhooks
3. **Epic 3: Code Quality Refactoring** - Apply Repository/DI patterns to rest of codebase

---

**Estimated Completion Date**: Day 12  
**Critical Path**: Database setup → Auth service → Flask routes → Migration → Testing  
**Blockers**: None (all dependencies internal)  
**Team Size**: 1-2 developers  

---

**PLAN STATUS**: ✅ READY FOR IMPLEMENTATION  
**Last Updated**: 2026-01-08