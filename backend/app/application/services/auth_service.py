import uuid
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from app.core.config import settings
from app.domain.auth import User, UserPreferences, UserSession, AuditLog, LoginHistory
from app.domain.repositories import (
    IUserRepository, 
    ISessionRepository, 
    IAuditLogRepository, 
    ILoginHistoryRepository
)
from app.domain.events import (
    UserRegisteredEvent,
    UserLoggedInEvent,
    UserLoggedOutEvent,
    PasswordChangedEvent,
    ProfileUpdatedEvent,
    SessionRevokedEvent,
    AuditLogCreatedEvent
)
from app.infrastructure.events.dispatcher import event_bus

logger = logging.getLogger(__name__)
ph = PasswordHasher()

class AuthService:
    def __init__(
        self,
        user_repo: IUserRepository,
        session_repo: ISessionRepository,
        audit_repo: IAuditLogRepository,
        history_repo: ILoginHistoryRepository
    ):
        self.user_repo = user_repo
        self.session_repo = session_repo
        self.audit_repo = audit_repo
        self.history_repo = history_repo

    async def register_user(self, email: str, password: str, ip: Optional[str] = None) -> User:
        # Check if user already exists
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise ValueError(f"User account with email '{email}' already exists.")

        # Hash password and save user
        hashed = ph.hash(password)
        user = await self.user_repo.create_user(email, hashed)

        # Trigger registration event
        reg_event = UserRegisteredEvent(
            event_id=str(uuid.uuid4()),
            user_id=user.id,
            email=user.email
        )
        await event_bus.publish(reg_event)

        # Write audit log
        audit = await self.audit_repo.create_audit_log(
            user_id=user.id,
            action="USER_REGISTRATION",
            component="auth",
            ip_address=ip,
            details={"email": email}
        )
        await event_bus.publish(
            AuditLogCreatedEvent(
                event_id=str(uuid.uuid4()), 
                log_id=audit.id, 
                user_id=user.id, 
                action="USER_REGISTRATION", 
                component="auth"
            )
        )

        return user

    async def authenticate_user(
        self, 
        email: str, 
        password: str, 
        ip_address: Optional[str] = None, 
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        user = await self.user_repo.get_by_email(email)
        if not user:
            # Prevent user enumeration timing attacks by running a dummy verify pass
            ph.hash("dummy_password")
            raise ValueError("Invalid email or password credentials.")

        # Fetch password hash
        hashed_password = await self.user_repo.get_password_hash(user.id)
        if not hashed_password:
            raise ValueError("Invalid email or password credentials.")

        try:
            ph.verify(hashed_password, password)
        except VerifyMismatchError:
            # Log failure attempt
            await self.history_repo.record_login_attempt(
                user_id=user.id,
                status="failed",
                failure_reason="Invalid credentials mismatch",
                ip_address=ip_address,
                user_agent=user_agent
            )
            await self.audit_repo.create_audit_log(
                user_id=user.id,
                action="LOGIN_FAILURE",
                component="auth",
                ip_address=ip_address,
                details={"reason": "Verify mismatch"}
            )
            raise ValueError("Invalid email or password credentials.")

        # Generate tokens
        session_token = str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        
        session = await self.session_repo.create_session(
            user_id=user.id,
            session_token=session_token,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )

        # Generate JWT Access & Refresh tokens
        access_token = self._create_access_token(user)
        refresh_token = self._create_refresh_token(user.id, session_token)

        # Log history
        await self.history_repo.record_login_attempt(
            user_id=user.id,
            status="success",
            failure_reason=None,
            ip_address=ip_address,
            user_agent=user_agent
        )

        # Trigger login event
        await event_bus.publish(
            UserLoggedInEvent(
                event_id=str(uuid.uuid4()),
                user_id=user.id,
                email=user.email,
                session_id=session.id,
                ip_address=ip_address
            )
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "session": session,
            "user": user
        }

    async def refresh_session_tokens(
        self, 
        refresh_token: str, 
        ip_address: Optional[str] = None, 
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("sub")
            jti = payload.get("jti")
        except jwt.PyJWTError as e:
            logger.warning(f"Failed JWT Refresh validation: {e}")
            raise ValueError("Invalid or expired refresh token.")

        # Check session status
        session = await self.session_repo.get_session(jti)
        if not session or not session.is_active or session.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise ValueError("Active session not found or revoked.")

        # Fetch user
        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise ValueError("User account is inactive or disabled.")

        # Rotate refresh token: revoke previous, create new
        await self.session_repo.revoke_session(session.id)

        new_session_token = str(uuid.uuid4())
        new_expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        new_session = await self.session_repo.create_session(
            user_id=user.id,
            session_token=new_session_token,
            expires_at=new_expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )

        new_access_token = self._create_access_token(user)
        new_refresh_token = self._create_refresh_token(user.id, new_session_token)

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "session": new_session
        }

    async def revoke_user_session(self, user_id: str, session_id: str, requester_ip: Optional[str] = None) -> bool:
        # Revoke target session
        await self.session_repo.revoke_session(session_id)

        # Trigger event
        await event_bus.publish(
            SessionRevokedEvent(
                event_id=str(uuid.uuid4()),
                user_id=user_id,
                session_id=session_id,
                revoked_by=user_id
            )
        )

        # Write audit
        await self.audit_repo.create_audit_log(
            user_id=user_id,
            action="SESSION_REVOCATION",
            component="auth",
            ip_address=requester_ip,
            details={"revoked_session_id": session_id}
        )
        return True

    async def change_password(self, user_id: str, old_password: str, new_password: str, ip_address: Optional[str] = None) -> bool:
        # Verify old password
        hashed_password = await self.user_repo.get_password_hash(user_id)
        if not hashed_password:
            raise ValueError("User account password hash not found.")

        try:
            ph.verify(hashed_password, old_password)
        except VerifyMismatchError:
            raise ValueError("Incorrect password credential confirmation.")

        # Hash new password
        new_hashed = ph.hash(new_password)
        await self.user_repo.update_password(user_id, new_hashed)

        # Revoke other sessions for security
        await self.session_repo.revoke_all_sessions(user_id)

        # Trigger event
        await event_bus.publish(
            PasswordChangedEvent(event_id=str(uuid.uuid4()), user_id=user_id)
        )

        # Audit
        await self.audit_repo.create_audit_log(
            user_id=user_id,
            action="PASSWORD_CHANGE",
            component="auth",
            ip_address=ip_address,
            details={}
        )
        return True

    def _create_access_token(self, user: User) -> str:
        roles_list = [r.name for r in user.roles]
        permissions_list = []
        for r in user.roles:
            permissions_list.extend([p.name for p in r.permissions])
        
        # Remove duplicates
        permissions_list = list(set(permissions_list))

        payload = {
            "sub": user.id,
            "email": user.email,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),  # 30 minutes life
            "roles": roles_list,
            "permissions": permissions_list
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    def _create_refresh_token(self, user_id: str, session_token: str) -> str:
        payload = {
            "sub": user_id,
            "jti": session_token,
            "exp": datetime.now(timezone.utc) + timedelta(days=7)  # 7 days life
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
