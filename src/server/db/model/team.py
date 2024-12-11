from sqlalchemy import BigInteger, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from . import Base


class Team(Base):
    __tablename__ = "teams"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tenant_id = Column(BigInteger, ForeignKey("tenants.id"))
    tenant = relationship("Tenant", lazy=True)
    name = Column(String)
    tags = Column(String, nullable=True)
    parent_id = Column(BigInteger, nullable=True)
    github_team_id = Column(String, nullable=True)

    def __init__(
        self, name, tenant_id, id=None, parent_id=None, tags=None, github_team_id=None
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.tags = tags
        self.parent_id = parent_id
        self.github_team_id = github_team_id

    def to_dict(self):
        return {
            "id": self.id,
            "tenantId": self.tenant_id,
            "name": self.name,
            "tags": self.tags,
            "parentId": self.parent_id,
            "githubTeamId": self.github_team_id,
        }
