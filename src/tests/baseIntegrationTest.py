from time import sleep
from unittest import IsolatedAsyncioTestCase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from testcontainers.postgres import PostgresContainer
from db.model import Base
from db.model.tenant import Tenant
from db.repository.asyncRepository import AsyncRepository


class BaseIntegrationTest(IsolatedAsyncioTestCase):
    session: AsyncSession
    tenant: Tenant

    @classmethod
    def setUpClass(cls):
        """Start the PostgreSQL container."""
        cls.postgres = PostgresContainer("postgres:16-alpine")
        cls.postgres.start()
        sleep(5)

    @classmethod
    def tearDownClass(cls):
        """Stop the PostgreSQL container."""
        cls.postgres.stop()

    async def asyncSetUp(self):
        """Set up the database and session for each test."""
        connection = self._get_sql_connection_string(is_async=True)
        self.engine = create_async_engine(connection)
        self.async_session_factory = async_sessionmaker(
            bind=self.engine,  expire_on_commit=False
        )
        self.session = self.async_session_factory()

        # Run database migrations or create tables
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        tenantRepository = AsyncRepository(Tenant, self.session)
        self.tenant = await tenantRepository.find_one_async(Tenant.oauth_tenant_id == "test_tenant")
        if not self.tenant:
            self.tenant = await tenantRepository.create_async(Tenant(name="Test Tenant", oauth_tenant_id="test_tenant"))

    async def asyncTearDown(self):
        """Dispose of the session and engine after each test."""
        await self.session.close()
        await self.engine.dispose()

    def _get_sql_connection_string(self, is_async=False):
        """Generate the SQL connection string."""
        url = self.postgres.get_connection_url()
        if is_async:
            return url.replace("postgresql+psycopg2", "postgresql+asyncpg")
        return url
