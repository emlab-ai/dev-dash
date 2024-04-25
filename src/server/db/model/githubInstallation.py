from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship

from db.model import GithubOrg, Tenant
from . import Base

class GithubInstallation(Base):
    __tablename__ = 'github_installations'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    installation_id = Column(BigInteger)
    installation_token = Column(String(256))
    deleted = Column(Boolean)
    tenant_id = Column(BigInteger, ForeignKey('tenants.id'))
    org_id = Column(BigInteger, ForeignKey('github_orgs.id'))
    tenant = relationship(Tenant.__name__)
    org = relationship(GithubOrg.__name__)
    imported_at = Column(DateTime)

    def __init__(self, installation_token, tenant_id, deleted = False, imported_at = None, installation_id=None, org_id = None):
        self.installation_id = installation_id
        self.installation_token = installation_token
        self.tenant_id = tenant_id
        self.org_id = org_id
        self.deleted = deleted
        self.imported_at = imported_at

    def to_dict(self):
        return {
            'id': self.id,
            'installationId': self.installation_id,
            'installationToken': self.installation_token,
            'tenantId': self.tenant_id,
            'orgId': self.org_id,
            'imported_at': self.imported_at,
        }