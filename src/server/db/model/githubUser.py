from sqlalchemy import BigInteger, Column, ForeignKey, String
from sqlalchemy.orm import relationship
from . import Base


class GithubUser(Base):
    __tablename__ = "github_users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tenant_id = Column(BigInteger, ForeignKey("tenants.id"))
    tenant = relationship("Tenant", lazy=True)
    login = Column(String)
    email = Column(String)
    name = Column(String)
    node_id = Column(String(128))
    avatar_url = Column(String)

    def __init__(self, id, name, email, tenant_id, login, node_id, avatar_url):
        self.id = id
        self.name = name
        self.email = email
        self.tenant_id = tenant_id
        self.login = login
        self.node_id = node_id
        self.avatar_url = avatar_url

    def to_dict(self):
        return {
            "id": self.id,
            "tenantId": self.tenant_id,
            "name": self.name,
            "email": self.email,
            "login": self.login,
            "nodeId": self.node_id,
            "avatarUrl": self.avatar_url,
        }
