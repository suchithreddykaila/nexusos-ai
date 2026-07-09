import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Table, JSON, Integer, Float, BigInteger, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Many-to-Many Association Tables
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", String(36), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", String(36), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", String(36), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)

class UserDB(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    avatar_url = Column(String(1024), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    roles = relationship("RoleDB", secondary=user_roles, back_populates="users", lazy="selectin")
    preferences = relationship("UserPreferencesDB", back_populates="user", uselist=False, lazy="selectin", cascade="all, delete-orphan")

class RoleDB(Base):
    __tablename__ = "roles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)

    users = relationship("UserDB", secondary=user_roles, back_populates="roles")
    permissions = relationship("PermissionDB", secondary=role_permissions, back_populates="roles", lazy="selectin")

class PermissionDB(Base):
    __tablename__ = "permissions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)

    roles = relationship("RoleDB", secondary=role_permissions, back_populates="permissions")

class UserPreferencesDB(Base):
    __tablename__ = "user_preferences"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    theme = Column(String(50), default="light", nullable=False)
    default_provider = Column(String(100), default="ollama", nullable=False)
    default_model = Column(String(100), default="llama3.2:3b", nullable=False)
    custom_settings = Column(JSON, default=dict, nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("UserDB", back_populates="preferences")

class UserSessionDB(Base):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(512), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class LoginHistoryDB(Base):
    __tablename__ = "login_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(512), nullable=True)
    status = Column(String(50), nullable=False)  # success, failed
    failure_reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class AuditLogDB(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(255), nullable=False)
    component = Column(String(255), nullable=False)
    ip_address = Column(String(45), nullable=True)
    details = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


# ==========================================
# WORKSPACE & MULTI-TENANCY PLATFORM DB SCHEMAS
# ==========================================

class OrganizationDB(Base):
    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False, index=True)
    billing_status = Column(String(50), default="active", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    workspaces = relationship("WorkspaceDB", back_populates="organization", cascade="all, delete-orphan")

class WorkspaceDB(Base):
    __tablename__ = "workspaces"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(512), nullable=True)
    logo_url = Column(String(1024), nullable=True)
    color_theme = Column(String(50), default="slate", nullable=False)
    icon = Column(String(50), default="briefcase", nullable=False)
    timezone = Column(String(50), default="UTC", nullable=False)
    language = Column(String(10), default="en", nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    organization = relationship("OrganizationDB", back_populates="workspaces")
    members = relationship("WorkspaceMemberDB", back_populates="workspace", cascade="all, delete-orphan", lazy="selectin")
    invitations = relationship("WorkspaceInvitationDB", back_populates="workspace", cascade="all, delete-orphan")
    ai_settings = relationship("WorkspaceAISettingsDB", back_populates="workspace", uselist=False, cascade="all, delete-orphan", lazy="selectin")
    storage = relationship("WorkspaceStorageDB", back_populates="workspace", uselist=False, cascade="all, delete-orphan", lazy="selectin")
    activities = relationship("WorkspaceActivityDB", back_populates="workspace", cascade="all, delete-orphan")
    preferences = relationship("WorkspacePreferencesDB", back_populates="workspace", uselist=False, cascade="all, delete-orphan", lazy="selectin")

class WorkspaceMemberDB(Base):
    __tablename__ = "workspace_members"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role_name = Column(String(50), default="viewer", nullable=False)  # owner, administrator, manager, editor, contributor, viewer, guest
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    workspace = relationship("WorkspaceDB", back_populates="members")
    user = relationship("UserDB", lazy="selectin")

class WorkspaceInvitationDB(Base):
    __tablename__ = "workspace_invitations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    role_name = Column(String(50), default="viewer", nullable=False)
    status = Column(String(50), default="pending", nullable=False)  # pending, accepted, declined, expired, revoked
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    workspace = relationship("WorkspaceDB", back_populates="invitations")

class WorkspaceAISettingsDB(Base):
    __tablename__ = "workspace_ai_settings"

    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), primary_key=True)
    default_provider = Column(String(100), default="ollama", nullable=False)
    default_model = Column(String(100), default="llama3.2:3b", nullable=False)
    temperature = Column(Float, default=0.7, nullable=False)
    max_tokens = Column(Integer, default=2048, nullable=False)
    streaming = Column(Boolean, default=True, nullable=False)
    offline_mode = Column(Boolean, default=True, nullable=False)
    privacy_mode = Column(Boolean, default=True, nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    workspace = relationship("WorkspaceDB", back_populates="ai_settings")

class WorkspaceStorageDB(Base):
    __tablename__ = "workspace_storage"

    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), primary_key=True)
    bytes_used = Column(BigInteger, default=0, nullable=False)
    bytes_quota = Column(BigInteger, default=10 * 1024 * 1024 * 1024, nullable=False)  # 10 GB
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    workspace = relationship("WorkspaceDB", back_populates="storage")

class WorkspaceActivityDB(Base):
    __tablename__ = "workspace_activities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    action = Column(String(255), nullable=False)
    details = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    workspace = relationship("WorkspaceDB", back_populates="activities")
    user = relationship("UserDB")

