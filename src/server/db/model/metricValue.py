import datetime
from sqlalchemy import JSON, BigInteger, Column, DateTime, Float, ForeignKey, Index
from sqlalchemy.orm import relationship

from db.model.metric import PR_METRIC_ID

from . import Base


class MetricValue(Base):
    __tablename__ = "metric_values"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tenant_id = Column(BigInteger, ForeignKey("tenants.id"))
    metric_id = Column(BigInteger, ForeignKey("metrics.id"))
    value1 = Column(Float)
    value2 = Column(Float, nullable=True)
    value3 = Column(Float, nullable=True)
    value4 = Column(Float, nullable=True)
    # source type should be designed on the Metric
    source_id = Column(BigInteger)
    reported_at = Column(DateTime)

    # dimmensions
    dimension1 = Column(BigInteger, nullable=True)
    dimension2 = Column(BigInteger, nullable=True)
    dimension3 = Column(BigInteger, nullable=True)
    dimension4 = Column(BigInteger, nullable=True)
    dimension5 = Column(BigInteger, nullable=True)
    extra_values = Column(JSON, nullable=True)

    tenant = relationship("Tenant", lazy=True)
    __table_args__ = (
        Index('idx_metric_values_1', 'tenant_id', 'metric_id', 'reported_at', 'dimension1'),
        Index('idx_metric_values_2', 'tenant_id', 'metric_id', 'reported_at', 'dimension2'),
        Index('idx_metric_values_3', 'tenant_id', 'metric_id', 'reported_at', 'dimension3'),
        Index('idx_metric_values_4', 'tenant_id', 'metric_id', 'reported_at', 'dimension4'),
        Index('idx_metric_values_5', 'tenant_id', 'metric_id', 'reported_at', 'dimension5'),
    )


def create_pr_metric_value(tenant_id, duration, loc, pr_id, github_user_id, repository_id):
    return MetricValue(
            tenant_id=tenant_id,
            metric_id=PR_METRIC_ID,
            value1=duration,
            value2=loc,
            dimension1=github_user_id,
            dimension2=repository_id,
            source_id=pr_id,
            reported_at=datetime.now(datetime.timezone.utc))
