from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    ForeignKey,
    String,
    Date,
    Integer,
    Text,
)
from sqlalchemy.orm import relationship
from . import Base


class GithubPullRequestReviewComment(Base):
    __tablename__ = "github_pull_request_review_comments"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tenant_id = Column(BigInteger, ForeignKey("tenants.id"))
    tenant = relationship("Tenant", lazy=True)
    org_id = Column(BigInteger)
    node_id = Column(String(128))
    thread_id = Column(String, nullable=True)
    is_resolved = Column(Boolean, nullable=True)
    is_outdated = Column(Boolean, nullable=True)
    author = Column(String)
    author_id = Column(BigInteger)
    reactions_count = Column(Integer)
    created_at = Column(Date)
    updated_at = Column(Date)
    pr_id = Column(BigInteger)
    pr_number = Column(Integer)
    repo_id = Column(BigInteger)
    body = Column(Text)
    commit_id = Column(String(256))
    pr_review_id = Column(BigInteger)
    author_association = Column(String(256))

    def __init__(
        self,
        tenant_id,
        org_id,
        node_id,
        thread_id,
        pr_review_id,
        commit_id,
        is_resolved,
        is_outdated,
        author,
        author_id,
        reactions_count,
        created_at,
        updated_at,
        pr_id,
        pr_number,
        repo_id,
        body,
        author_association,
        id=None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.org_id = org_id
        self.node_id = node_id
        self.commit_id = commit_id
        self.thread_id = thread_id
        self.is_resolved = is_resolved
        self.is_outdated = is_outdated
        self.author = author
        self.author_id = author_id
        self.reactions_count = reactions_count
        self.created_at = created_at
        self.pr_id = pr_id
        self.pr_number = pr_number
        self.repo_id = repo_id
        self.body = body
        self.updated_at = updated_at
        self.author_association = author_association
        self.pr_review_id = pr_review_id

    def to_dict(self):
        return {
            "id": self.id,
            "tenantId": self.tenant_id,
            "orgId": self.org_id,
            "nodeId": self.node_id,
            "threadId": self.thread_id,
            "isResolved": self.is_resolved,
            "isOutdated": self.is_outdated,
            "author": self.author,
            "authorId": self.author_id,
            "commitId": self.commit_id,
            "reactionsCount": self.reactions_count,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "prId": self.pr_id,
            "prNumber": self.pr_number,
            "repoId": self.repo_id,
            "prReviewId": self.pr_review_id,
            "body": self.body,
            "authorAssociation": self.author_association,
        }