class WorkspacePreferencesDB(Base):
    __tablename__ = "workspace_preferences"

    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), primary_key=True)
    enable_notifications = Column(Boolean, default=True, nullable=False)
    custom_settings = Column(JSON, default=dict, nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    workspace = relationship("WorkspaceDB", back_populates="preferences")


# ==========================================
# ENTERPRISE KNOWLEDGE ORGANIZATION SYSTEM
# ==========================================

# Asset - Tag Many-to-Many Bridge Table
asset_tags = Table(
    "asset_tags",
    Base.metadata,
    Column("asset_id", String(36), ForeignKey("knowledge_assets.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", String(36), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

class ProjectDB(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(512), nullable=True)
    color = Column(String(50), default="slate", nullable=False)
    icon = Column(String(50), default="folder", nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    collections = relationship("CollectionDB", back_populates="project", cascade="all, delete-orphan")

class CollectionDB(Base):
    __tablename__ = "collections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(512), nullable=True)
    color = Column(String(50), default="slate", nullable=False)
    icon = Column(String(50), default="layers", nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    project = relationship("ProjectDB", back_populates="collections")
    folders = relationship("FolderDB", back_populates="collection", cascade="all, delete-orphan")

class FolderDB(Base):
    __tablename__ = "folders"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    collection_id = Column(String(36), ForeignKey("collections.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_id = Column(String(36), ForeignKey("folders.id", ondelete="CASCADE"), nullable=True, index=True)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    color = Column(String(50), default="slate", nullable=False)
    icon = Column(String(50), default="folder", nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    collection = relationship("CollectionDB", back_populates="folders")
    assets = relationship("KnowledgeAssetDB", back_populates="folder", cascade="all, delete-orphan")

class KnowledgeAssetDB(Base):
    __tablename__ = "knowledge_assets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    folder_id = Column(String(36), ForeignKey("folders.id", ondelete="CASCADE"), nullable=True, index=True)
    collection_id = Column(String(36), ForeignKey("collections.id", ondelete="CASCADE"), nullable=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    asset_type = Column(String(50), nullable=False, index=True)  # document, link, code, dataset, image, video, audio
    
    # Ingestion & Processing lifecycle states
    status = Column(String(50), default="pending", nullable=False, index=True)
    processing_stage = Column(String(100), default="pending", nullable=False)
    checksum = Column(String(255), nullable=True, index=True)
    
    # Audit references
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    deleted_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    details = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    folder = relationship("FolderDB", back_populates="assets")
    tags = relationship("TagDB", secondary=asset_tags, back_populates="assets", lazy="selectin")
    versions = relationship("AssetVersionDB", back_populates="asset", cascade="all, delete-orphan")

class TagDB(Base):
    __tablename__ = "tags"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    color = Column(String(50), default="slate", nullable=False)

    assets = relationship("KnowledgeAssetDB", secondary=asset_tags, back_populates="tags")

class FavoriteDB(Base):
    __tablename__ = "favorites"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    target_id = Column(String(36), nullable=False, index=True)
    target_type = Column(String(50), nullable=False)  # project, collection, folder, asset
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class BookmarkDB(Base):
    __tablename__ = "bookmarks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_id = Column(String(36), ForeignKey("knowledge_assets.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class AssetVersionDB(Base):
    __tablename__ = "asset_versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    asset_id = Column(String(36), ForeignKey("knowledge_assets.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, default=1, nullable=False)
    storage_path = Column(String(1024), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    asset = relationship("KnowledgeAssetDB", back_populates="versions")

class RecycleBinDB(Base):
    __tablename__ = "recycle_bin"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    item_id = Column(String(36), nullable=False, index=True)
    item_type = Column(String(50), nullable=False)  # project, collection, folder, asset
    original_parent_id = Column(String(36), nullable=True)
    deleted_by = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    deleted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class TimelineEventDB(Base):
    __tablename__ = "timeline_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    target_id = Column(String(36), nullable=False, index=True)
    target_type = Column(String(50), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class ResearchSessionDB(Base):
    __tablename__ = "research_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(512), nullable=True)
    asset_ids = Column(JSON, default=list, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

class ResearchNoteDB(Base):
    __tablename__ = "research_notes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(100), default="Untitled Note", nullable=False)
    content = Column(Text, nullable=False, default="")
    linked_asset_ids = Column(JSON, default=list, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

class LegalMatterDB(Base):
    __tablename__ = "legal_matters"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    client_name = Column(String(100), nullable=True)
    description = Column(String(512), nullable=True)
    status = Column(String(50), default="Active", nullable=False)
    is_pinned = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

class ContractAnalysisDB(Base):
    __tablename__ = "contract_analyses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    matter_id = Column(String(36), ForeignKey("legal_matters.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_id = Column(String(36), ForeignKey("knowledge_assets.id", ondelete="CASCADE"), nullable=False, index=True)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    executive_summary = Column(Text, nullable=False, default="")
    clauses = Column(JSON, default=list, nullable=False)
    risk_profile = Column(JSON, nullable=True)
    timeline = Column(JSON, default=list, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

class ComplianceReportDB(Base):
    __tablename__ = "compliance_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    matter_id = Column(String(36), ForeignKey("legal_matters.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_ids = Column(JSON, default=list, nullable=False)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    framework = Column(String(100), nullable=False)
    score = Column(Float, nullable=False, default=0.0)
    violations = Column(JSON, default=list, nullable=False)
    missing_requirements = Column(JSON, default=list, nullable=False)
    recommendations = Column(JSON, default=list, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
