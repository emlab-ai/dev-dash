from sqlalchemy import Column, Integer, String
from . import Base

class Tribe(Base):
    __tablename__ = 'tribes'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self, name):
        self.name = name