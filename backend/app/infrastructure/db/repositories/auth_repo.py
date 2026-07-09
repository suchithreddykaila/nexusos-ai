import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.auth import User, UserPreferences, UserSession, AuditLog, LoginHistory, Permission, Role
from app.domain.repositories import (
    IUserRepository, 
    ISessionRepository, 
    IAuditLogRepository, 
    ILoginHistoryRepository
)
from app.infrastructure.db.models import (
    UserDB, 
    UserPreferencesDB, 
    UserSessionDB, 
    AuditLogDB, 
    LoginHistoryDB,
    RoleDB
)

def map_user_db_to_domain(db_user: UserDB) -> User:
    roles = []
    for r in db_user.roles:
        perms = [Permission(id=p.id, name=p.name, description=p.description) for p in r.permissions]
        roles.append(Role(id=r.id, name=r.name, description=r.description, permissions=perms))
    
    prefs = None
    if db_user.preferences:
        prefs = UserPreferences(
            user_id=db_user.preferences.user_id,
            theme=db_user.preferences.theme,
            default_provider=db_user.preferences.default_provider,
            default_model=db_user.preferences.default_model,
            custom_settings=db_user.preferences.custom_settings or {},
            updated_at=db_user.preferences.updated_at
        )
        
    return User(
        id=db_user.id,
        email=db_user.email,
        is_active=db_user.is_active,
        is_verified=db_user.is_verified,
        avatar_url=db_user.avatar_url,
        roles=roles,
        preferences=prefs,
        created_at=db_user.created_at,
        updated_at=db_user.updated_at
    )

class SQLUserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, email: str, hashed_password: str) -> User:
        # Create User entry
        db_user = UserDB(
            id=str(uuid.uuid4()),
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            is_verified=False
        )
        self.session.add(db_user)
        await self.session.flush()

        # Seed default User Preferences entry
        db_prefs = UserPreferencesDB(
            user_id=db_user.id,
            theme="light",
            default_provider="ollama",
            default_model="llama3.2:3b",
            custom_settings={}
        )
        self.session.add(db_prefs)
        await self.session.flush()

        # Retrieve default User Role
        result = await self.session.execute(select(RoleDB).where(RoleDB.name == "user"))
        default_role = result.scalar_one_or_none()
        if default_role:
            db_user.roles.append(default_role)
            await self.session.flush()

        return map_user_db_to_domain(db_user)

    async def get_by_id(self, user_id: str) -> Optional[User]:
        result = await self.session.execute(select(UserDB).where(UserDB.id == user_id))
        db_user = result.scalar_one_or_none()
        if db_user:
            return map_user_db_to_domain(db_user)
        return None

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(select(UserDB).where(UserDB.email == email))
        db_user = result.scalar_one_or_none()
        if db_user:
            return map_user_db_to_domain(db_user)
        return None

    async def get_password_hash(self, user_id: str) -> Optional[str]:
        result = await self.session.execute(select(UserDB.hashed_password).where(UserDB.id == user_id))
        return result.scalar_one_or_none()

    async def update_password(self, user_id: str, new_hashed_password: str) -> bool:
        await self.session.execute(
            update(UserDB)
            .where(UserDB.id == user_id)
            .values(hashed_password=new_hashed_password, updated_at=datetime.now(timezone.utc))
        )
        return True

    async def update_profile(
        self, 
        user_id: str, 
        email: Optional[str] = None, 
        avatar_url: Optional[str] = None
    ) -> User:
        values = {"updated_at": datetime.now(timezone.utc)}
        if email:
            values["email"] = email
        if avatar_url:
            values["avatar_url"] = avatar_url

        await self.session.execute(
            update(UserDB)
            .where(UserDB.id == user_id)
            .values(**values)
        )
        # Flush session to fetch details
        result = await self.session.execute(select(UserDB).where(UserDB.id == user_id))
        db_user = result.scalar_one()
        return map_user_db_to_domain(db_user)

    async def get_preferences(self, user_id: str) -> Optional[UserPreferences]:
        result = await self.session.execute(
            select(UserPreferencesDB).where(UserPreferencesDB.user_id == user_id)
        )
        db_prefs = result.scalar_one_or_none()
        if db_prefs:
            return UserPreferences(
                user_id=db_prefs.user_id,
                theme=db_prefs.theme,
                default_provider=db_prefs.default_provider,
                default_model=db_prefs.default_model,
                custom_settings=db_prefs.custom_settings or {},
                updated_at=db_prefs.updated_at
            )
        return None

    async def update_preferences(self, preferences: UserPreferences) -> UserPreferences:
        await self.session.execute(
            update(UserPreferencesDB)
            .where(UserPreferencesDB.user_id == preferences.user_id)
            .values(
                theme=preferences.theme,
                default_provider=preferences.default_provider,
                default_model=preferences.default_model,
                custom_settings=preferences.custom_settings,
                updated_at=datetime.now(timezone.utc)
            )
        )
        return preferences


