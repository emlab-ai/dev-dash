from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    ForeignKey,
    String,
)
from . import Base
from sqlalchemy.orm import relationship


class GithubRepo(Base):
    __tablename__ = "github_repos"

    id = Column(BigInteger, primary_key=True)
    tenant_id = Column(BigInteger, ForeignKey("tenants.id"))
    org_id = Column(BigInteger, ForeignKey("github_orgs.id"))
    node_id = Column(String(128))
    name = Column(String)
    full_name = Column(String)
    private = Column(Boolean)
    deleted = Column(Boolean)

    tenant = relationship("Tenant", lazy=True)
    github_org = relationship("GithubOrg", lazy=True)

    def __init__(
        self,
        id: int,
        tenant_id: int,
        org_id: int,
        node_id: str,
        name,
        full_name: str,
        private: bool = False,
        deleted=False,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.org_id = org_id
        self.node_id = node_id
        self.name = name
        self.full_name = full_name
        self.private = private
        self.deleted = deleted

    def to_dict(self):
        return {
            "id": self.id,
            "tenantId": self.tenant_id,
            "orgId": self.org_id,
            "nodeId": self.node_id,
            "name": self.name,
            "fullName": self.full_name,
            "private": self.private,
            "deleted": self.deleted,
        }
