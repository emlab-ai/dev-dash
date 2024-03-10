import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.repository import TribeRepository
from db.model import Tribe

class TribeRepositoryTests(unittest.TestCase):
    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.engine = create_engine('sqlite:///:memory:')
        Tribe.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()
        self.repository = TribeRepository(self.engine)

    def tearDown(self):
        # Close the database connection after each test
        self.session.close()
        self.engine.dispose()

    def test_add_tribe(self):
        # Test adding a new tribe
        tribe = Tribe(name='Test Tribe')
        self.repository.add_tribe(tribe)

        added_tribe = self.session.query(Tribe).filter_by(name='Test Tribe').first()

        self.assertIsNotNone(added_tribe)
        self.assertEqual(added_tribe.name, 'Test Tribe')

    def test_remove_tribe(self):
        # Test removing an existing tribe
        tribe = Tribe(name='Test Tribe')
        self.session.add(tribe)
        self.session.commit()

        self.repository.remove_tribe_by_id(tribe.id)

        removed_tribe = self.session.query(Tribe).filter_by(name='Test Tribe').first()
        self.assertIsNone(removed_tribe)

    def test_get_tribes(self):
        # Test retrieving all tribes
        tribe1 = Tribe(name='Tribe 1')
        tribe2 = Tribe(name='Tribe 2')
        self.session.add_all([tribe1, tribe2])
        self.session.commit()

        tribes = self.repository.get_tribes()

        self.assertEqual(len(tribes), 2)
    

    def test_get_tribe_by_id(self):
        # Test retrieving a tribe by ID
        tribe = Tribe(name='Test Tribe')
        self.session.add(tribe)
        self.session.commit()

        retrieved_tribe = self.repository.get_tribe_by_id(tribe.id)
        self.assertIsNotNone(retrieved_tribe)
        self.assertEqual(retrieved_tribe.name, 'Test Tribe')

    def test_get_tribes_by_name(self):
        # Test retrieving tribes by name
        tribe1 = Tribe(name='Test Tribe')
        tribe2 = Tribe(name='Test Tribe')
        self.session.add_all([tribe1, tribe2])
        self.session.commit()

        matching_tribes = self.repository.get_tribes_by_name('Test Tribe')

        self.assertEqual(len(matching_tribes), 2)
        # self.assertIn(tribe1, matching_tribes)
        # self.assertIn(tribe2, matching_tribes)

if __name__ == '__main__':
    unittest.main()