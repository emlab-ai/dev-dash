from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from . import Base

class RepoSettings(Base):
    __tablename__ = 'repo_settings'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tenant_id = Column(BigInteger, ForeignKey('tenants.id'))
    tenant = relationship('Tenant', lazy=True)
    
    description = Column(String)
    enable_description_review = Column(Boolean)
    review_prompt = Column(String)
    disable_tracking = Column(Boolean)

    repository_id = Column(BigInteger, ForeignKey('github_repos.id'))
    repository = relationship('GithubRepo')

    def __init__(self, tenant_id, repository_id, id=None, description=None, review_prompt=None, disable_tracking=False, enable_description_review=False):
        self.id = id
        self.tenant_id = tenant_id
        self.description = description
        self.review_prompt = review_prompt
        self.disable_tracking = disable_tracking
        self.repository_id = repository_id
        self.enable_description_review = enable_description_review
        
    def to_dict(self):
        return {
            'id': self.id,
            'tenantId': self.tenant_id,
            'name': self.repository.name,
            'description': self.description,
            'reviewPrompt': self.review_prompt,
            'disableTracking': self.disable_tracking,
            'repositoryId': self.repository_id,
            'enableDescriptionReview': self.enable_description_review
        }