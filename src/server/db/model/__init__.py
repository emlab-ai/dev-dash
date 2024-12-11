# flake8: noqa: F401
from sqlalchemy.orm import registry

mapper_registry = registry()
Base = mapper_registry.generate_base()


from .team import Team
from .user import User
from .tenant import Tenant
from .pullRequest import PullRequest
from .githubPullRequestReview import GithubPullRequestReview
from .githubPullRequestReviewComment import GithubPullRequestReviewComment
from .githubEvent import GithubEvent
from .githubUser import GithubUser
from .githubRepo import GithubRepo
from .githubOrg import GithubOrg
from .githubIssueComment import GithubIssueComment

# from .githubIssue import GithubIssue
from .githubInstallation import GithubInstallation


