import json
from sqlalchemy import Column, Integer, String, Boolean
from . import Base

    
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    team = Column(String)
    isManager = Column(Boolean)
    teamId = Column(Integer)
    email = Column(String, nullable=True)
    gitAlias = Column(String, nullable=True)
    tags = Column(String, nullable=True)
    managerId = Column(Integer, nullable=True)
    level = Column(String, nullable=True)

    def __init__(self, name, teamId, id=None, level = None, email = None, gitAlias = None, managerId=None, isManager=False, tags=None, **kwargs):
        self.id = id
        self.name = name
        self.managerId = managerId
        self.isManager = isManager
        self.teamId = teamId
        self.email = email
        self.gitAlias = gitAlias
        self.tags = tags
        self.level = level
