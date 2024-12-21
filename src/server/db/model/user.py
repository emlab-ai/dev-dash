from sqlalchemy import BigInteger, Column, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship

from . import Base

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tenant_id = Column(
        BigInteger, ForeignKey("tenants.id"), nullable=True
    )  # todo: make non nullable
    tenant = relationship("Tenant", uselist=False)
    name = Column(String)
    is_manager = Column(Boolean)
    team_id = Column(BigInteger, ForeignKey("teams.id"), nullable=True)
    email = Column(String, nullable=False, unique=True)
    github_user_id = Column(BigInteger, ForeignKey("github_users.id"), nullable=True)
    tags = Column(String, nullable=True)
    level = Column(String, nullable=True)
    team = relationship("Team")
    github_user = relationship("GithubUser", uselist=False)
    manager_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    manager = relationship("User", lazy=True, remote_side=[id], uselist=False)

    def __init__(
        self,
        name,
        tenant_id,
        team_id=None,
        id=None,
        level=None,
        email=None,
        github_user_id=None,
        manager_id=None,
        is_manager=False,
        tags=None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.manager_id = manager_id
        self.is_manager = is_manager
        self.team_id = team_id
        self.email = email
        self.github_user_id = github_user_id
        self.tags = tags
        self.level = level

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "managerId": self.manager_id,
            "isManager": self.is_manager,
            "teamId": self.team_id,
            "email": self.email,
            "githubUserId": self.github_user_id,
            "tags": self.tags,
            "level": self.level,
            "tenantId": self.tenant_id,
            "tenant": self.tenant.to_dict() if self.tenant else None,
            "team": self.team.to_dict() if self.team else None,
            "manager": self.manager.to_dict() if self.manager else None,
            "githubUser": self.github_user.to_dict() if self.github_user else None,
        }

    def from_dict(data):
        tenant_id = data.get("tenantId", None)
        if not tenant_id:
            tenant = data.get("tenant", None)
            if tenant:
                tenant_id = tenant.get("id", None)
        team_id = data.get("teamId", None)
        if not team_id:
            team = data.get("team", None)
            if team:
                team_id = team.get("id", None)

        return User(
            id=data.get("id", None),
            name=data.get("name", None),
            tenant_id=tenant_id,
            team_id=team_id,
            email=data.get("email", None),
            github_user_id=data.get("githubUserId", None),
            tags=data.get("tags", None),
            manager_id=data.get("managerId", None),
            level=data.get("level", None),
            is_manager=data.get("isManager", False),
        )
