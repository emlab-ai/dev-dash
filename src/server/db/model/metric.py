from sqlalchemy import JSON, BigInteger, Boolean, Column, String

from db.repository.asyncRepository import AsyncRepository

from . import Base


class Metric(Base):
    __tablename__ = "metrics"

    id = Column(BigInteger, primary_key=True)
    name = Column(String)
    source_type = Column(String)
    structure = Column(JSON, nullable=True)

    def __init__(
        self,
        name,
        source_type,
        structure=None,
        id=None,
    ):
        self.id = id
        self.name = name
        self.source_type = source_type
        self.structure = structure

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "sourceType": self.source_type,
            "structure": self.structure,
        }


PR_METRIC_ID: int = 1


async def setup_tenant_metrics(session):
    repo = AsyncRepository(Metric, session)
    prMetric = await repo.find_one_async(Metric.name == "Pull Request")
    if prMetric is None:
        await repo.create_async(
            Metric(
                id=PR_METRIC_ID,
                name="Pull Request",
                source_type="github",
                structure={
                    "value1": "duration",
                    "value2": "loc",
                    "dimensions1": "github_user_id",
                    "dimensions2": "repository_id",
                },
            )
        )

