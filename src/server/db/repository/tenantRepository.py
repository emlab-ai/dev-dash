from db.model import Tenant
from db.model.pagedResult import PagedResult
from db.repository.repository import process_paged_result


class TenantRepository:
    def __init__(self, session):
        self.session = session

    def create(self, tenant):
        self.session.add(tenant)
        self.session.commit()
        return tenant

    def get(self, tenant_id) -> Tenant:
        tenant = self.session.query(Tenant).filter(Tenant.id == tenant_id).first()
        return tenant

    def get_by_oauth_tenant_id(self, oauth_tenant_id) -> Tenant:
        tenant = (
            self.session.query(Tenant)
            .filter(Tenant.oauth_tenant_id == oauth_tenant_id)
            .first()
        )
        return tenant

    def list_all(self, limit=None, after=None, before=None):
        if before is not None and after is not None:
            raise ValueError(
                "Both 'before' and 'after' cannot be provided at the same time."
            )

        query = self.session.query(Tenant)
        total_count = query.count()

        if after:
            query = query.filter(Tenant.id >= after)
            query = query.order_by(Tenant.id)
        elif before:
            query = query.filter(Tenant.id < before)
            query = query.order_by(Tenant.id.desc())
        else:
            query = query.order_by(Tenant.id)

        if limit:
            query = query.limit(limit + 1)

        result = query.all()
        result = [item._asdict() for item in result]

        result, before_cursor, after_cursor = process_paged_result(
            result, limit, before, after
        )

        return PagedResult(result, total_count, before_cursor, after_cursor)

    def update(self, tenant):
        self.session.merge(tenant)
        self.session.commit()
        return tenant

    def delete(self, tenant_id):
        tenant = self.session.query(Tenant).filter_by(id=tenant_id).first()
        self.session.delete(tenant)
        self.session.commit()
