import sys
import os
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta, timezone
import jwt

# Add backend root directory to path for app imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.domain.auth import User, Role, UserPreferences, UserSession, AuditLog
from app.application.services.auth_service import AuthService

@pytest.fixture
def mock_user_repo():
    repo = MagicMock()
    repo.create_user = AsyncMock()
    repo.get_by_email = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_password_hash = AsyncMock()
    repo.update_password = AsyncMock()
    repo.update_profile = AsyncMock()
    repo.get_preferences = AsyncMock()
    repo.update_preferences = AsyncMock()
    return repo

@pytest.fixture
def mock_session_repo():
    repo = MagicMock()
    repo.create_session = AsyncMock()
    repo.get_session = AsyncMock()
    repo.list_user_sessions = AsyncMock()
    repo.revoke_session = AsyncMock()
    repo.revoke_all_sessions = AsyncMock()
    return repo

@pytest.fixture
def mock_audit_repo():
    repo = MagicMock()
    repo.create_audit_log = AsyncMock()
    repo.list_audit_logs = AsyncMock()
    return repo

@pytest.fixture
def mock_history_repo():
    repo = MagicMock()
    repo.record_login_attempt = AsyncMock()
    repo.list_login_history = AsyncMock()
    return repo

@pytest.fixture
def auth_service(mock_user_repo, mock_session_repo, mock_audit_repo, mock_history_repo):
    return AuthService(
        user_repo=mock_user_repo,
        session_repo=mock_session_repo,
        audit_repo=mock_audit_repo,
        history_repo=mock_history_repo
    )

@pytest.mark.asyncio
async def test_register_user_success(auth_service, mock_user_repo, mock_audit_repo):
    email = "test@example.com"
    password = "securepassword123"
    
    mock_user_repo.get_by_email.return_value = None
    mock_user_repo.create_user.return_value = User(
        id="user_123",
        email=email,
        is_active=True,
        is_verified=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    mock_audit_repo.create_audit_log.return_value = AuditLog(
        id="audit_123",
        user_id="user_123",
        action="USER_REGISTRATION",
        component="auth",
        created_at=datetime.now(timezone.utc)
    )
    
    user = await auth_service.register_user(email, password)
    
    assert user.id == "user_123"
    assert user.email == email
    mock_user_repo.create_user.assert_called_once()
    mock_audit_repo.create_audit_log.assert_called_once()

@pytest.mark.asyncio
async def test_register_user_already_exists(auth_service, mock_user_repo):
    email = "test@example.com"
    password = "securepassword123"
    
    mock_user_repo.get_by_email.return_value = User(
        id="user_123",
        email=email,
        is_active=True,
        is_verified=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    with pytest.raises(ValueError, match="already exists"):
        await auth_service.register_user(email, password)

@pytest.mark.asyncio
async def test_authenticate_user_success(auth_service, mock_user_repo, mock_session_repo):
    email = "test@example.com"
    password = "securepassword123"
    from argon2 import PasswordHasher
    ph = PasswordHasher()
    hashed = ph.hash(password)
    
    user = User(
        id="user_123",
        email=email,
        is_active=True,
        is_verified=True,
        roles=[Role(id="r1", name="user", permissions=[])],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    mock_user_repo.get_by_email.return_value = user
    mock_user_repo.get_password_hash.return_value = hashed
    
    mock_session_repo.create_session.return_value = UserSession(
        id="sess_abc",
        user_id="user_123",
        session_token="token_xyz",
        is_active=True,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        created_at=datetime.now(timezone.utc)
    )
    
    result = await auth_service.authenticate_user(email, password)
    
    assert "access_token" in result
    assert "refresh_token" in result
    assert result["user"].id == "user_123"

@pytest.mark.asyncio
async def test_authenticate_user_invalid_password(auth_service, mock_user_repo, mock_history_repo):
    email = "test@example.com"
    password = "securepassword123"
    from argon2 import PasswordHasher
    ph = PasswordHasher()
    hashed = ph.hash("different_password")
    
    user = User(
        id="user_123",
        email=email,
        is_active=True,
        is_verified=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    mock_user_repo.get_by_email.return_value = user
    mock_user_repo.get_password_hash.return_value = hashed
    
    with pytest.raises(ValueError, match="Invalid email or password"):
        await auth_service.authenticate_user(email, password)
    
    mock_history_repo.record_login_attempt.assert_called_once()
