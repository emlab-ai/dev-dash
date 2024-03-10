from sqlalchemy import Column, Integer, String
from . import Base

class Team(Base):
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    tags = Column(String, nullable=True)
    tribeId = Column(Integer)

    def __init__(self, name, tribeId, tags=None):
        self.name = name
        self.tags = tags
        self.tribeId = tribeId