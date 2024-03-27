from sqlalchemy import Column, Integer, String
from . import Base

class Tenant(Base):
    __tablename__ = 'tenants'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    oauth_tenant_id = Column(String, unique=True)
    organization_domain = Column(String)
    github_installation_id = Column(Integer, unique=True)
    github_installation_token = Column(String)

    def __init__(self, name, oauth_tenant_id, github_installation_id=None, organization_domain = None, github_installation_token = None, id=None):
        self.id = id
        self.name = name
        self.github_installation_id = github_installation_id
        self.oauth_tenant_id = oauth_tenant_id
        self.organization_domain = organization_domain
        self.github_installation_token = github_installation_token

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'github_installation_id': self.github_installation_id,
            'oauth_tenant_id': self.oauth_tenant_id,
            'organization_domain': self.organization_domain,
            'github_installation_token': self.github_installation_token
        }