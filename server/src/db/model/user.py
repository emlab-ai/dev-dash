import json
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship
from . import Base
    
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    isManager = Column(Boolean)
    teamId = Column(Integer, ForeignKey('teams.id'), nullable=True)
    email = Column(String, nullable=True, unique=True)
    gitAlias = Column(String, nullable=True)
    tags = Column(String, nullable=True)
    managerId = Column(Integer, nullable=True)
    level = Column(String, nullable=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=True) #todo: make non nullable
    tenant = relationship('Tenant')
    team = relationship('Team')

    def __init__(self, name, tenant_id, teamId = None, id=None, level = None, email = None, gitAlias = None, managerId=None, isManager=False, tags=None, **kwargs):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.managerId = managerId
        self.isManager = isManager
        self.teamId = teamId
        self.email = email
        self.gitAlias = gitAlias
        self.tags = tags
        self.level = level

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'managerId': self.managerId,
            'isManager': self.isManager,
            'teamId': self.teamId,
            'email': self.email,
            'gitAlias': self.gitAlias,
            'tags': self.tags,
            'level': self.level,
            'tenant': self.tenant.to_dict() if self.tenant else None,
            'team': self.team.to_dict() if self.team else None,
        }
