from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    DateTime,
)
from . import Base
from sqlalchemy.orm import relationship


class GithubIssueComment(Base):
    __tablename__ = "github_issue_comments"

    id = Column(BigInteger, primary_key=True)
    node_id = Column(String(128))
    author = Column(String)
    author_id = Column(BigInteger)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    author_association = Column(String)
    body = Column(String)
    issue_number = Column(Integer)
    issue_id = Column(BigInteger)
    is_pr = Column(Boolean, default=False)

    org_id = Column(BigInteger, ForeignKey("github_orgs.id"))
    tenant_id = Column(BigInteger, ForeignKey("tenants.id"))
    repo_id = Column(BigInteger, ForeignKey("github_repos.id"))

    org = relationship("GithubOrg", lazy=True)
    tenant = relationship("Tenant", lazy=True)
    repo = relationship("GithubRepo", lazy=True)

    def __init__(
        self,
        id,
        node_id,
        author,
        is_pr,
        author_id,
        created_at,
        updated_at,
        author_association,
        body,
        org_id,
        tenant_id,
        issue_number,
        issue_id,
        repo_id,
    ):
        self.id = id
        self.node_id = node_id
        self.author = author
        self.author_id = author_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.author_association = author_association
        self.body = body
        self.org_id = org_id
        self.tenant_id = tenant_id
        self.issue_number = issue_number
        self.issue_id = issue_id
        self.is_pr = is_pr
        self.repo_id = repo_id

    def to_dict(self):
        return {
            "id": self.id,
            "nodeId": self.node_id,
            "author": self.author,
            "authorId": self.author_id,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "authorAssociation": self.author_association,
            "body": self.body,
            "orgId": self.org_id,
            "tenantId": self.tenant_id,
            "issueNumber": self.issue_number,
            "issueId": self.issue_id,
            "isPR": self.is_pr,
            "repoId": self.repo_id,
        }
