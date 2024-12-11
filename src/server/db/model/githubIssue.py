from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    DateTime,
    BigInteger,
)
from sqlalchemy.orm import relationship
from . import Base


class GithubIssue(Base):
    __tablename__ = "github_issues"

    id = Column(BigInteger, primary_key=True)
    node_id = Column(String(128))
    number = Column(BigInteger)
    title = Column(String)
    user_id = Column(BigInteger)
    user_login = Column(String)
    state = Column(String)
    locked = Column(Boolean)
    comments = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    closed_at = Column(DateTime)
    author_association = Column(String)
    body = Column(String)

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
        number,
        title,
        user_id,
        user_login,
        state,
        locked,
        comments,
        created_at,
        updated_at,
        closed_at,
        author_association,
        body,
        org_id,
        tenant_id,
        repo_id,
    ):
        self.id = id
        self.node_id = node_id
        self.number = number
        self.title = title
        self.user_id = user_id
        self.user_login = user_login
        self.state = state
        self.locked = locked
        self.comments = comments
        self.created_at = created_at
        self.updated_at = updated_at
        self.closed_at = closed_at
        self.author_association = author_association
        self.body = body
        self.org_id = org_id
        self.tenant_id = tenant_id
        self.repo_id = repo_id

    def to_dict(self):
        return {
            "id": self.id,
            "nodeId": self.node_id,
            "number": self.number,
            "title": self.title,
            "userId": self.user_id,
            "userLogin": self.user_login,
            "state": self.state,
            "locked": self.locked,
            "comments": self.comments,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "closedAt": self.closed_at,
            "authorAssociation": self.author_association,
            "body": self.body,
            "orgId": self.org_id,
            "tenantId": self.tenant_id,
            "repoId": self.repo_id,
        }
