from sqlalchemy import Column, Integer, String, Uuid
from . import Base

class Team(Base):
    __tablename__ = 'teams'

    id = Column(Uuid, primary_key=True)
    name = Column(String)
    tags = Column(String, nullable=True)
    parentId = Column(Uuid, nullable=True)
    gitHubTeamId = Column(String, nullable=True)

    def __init__(self, name, id=None, parentId=None, tags=None, gitHubTeamId=None, **kwargs):
        self.id = id
        self.name = name
        self.tags = tags
        self.parentId = parentId
        self.gitHubTeamId = gitHubTeamId

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'tags': self.tags,
            'parentId': self.parentId,
            'gitHubTeamId': self.gitHubTeamId
        }