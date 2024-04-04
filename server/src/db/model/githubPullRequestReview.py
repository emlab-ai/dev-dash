from sqlalchemy import BigInteger, Column, ForeignKey, String, Date, Integer, Text
from sqlalchemy.orm import relationship

from . import Base

class GithubPullRequestReview(Base):
    __tablename__ = 'github_pull_requests_reviews'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    node_id = Column(String(128))
    tenant_id = Column(BigInteger, ForeignKey('tenants.id'))
    tenant = relationship('Tenant', lazy=True)
    org_id = Column(BigInteger)
    pr_id = Column(BigInteger)
    pr_number = Column(Integer)
    repo_id = Column(BigInteger)    
    state = Column(String)
    submitted_at = Column(Date)
    author = Column(String)
    author_id = Column(BigInteger)
    body = Column(Text)
    commit_id = Column(String(256))
    state = Column(String(64))

    def __init__(self, tenant_id, node_id, pr_id, org_id, pr_number, repo_id, state, submitted_at, author, author_id, body, commit_id, id=None):
        self.id = id
        self.tenant_id = tenant_id
        self.node_id = node_id
        self.org_id = org_id
        self.pr_id = pr_id
        self.pr_number = pr_number
        self.repo_id = repo_id
        self.state = state
        self.submitted_at = submitted_at
        self.author = author
        self.author_id = author_id
        self.body = body
        self.commit_id = commit_id

    def to_dict(self):
        return {
            'id': self.id,
            'tenantId': self.tenant_id,
            'prId': self.pr_id,
            'orgId': self.org_id,
            'prNumber': self.pr_number,
            'repoId': self.repo_id,
            'state': self.state,
            'publishedAt': self.submitted_at,
            'author': self.author,
            'authorId': self.author_id,
            'body': self.body,
            'commitId': self.commit_id,
            'nodeId': self.node_id
        }