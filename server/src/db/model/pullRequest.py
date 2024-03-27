from sqlalchemy import Column, Integer, String, DateTime
from . import Base

class PullRequest(Base):
    __tablename__ = 'pull_requests'

    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer)

    author = Column(String)
    authorId = Column(Integer)
    prId = Column(String)
    number = Column(Integer)
    closedAt = Column(DateTime)
    createdAt = Column(DateTime)
    changedFiles = Column(Integer, nullable=True)
    deletions = Column(Integer)
    additions = Column(Integer)
    bodyText = Column(String)
    title = Column(String)
    commitsCount = Column(Integer)
    firstCommitMessage = Column(String)
    firstCommitDate = Column(DateTime)
    repositoryName = Column(String)
    repositoryUrl = Column(String)
    reviewThreadsCount = Column(Integer)
    commentsCount = Column(Integer)
    reactionsCount = Column(Integer)
    url = Column(String)
    
    def __init__(self, tenant_id, author, authorId, prId, number, closedAt, createdAt, changedFiles, deletions, additions, bodyText, title, commitsCount, firstCommitMessage, firstCommitDate, repositoryName, repositoryUrl, reviewThreadsCount, commentsCount, reactionsCount, url):
        self.tenant_id = tenant_id
        self.author = author
        self.authorId = authorId
        self.prId = prId
        self.number = number
        self.closedAt = closedAt
        self.createdAt = createdAt
        self.changedFiles = changedFiles
        self.deletions = deletions
        self.additions = additions
        self.bodyText = bodyText
        self.title = title
        self.commitsCount = commitsCount
        self.firstCommitMessage = firstCommitMessage
        self.firstCommitDate = firstCommitDate
        self.repositoryName = repositoryName
        self.repositoryUrl = repositoryUrl
        self.reviewThreadsCount = reviewThreadsCount
        self.commentsCount = commentsCount
        self.reactionsCount = reactionsCount
        self.url = url

    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'author': self.author,
            'authorId': self.authorId,
            'prId': self.prId,
            'number': self.number,
            'closedAt': self.closedAt,
            'createdAt': self.createdAt,
            'changedFiles': self.changedFiles,
            'deletions': self.deletions,
            'additions': self.additions,
            'bodyText': self.bodyText,
            'title': self.title,
            'commitsCount': self.commitsCount,
            'firstCommitMessage': self.firstCommitMessage,
            'firstCommitDate': self.firstCommitDate,
            'repositoryName': self.repositoryName,
            'repositoryUrl': self.repositoryUrl,
            'reviewThreadsCount': self.reviewThreadsCount,
            'commentsCount': self.commentsCount,
            'reactionsCount': self.reactionsCount,
            'url': self.url
        }