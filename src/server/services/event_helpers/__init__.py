from db.model import PullRequest
from db.model import GithubIssueComment
from db.model import GithubPullRequestReview, GithubRepo
from db.model import GithubPullRequestReviewComment
from db.model.githubIssue import GithubIssue


def pull_request_event_to_model(tenant, data) -> PullRequest:
    pull_request = data["pull_request"]
    organization = data["organization"]
    repository = data["repository"]

    return PullRequest(
        id=pull_request["id"],
        tenant_id=tenant.id,
        author=pull_request["user"]["login"],
        author_id=pull_request["user"]["id"],
        node_id=pull_request["node_id"],
        number=pull_request["number"],
        org_id=organization["id"],
        repository_id=repository["id"],
        closed_at=pull_request["merged_at"] or pull_request["closed_at"],
        created_at=pull_request["created_at"],
        changed_files=pull_request["changed_files"],
        deletions=pull_request["deletions"],
        additions=pull_request["additions"],
        body=pull_request["body"],
        title=pull_request["title"],
        commits_count=pull_request["commits"],
        first_commit_message=None,
        first_commit_date=None,
        review_threads_count=pull_request["review_comments"],
        comments_count=pull_request["comments"],
        url=pull_request["html_url"],
        state=pull_request["state"] if not bool(pull_request["merged"]) else "merged",
    )


def issue_comment_to_model(tenant, data) -> GithubIssueComment:
    comment = data["comment"]
    issue = data["issue"]
    organization = data["organization"]
    repository = data["repository"]

    return GithubIssueComment(
        id=comment["id"],
        tenant_id=tenant.id,
        author=comment["user"]["login"],
        author_id=comment["user"]["id"],
        node_id=comment["node_id"],
        created_at=comment["created_at"],
        updated_at=comment["updated_at"],
        author_association=comment["author_association"],
        body=comment["body"],
        org_id=organization["id"],
        issue_id=issue["id"],
        issue_number=issue["number"],
        is_pr="pull_request" in issue,
        repo_id=repository["id"],
    )


def pull_request_review_to_model(tenant, data) -> GithubPullRequestReview:
    pull_request = data["pull_request"]
    review = data["review"]
    repository = data["repository"]
    org_id = data["organization"]["id"]

    return GithubPullRequestReview(
        id=review["id"],
        node_id=review["node_id"],
        tenant_id=tenant.id,
        author_id=review["user"]["id"],
        author=review["user"]["login"],
        state=review["state"],
        submitted_at=review["submitted_at"],
        body=review["body"],
        repo_id=repository["id"],
        pr_id=pull_request["id"],
        pr_number=pull_request["number"],
        commit_id=review["commit_id"],
        org_id=org_id,
    )


def pull_request_review_comment_to_model(
    tenant, data
) -> GithubPullRequestReviewComment:
    comment = data["comment"]
    pull_request = data["pull_request"]
    repository = data["repository"]
    org_id = data["organization"]["id"]

    return GithubPullRequestReviewComment(
        id=comment["id"],
        tenant_id=tenant.id,
        org_id=org_id,
        node_id=comment["node_id"],
        thread_id=comment["thread_id"] if "thread_id" in comment else None,
        is_resolved=False,
        is_outdated=False,
        author=comment["user"]["login"],
        author_id=comment["user"]["id"],
        reactions_count=comment["reactions"]["total_count"],
        created_at=comment["created_at"],
        updated_at=comment["updated_at"],
        pr_id=pull_request["id"],
        pr_number=pull_request["number"],
        repo_id=repository["id"],
        body=comment["body"],
        pr_review_id=comment["pull_request_review_id"],
        commit_id=comment["commit_id"],
        author_association=comment["author_association"],
    )


def repository_to_model(tenant, org, repo) -> GithubRepo:
    return GithubRepo(
        id=repo["id"],
        tenant_id=tenant.id,
        org_id=org.id,
        node_id=repo["node_id"],
        name=repo["name"],
        full_name=repo["full_name"],
        private=repo["private"],
    )


def issue_to_model(tenant, data) -> GithubIssue:
    return GithubIssue(
        id=data["issue"]["id"],
        node_id=data["issue"]["node_id"],
        number=data["issue"]["number"],
        title=data["issue"]["title"],
        user_id=data["issue"]["user"]["id"],
        user_login=data["issue"]["user"]["login"],
        state=data["issue"]["state"],
        locked=data["issue"]["locked"],
        comments=data["issue"]["comments"],
        created_at=data["issue"]["created_at"],
        updated_at=data["issue"]["updated_at"],
        closed_at=data["issue"]["closed_at"],
        author_association=data["issue"]["author_association"],
        body=data["issue"]["body"],
        org_id=data["organization"]["id"],
        tenant_id=tenant.id,
        repo_id=data["repository"]["id"],
    )
