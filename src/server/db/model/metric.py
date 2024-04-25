from sqlalchemy import JSON, BigInteger, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from . import Base

class Metric(Base):
    __tablename__ = 'metrics'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tenant_id = Column(BigInteger, ForeignKey('tenants.id'))
    tenant = relationship('Tenant', lazy=True)
    enabled = Column(Boolean)
    name = Column(String)
    source_type = Column(String)
    hasPrDimension = Column(Boolean)
    hasUserDimension = Column(Boolean)
    hasOrgDimension = Column(Boolean)
    customDimensions = Column(JSON, nullable=True)

    def __init__(self, name, tenant_id, source_type, hasPrDimension, hasUserDimension, hasOrgDimension, customDimensions = None, enabled=True, id=None):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name

    def to_dict(self):
        return {
            'id': self.id,
            'tenantId': self.tenant_id,
            'name': self.name,
        }
        
def setup_tenant_metrics(tenant, session):
    