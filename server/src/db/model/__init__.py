from sqlalchemy.orm import registry

mapper_registry = registry()
Base = mapper_registry.generate_base()

from .team import Team
from .user import User
from .pullRequest import PullRequest
from .pullRequestReview import PullRequestReview
from .pullRequestComment import PullRequestComment