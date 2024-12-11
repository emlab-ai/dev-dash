import datetime

from sqlalchemy import func
from db.model import GithubPullRequestReview, GithubUser
from db.model.pagedResult import PagedResult


class PullRequestReviewRepository:
    def __init__(self, session):
        self.session = session

    def create(self, review):
        try:
            self.session.add(review)
            self.session.commit()
            return review
        except Exception as error:
            print("Error while creating review:", error)

    def get(self, review_id):
        try:
            review = (
                self.session.query(GithubPullRequestReview)
                .filter_by(id=review_id)
                .first()
            )
            return review
        except Exception as error:
            print("Error while getting review:", error)

    def list_all(
        self,
        tenant_id: int,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        limit=None,
        after=None,
        before=None,
    ):
        if before is not None and after is not None:
            raise ValueError(
                "Both 'before' and 'after' cannot be provided at the same time."
            )

        query = self.session.query(GithubPullRequestReview)
        query = query.filter(GithubPullRequestReview.tenant_id == tenant_id)
        query = query.filter(GithubPullRequestReview.author_id == user_id)
        query = query.filter(
            GithubPullRequestReview.submitted_at >= start_date.date(),
            GithubPullRequestReview.submitted_at <= end_date,
        )
        query = query.join(
            GithubUser, GithubUser.id == GithubPullRequestReview.author_id
        )

        total = query.count()
        if after:
            query = query.filter(GithubPullRequestReview.id > after)
            query = query.order_by(GithubPullRequestReview.id)
        elif before:
            query = query.filter(GithubPullRequestReview.id < before)
            query = query.order_by(GithubPullRequestReview.id.desc())
        else:
            query = query.order_by(GithubPullRequestReview.id)

        if limit:
            query = query.limit(limit + 1)

        query = query.with_entities(
            GithubPullRequestReview.id,
            GithubPullRequestReview.author_id.label("authorId"),
            GithubPullRequestReview.author,
            GithubUser.name.label("authorName"),
            GithubUser.login.label("authorGitalias"),
            # GithubPullRequestReview.prUrl,
            GithubPullRequestReview.state,
            GithubPullRequestReview.submitted_at.label("submittedAt"),
            GithubPullRequestReview.body,
        )

        reviews = query.all()

        hasMore = False
        if limit:
            hasMore = len(reviews) > limit
            if hasMore:
                reviews = reviews[:-1]

        before_cursor = None
        after_cursor = None

        if before:
            reviews = list(reversed(reviews))

        reviews = [review._asdict() for review in reviews]

        if reviews:
            before_cursor = (
                reviews[0]["id"]
                if ((before is not None and hasMore) or after is not None)
                else None
            )
            after_cursor = reviews[-1]["id"] if hasMore or before is not None else None

        return PagedResult(reviews, total, before_cursor, after_cursor)

    def get_count_by_date_user(
        self, tenant_id: int, user_id: int, start_date: datetime, end_date: datetime
    ):
        query = self.session.query(GithubPullRequestReview)
        query = query.filter(GithubPullRequestReview.tenant_id == tenant_id)
        query = query.filter(
            GithubPullRequestReview.submitted_at >= start_date,
            GithubPullRequestReview.submitted_at <= end_date,
            GithubPullRequestReview.author_id == user_id,
        )
        query = query.with_entities(
            func.date_trunc("day", GithubPullRequestReview.submitted_at).label(
                "created_day"
            ),
            func.count(GithubPullRequestReview.id).label("count"),
        )
        query = query.group_by(
            func.date_trunc("day", GithubPullRequestReview.submitted_at)
        )

        prs = query.all()

        delta = end_date - start_date
        labels = [
            (start_date + datetime.timedelta(days=i)).date().isoformat()
            for i in range(delta.days + 1)
        ]
        values = {item.created_day.date().isoformat(): item.count for item in prs}

        data = [values.get(label, 0) for label in labels]

        return {"labels": labels, "data": data}
