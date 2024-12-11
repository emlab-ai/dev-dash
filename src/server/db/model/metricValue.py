from click import DateTime
from sqlalchemy import JSON, BigInteger, Column, Float, ForeignKey
from sqlalchemy.orm import relationship

from . import Base


class MetricValue(Base):
    __tablename__ = "metrics"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tenant_id = Column(BigInteger, ForeignKey("tenants.id"))
    metric_id = Column(BigInteger, ForeignKey("metrics.id"))
    value = Column(Float)
    # source type should be degined on the Metric
    source_id = Column(BigInteger)
    reported_at = Column(DateTime)

    # dimmensions
    user_id = Column(BigInteger, nullable=True)
    team_id = Column(BigInteger, nullable=True)
    github_user_id = Column(BigInteger, nullable=True)
    github_org_id = Column(BigInteger, nullable=True)
    github_pr_id = Column(BigInteger, nullable=True)
    dimensions = Column(JSON, nullable=True)

    tenant = relationship("Tenant", lazy=True)
