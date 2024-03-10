import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.repository import TeamRepository
from db.model import Team

class TeamRepositoryTests(unittest.TestCase):
    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.engine = create_engine('sqlite:///:memory:')
        Team.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()
        self.repository = TeamRepository(self.session)

    def tearDown(self):
        # Close the database connection after each test
        self.session.close()
        self.engine.dispose()

    def test_create_team(self):
        # Test creating a new team
        self.repository.create_team(Team(name='Team A', tribeId=1))

        team = self.session.query(Team).filter_by(name='Team A').first()

        self.assertIsNotNone(team)
        self.assertEqual(team.name, 'Team A')

    def test_get_team(self):
        # Test retrieving an existing team
        team = self.repository.create_team(Team(name='Team B', tribeId=1))

        retrieved_team = self.repository.get_team(team.id)
        self.assertIsNotNone(retrieved_team)
        self.assertEqual(retrieved_team.name, 'Team B')

    def test_update_team(self):
        # Test updating an existing team
        team = self.repository.create_team(Team(name='Team C', tribeId=1))

        self.repository.update_team(team.id, 'Team D')

        updated_team = self.session.query(Team).filter_by(id=team.id).first()
        self.assertIsNotNone(updated_team)
        self.assertEqual(updated_team.name, 'Team D')

    def test_delete_team(self):
        # Test deleting an existing team
        team = Team(name='Team E', tribeId=1)
        self.session.add(team)
        self.session.commit()

        self.repository.delete_team(team.id)

        deleted_team = self.session.query(Team).filter_by(id=team.id).first()
        self.assertIsNone(deleted_team)

if __name__ == '__main__':
    unittest.main()