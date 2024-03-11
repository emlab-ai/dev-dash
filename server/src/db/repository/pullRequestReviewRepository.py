import datetime

from sqlalchemy import func
from db.model import PullRequestReview, User
from db.model.pagedResult import PagedResult
from utils import entity_as_dict

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
            review = self.session.query(PullRequestReview).filter_by(id=review_id).first()
            return review
        except Exception as error:
            print("Error while getting review:", error)

    def list_all(self, user_id:int, start_date:datetime, end_date:datetime, limit=None, after=None, before=None):
        try:
            if before is not None and after is not None:
                raise ValueError("Both 'before' and 'after' cannot be provided at the same time.")
            
            query = self.session.query(PullRequestReview)
            query = query.filter(PullRequestReview.authorId == user_id)
            query = query.filter(PullRequestReview.createdAt >= start_date.date(), PullRequestReview.createdAt <= end_date)
            query = query.join(User, User.id == PullRequestReview.authorId)
            
            total = query.count()
            if after:
                query = query.filter(PullRequestReview.id > after)
                query = query.order_by(PullRequestReview.id)
            elif before:
                query = query.filter(PullRequestReview.id < before)
                query = query.order_by(PullRequestReview.id.desc())
            else :
                query  = query.order_by(PullRequestReview.id)

            if limit:
                query = query.limit(limit + 1)
            
            query = query.with_entities(
                PullRequestReview.id,
                PullRequestReview.authorId,
                PullRequestReview.author,
                User.name.label('author_name'),
                PullRequestReview.prUrl,
                PullRequestReview.state,
                PullRequestReview.createdAt,
                PullRequestReview.body
            )
                
            reviews = query.all()

            hasMore = False
            if limit:
                hasMore = len(reviews) > limit
                if (hasMore):
                    reviews = reviews[:-1]

            before_cursor = None
            after_cursor = None

            if before:
                reviews = list(reversed(reviews))

            reviews = [review._asdict() for review in reviews]
            
            if reviews:
                before_cursor = reviews[0]['id'] if ((before is not None and hasMore) or after is not None)  else None
                after_cursor = reviews[-1]['id'] if hasMore or before is not None else None
                    

            return PagedResult(reviews, total, before_cursor, after_cursor)
             
        except Exception as error:
            print("Error while listing reviews:", error)

 