class SQLSessionRepository(ISessionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_session(
        self, 
        user_id: str, 
        session_token: str, 
        expires_at: datetime, 
        ip_address: Optional[str] = None, 
        user_agent: Optional[str] = None
    ) -> UserSession:
        db_session = UserSessionDB(
            id=str(uuid.uuid4()),
            user_id=user_id,
            session_token=session_token,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
            is_active=True
        )
        self.session.add(db_session)
        await self.session.flush()
        return UserSession(
            id=db_session.id,
            user_id=db_session.user_id,
            session_token=db_session.session_token,
            ip_address=db_session.ip_address,
            user_agent=db_session.user_agent,
            is_active=db_session.is_active,
            expires_at=db_session.expires_at,
            created_at=db_session.created_at
        )

    async def get_session(self, session_token: str) -> Optional[UserSession]:
        result = await self.session.execute(
            select(UserSessionDB).where(UserSessionDB.session_token == session_token)
        )
        db_session = result.scalar_one_or_none()
        if db_session:
            return UserSession(
                id=db_session.id,
                user_id=db_session.user_id,
                session_token=db_session.session_token,
                ip_address=db_session.ip_address,
                user_agent=db_session.user_agent,
                is_active=db_session.is_active,
                expires_at=db_session.expires_at,
                created_at=db_session.created_at
            )
        return None

    async def list_user_sessions(self, user_id: str) -> List[UserSession]:
        result = await self.session.execute(
            select(UserSessionDB)
            .where(UserSessionDB.user_id == user_id, UserSessionDB.is_active == True)
            .order_by(UserSessionDB.created_at.desc())
        )
        db_sessions = result.scalars().all()
        return [
            UserSession(
                id=s.id,
                user_id=s.user_id,
                session_token=s.session_token,
                ip_address=s.ip_address,
                user_agent=s.user_agent,
                is_active=s.is_active,
                expires_at=s.expires_at,
                created_at=s.created_at
            ) for s in db_sessions
        ]

    async def revoke_session(self, session_id: str) -> bool:
        await self.session.execute(
            update(UserSessionDB)
            .where(UserSessionDB.id == session_id)
            .values(is_active=False)
        )
        return True

    async def revoke_all_sessions(self, user_id: str) -> bool:
        await self.session.execute(
            update(UserSessionDB)
            .where(UserSessionDB.user_id == user_id)
            .values(is_active=False)
        )
        return True


class SQLAuditLogRepository(IAuditLogRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_audit_log(
        self, 
        user_id: Optional[str], 
        action: str, 
        component: str, 
        ip_address: Optional[str], 
        details: dict
    ) -> AuditLog:
        db_log = AuditLogDB(
            id=str(uuid.uuid4()),
            user_id=user_id,
            action=action,
            component=component,
            ip_address=ip_address,
            details=details
        )
        self.session.add(db_log)
        await self.session.flush()
        return AuditLog(
            id=db_log.id,
            user_id=db_log.user_id,
            action=db_log.action,
            component=db_log.component,
            ip_address=db_log.ip_address,
            details=db_log.details,
            created_at=db_log.created_at
        )

    async def list_audit_logs(self, user_id: Optional[str] = None) -> List[AuditLog]:
        query = select(AuditLogDB)
        if user_id:
            query = query.where(AuditLogDB.user_id == user_id)
        query = query.order_by(AuditLogDB.created_at.desc())
        
        result = await self.session.execute(query)
        db_logs = result.scalars().all()
        return [
            AuditLog(
                id=log.id,
                user_id=log.user_id,
                action=log.action,
                component=log.component,
                ip_address=log.ip_address,
                details=log.details,
                created_at=log.created_at
            ) for log in db_logs
        ]


class SQLLoginHistoryRepository(ILoginHistoryRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def record_login_attempt(
        self, 
        user_id: str, 
        status: str, 
        failure_reason: Optional[str], 
        ip_address: Optional[str], 
        user_agent: Optional[str]
    ) -> LoginHistory:
        db_history = LoginHistoryDB(
            id=str(uuid.uuid4()),
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            failure_reason=failure_reason
        )
        self.session.add(db_history)
        await self.session.flush()
        return LoginHistory(
            id=db_history.id,
            user_id=db_history.user_id,
            ip_address=db_history.ip_address,
            user_agent=db_history.user_agent,
            status=db_history.status,
            failure_reason=db_history.failure_reason,
            created_at=db_history.created_at
        )

    async def list_login_history(self, user_id: str) -> List[LoginHistory]:
        result = await self.session.execute(
            select(LoginHistoryDB)
            .where(LoginHistoryDB.user_id == user_id)
            .order_by(LoginHistoryDB.created_at.desc())
        )
        db_history = result.scalars().all()
        return [
            LoginHistory(
                id=h.id,
                user_id=h.user_id,
                ip_address=h.ip_address,
                user_agent=h.user_agent,
                status=h.status,
                failure_reason=h.failure_reason,
                created_at=h.created_at
            ) for h in db_history
        ]
