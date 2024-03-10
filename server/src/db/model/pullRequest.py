from sqlalchemy import Column, Integer, String, DateTime
from . import Base

class PullRequest(Base):
    __tablename__ = 'pull_requests'

    id = Column(Integer, primary_key=True)
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
    resolvedCommentsCount = Column(Integer)
    commentsCount = Column(Integer)
    reactionsCount = Column(Integer)
    url = Column(String)
    
    
    def __init__(self, author, authorId, prId, number, closedAt, createdAt, changedFiles, deletions, additions, bodyText, title, commitsCount, firstCommitMessage, firstCommitDate, repositoryName, repositoryUrl, reviewThreadsCount, resolvedCommentsCount, commentsCount, reactionsCount, url):
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
        self.resolvedCommentsCount = resolvedCommentsCount
        self.commentsCount = commentsCount
        self.reactionsCount = reactionsCount
        self.url = url

    @property
    def totalDuration(self):
        return (self.closedAt - self.firstCommitDate).total_seconds() / 3600
