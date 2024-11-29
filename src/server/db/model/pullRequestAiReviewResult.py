from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from . import Base

class PullRequestAiReviewResult(Base):
    __tablename__ = 'pull_request_ai_review_results'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tenant_id = Column(BigInteger, ForeignKey('tenants.id'))
    tenant = relationship('Tenant', lazy=True)
    
    summary = Column(String)
    result = Column(String)
    score = Column(Integer)
    pr_id = Column(BigInteger)
    github_user_id = Column(BigInteger)
    tokens_used=Column(Integer)

    def __init__(self, tenant_id, pr_id, github_user_id, id=None, summary=None, result=None, score=None, tokens_used=None):
        self.id = id
        self.tenant_id = tenant_id
        self.pr_id = pr_id
        self.github_user_id = github_user_id
        self.summary = summary
        self.result = result
        self.score = score     
        self.tokens_used = tokens_used   
        
    def to_dict(self):
        return {
            'id': self.id,
            'tenantId': self.tenant_id,
            'summary': self.summary,
            'result': self.result,
            'score': self.score,
            'prId': self.pr_id,
            'githubUserId': self.github_user_id,
            'tokensUsed': self.tokens_used
        }