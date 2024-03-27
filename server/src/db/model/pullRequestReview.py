from sqlalchemy import Column, String, Date, Integer, Text
from . import Base

class PullRequestReview(Base):
    __tablename__ = 'pull_requests_reviews'

    id = Column(Integer, primary_key=True)
    prUrl = Column(String)
    state = Column(String)
    createdAt = Column(Date)
    publishedAt = Column(Date)
    author = Column(String)
    authorId = Column(Integer)
    body = Column(Text)

    def __init__(self, prUrl, state, createdAt, publishedAt, author, authorId, body):
        self.prUrl = prUrl
        self.state = state
        self.createdAt = createdAt
        self.publishedAt = publishedAt
        self.author = author
        self.authorId = authorId
        self.body = body

    def to_dict(self):
        return {
            'id': self.id,
            'prUrl': self.prUrl,
            'state': self.state,
            'createdAt': self.createdAt,
            'publishedAt': self.publishedAt,
            'author': self.author,
            'authorId': self.authorId,
            'body': self.body
        }