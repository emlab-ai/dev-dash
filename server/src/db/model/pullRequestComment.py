from sqlalchemy import Boolean, Column, String, Date, Integer, Text
from . import Base

class PullRequestComment(Base):
    __tablename__ = 'pull_requests_comments'

    id = Column(Integer, primary_key=True)
    threadId = Column(String)
    prUrl = Column(String)
    isResolved = Column(Boolean, nullable=True)
    isOutdated = Column(Boolean, nullable=True)
    author = Column(String)
    authorId = Column(Integer)
    reactionsCount = Column(Integer)
    createdAt = Column(Date)
    repositoryName = Column(String)
    body = Column(Text)

    def __init__(self, threadId, prUrl, isResolved, isOutdated, author, authorId, reactionsCount, createdAt, repositoryName, body):
        self.threadId = threadId
        self.prUrl = prUrl
        self.isResolved = isResolved
        self.isOutdated = isOutdated
        self.author = author
        self.authorId = authorId
        self.reactionsCount = reactionsCount
        self.createdAt = createdAt
        self.repositoryName = repositoryName
        self.body = body

    def to_dict(self):
        return {
            'id': self.id,
            'threadId': self.threadId,
            'prUrl': self.prUrl,
            'isResolved': self.isResolved,
            'isOutdated': self.isOutdated,
            'author': self.author,
            'authorId': self.authorId,
            'reactionsCount': self.reactionsCount,
            'createdAt': self.createdAt,
            'repositoryName': self.repositoryName,
            'body': self.body
        }