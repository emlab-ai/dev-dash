from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from . import Base


class PullRequest(Base):
    __tablename__ = "pull_requests"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tenant_id = Column(BigInteger, ForeignKey("tenants.id"))
    tenant = relationship("Tenant", lazy=True)

    author = Column(String(256))
    author_id = Column(BigInteger)
    node_id = Column(String(128))
    org_id = Column(BigInteger)
    repository_id = Column(BigInteger, ForeignKey("github_repos.id"))
    number = Column(Integer)
    closed_at = Column(DateTime)
    created_at = Column(DateTime)
    changed_files = Column(Integer, default=0)
    deletions = Column(Integer)
    additions = Column(Integer)
    body = Column(String)
    title = Column(String(2000))
    commits_count = Column(Integer)
    first_commit_message = Column(String)
    first_commit_date = Column(DateTime)
    review_threads_count = Column(Integer)
    comments_count = Column(Integer)
    url = Column(String(2000))
    state = Column(String(64), nullable=True)

    repository = relationship("GithubRepo")

    def __init__(
        self,
        id,
        tenant_id,
        author,
        author_id,
        node_id,
        org_id,
        repository_id,
        number,
        closed_at,
        created_at,
        changed_files,
        deletions,
        additions,
        body,
        title,
        commits_count,
        first_commit_message,
        first_commit_date,
        review_threads_count,
        comments_count,
        url,
        state,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.author = author
        self.author_id = author_id
        self.node_id = node_id
        self.org_id = org_id
        self.repository_id = repository_id
        self.number = number
        self.closed_at = closed_at
        self.created_at = created_at
        self.changed_files = changed_files
        self.deletions = deletions
        self.additions = additions
        self.body = body
        self.title = title
        self.commits_count = commits_count
        self.first_commit_message = first_commit_message
        self.first_commit_date = first_commit_date
        self.review_threads_count = review_threads_count
        self.comments_count = comments_count
        self.url = url
        self.state = state

    def to_dict(self):
        return {
            "id": self.id,
            "tenantId": self.tenant_id,
            "author": self.author,
            "authorId": self.author_id,
            "nodeId": self.node_id,
            "orgId": self.org_id,
            "repositoryId": self.repository_id,
            "number": self.number,
            "closedAt": self.closed_at,
            "createdAt": self.created_at,
            "changedFiles": self.changed_files,
            "deletions": self.deletions,
            "additions": self.additions,
            "body": self.body,
            "title": self.title,
            "commitsCount": self.commits_count,
            "firstCommitMessage": self.first_commit_message,
            "firstCommitDate": self.first_commit_date,
            "reviewThreadsCount": self.review_threads_count,
            "commentsCount": self.comments_count,
            "url": self.url,
            "state": self.state,
        }
