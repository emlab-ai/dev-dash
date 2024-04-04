from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Integer, String, DateTime, JSON
from . import Base
from sqlalchemy.orm import relationship

class GithubEvent(Base):
    __tablename__ = 'github_events'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    installation_id = Column(BigInteger)
    received_at = Column(DateTime)
    delivery_id = Column(String)
    data = Column(JSON)
    failed = Column(Boolean)
    error_text = Column(String)

    def __init__(self, installation_id, received_at, delivery_id, data, failed=False, error_text=None, id=None):
        self.id = id
        self.installation_id = installation_id
        self.received_at = received_at
        self.delivery_id = delivery_id
        self.failed = failed
        self.error_text = error_text
        self.data = data

    def to_dict(self):
        return {
            'id': self.id,
            'installationId': self.installation_id,
            'receivedt': self.received_at,
            'deliveryId': self.delivery_id,
            'data': self.data,
            'error': self.error,
            'errorText': self.error_text
        }