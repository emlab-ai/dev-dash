from time import sleep
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.model.tenant import Tenant
from db.repository import UserRepository
from db.model import User
from testcontainers.postgres import PostgresContainer

from db.repository.repository import Repository


postgres = PostgresContainer("postgres:16-alpine")



def setup_async_sql_engine():
    connection_string = get_sql_connection_string(is_async=True)
    async_engine = create_async_engine(
        connection_string,
        pool_size=5,
        max_overflow=5,
        pool_timeout=30,
        pool_recycle=600,
        echo=True,
    )

    Session = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )

    return Session


def get_sql_connection_string(is_async=False):
    global postgres

    url = postgres.get_connection_url()

    if is_async:
        connection_string = url.replace("postgresql+psycopg2", "postgresql+asyncpg")
    else:
        connection_string = url

    return connection_string

class UserRepositoryTests(unittest.TestCase):
    def setUp(self):
        postgres.start()
        connection = get_sql_connection_string(is_async=False)

        for _ in range(10):
            try:
                postgres.exec("SELECT 1")
                break
            except Exception:
                sleep(500)
            raise Exception("Postgres container failed to start")

        # Create an in-memory SQLite database for testing
        self.engine = create_engine(connection)
        User.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()
        self.repository = UserRepository(self.session)
        tenantRepository = Repository(Tenant, self.session)
        self.tenant = tenantRepository.create(Tenant(name="Test Tenant", oauth_tenant_id="test_tenant"))

    def tearDown(self):
        self.session.close()
        self.engine.dispose()
        postgres.stop()
        pass

    def test_create_user(self):
        # Test creating a new user
        user = User(name="John Doe", email="john@example.com", tenant_id=self.tenant.id)
        self.repository.create(user)

        created_user = self.session.query(User).filter_by(name="John Doe").first()

        self.assertIsNotNone(created_user)
        self.assertEqual(created_user.name, "John Doe")
        self.assertEqual(created_user.email, "john@example.com")

    def test_get_user(self):
        # Test retrieving an existing user
        user = User(name="Jane Smith", email="jane@example.com", tenant_id=1)
        self.session.add(user)
        self.session.commit()

        retrieved_user = self.repository.get(user.id)
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.name, "Jane Smith")
        self.assertEqual(retrieved_user.email, "jane@example.com")

    def test_update_user(self):
        # Test updating an existing user
        user = User(name="Alice Brown", email="alice@example.com", tenant_id=1)
        self.session.add(user)
        self.session.commit()

        user.name = "Alice Green"
        self.repository.update(user)

        updated_user = self.session.query(User).filter_by(id=user.id).first()
        self.assertIsNotNone(updated_user)
        self.assertEqual(updated_user.name, "Alice Green")
        self.assertEqual(updated_user.email, "alice@example.com")

    def test_delete_user(self):
        # Test deleting an existing user
        user = User(name="Bob Johnson", email="bob@example.com", tenant_id=1)
        self.session.add(user)
        self.session.commit()

        self.repository.delete(user.id)

        deleted_user = self.session.query(User).filter_by(id=user.id).first()
        self.assertIsNone(deleted_user)

    def test_list_all_with_after(self):
        # Test listing all users with 'after' cursor
        # Insert at least 20 test users
        for i in range(20):
            user = User(name=f"Test User {i}", email=f"test{i}@example.com", tenant_id=1)
            self.session.add(user)
        self.session.commit()

        limit = 10
        after = 5

        result = self.repository.list_all(limit, after=after)

        self.assertEqual(len(result.data), limit)
        self.assertEqual(result.before, 6)
        self.assertEqual(result.after, 15)

    def test_list_all_with_before(self):
        # Test listing all users with 'before' cursor
        # Insert at least 20 test users
        for i in range(20):
            user = User(name=f"Test User {i}", email=f"test{i}@example.com", tenant_id=1)
            self.session.add(user)
        self.session.commit()

        limit = 10
        before = 15

        result = self.repository.list_all(limit, before=before)

        self.assertEqual(len(result.data), limit)
        self.assertEqual(result.before, 5)
        self.assertEqual(result.after, 14)


if __name__ == "__main__":
    unittest.main()
