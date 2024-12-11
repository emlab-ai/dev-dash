from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, String
from sqlalchemy.orm import relationship
from . import Base


class GithubOrg(Base):
    __tablename__ = "github_orgs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tenant_id = Column(BigInteger, ForeignKey("tenants.id"))
    tenant = relationship("Tenant", back_populates="github_orgs", lazy=True)
    name = Column(String(2000))
    node_id = Column(String(128))
    avatar_url = Column(String(2000))
    url = Column(String(2000))
    type = Column(String(128))
    installation_id = Column(BigInteger)
    deleted = Column(Boolean)

    def __init__(
        self,
        tenant_id,
        name=None,
        node_id=None,
        avatar_url=None,
        url=None,
        type=None,
        deleted=False,
        installation_id=None,
        id=None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.node_id = node_id
        self.avatar_url = avatar_url
        self.url = url
        self.type = type
        self.installation_id = installation_id
        self.deleted = deleted

    def to_dict(self):
        return {
            "id": self.id,
            "tenantId": self.tenant_id,
            "name": self.name,
            "nodeId": self.node_id,
            "avatarUrl": self.avatar_url,
            "url": self.url,
            "type": self.type,
            "installationId": self.installation_id,
            "deleted": self.deleted,
        }
