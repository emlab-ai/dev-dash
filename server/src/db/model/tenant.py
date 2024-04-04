from sqlalchemy import BigInteger, Column, Integer, String
from sqlalchemy.orm import relationship
from . import Base

class Tenant(Base):
    __tablename__ = 'tenants'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String)
    oauth_tenant_id = Column(String, unique=True)
    organization_domain = Column(String)
     # Add a relationship to GithubOrg
    github_orgs = relationship('GithubOrg')


    def __init__(self, name, oauth_tenant_id, organization_domain = None, id=None):
        self.id = id
        self.name = name
        self.oauth_tenant_id = oauth_tenant_id
        self.organization_domain = organization_domain

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'oauthTenantId': self.oauth_tenant_id,
            'organizationDomain': self.organization_domain,
            'githubOrgs': [github_org.to_dict() for github_org in self.github_orgs if github_org.installation_id is not None] if hasattr(self, 'github_orgs') else [],
        }