import asyncio
import unittest

from sqlalchemy import delete
from tests.baseIntegrationTest import BaseIntegrationTest
from db.model import Team
from db.repository import TeamRepository


class TeamRepositoryTests(BaseIntegrationTest):

    async def test_create_async(self):
        repository = TeamRepository(self.session)
        # Test creating a new team
        await repository.create_async(Team(name="Team A", tenant_id=self.tenant.id))

        team = await repository.find_one_async(Team.name == "Team A")
        self.assertIsNotNone(team)
        self.assertEqual(team.name, "Team A")

    async def test_get_team(self):
        repository = TeamRepository(self.session)
        # Test retrieving an existing team
        team = await repository.create_async(Team(name="Team B", tenant_id=1))

        retrieved_team = await repository.get_async(team.id, tenant_id=self.tenant.id)
        self.assertIsNotNone(retrieved_team)
        self.assertEqual(retrieved_team.name, "Team B")

    async def test_update_async(self):
        repository = TeamRepository(self.session)
        # Test updating an existing team
        team = await repository.create_async(Team(name="Team C", tenant_id=1))

        target_value = "Team D"
        team.name = target_value

        await repository.update_async(team)

        updated_team = await repository.find_one_async(Team.name == target_value)
        self.assertIsNotNone(updated_team)

    async def test_delete_team(self):
        repository = TeamRepository(self.session)
        # Test deleting an existing team
        team = Team(name="Team E", tenant_id=self.tenant.id)
        await repository.create_async(team)

        await repository.delete_async(item_id=team.id, tenant_id=self.tenant.id)

        deleted_team = await repository.find_one_async(Team.id == team.id)

        self.assertIsNone(deleted_team)

    async def test_find_all_teams(self):
        repository = TeamRepository(self.session)
        await self.session.execute(delete(Team))
        await self.session.commit()

        # Test finding all teams
        for i in range(20):
            team = Team(name=f"Team {i}", tenant_id=self.tenant.id)
            await repository.create_async(team)

        result = await repository.list_all_async(tenant_id=1, limit=5)
        self.assertEqual(len(result.data), 5)
        self.assertIsNotNone(result.after)
        self.assertIsNone(result.before)

        result = await repository.list_all_async(tenant_id=1, limit=12, after=result.after)
        self.assertEqual(len(result.data), 12)
        self.assertIsNotNone(result.after)
        self.assertIsNotNone(result.before)

        result = await repository.list_all_async(tenant_id=1, limit=12, after=result.after)
        self.assertEqual(len(result.data), 3)
        self.assertIsNone(result.after)
        self.assertIsNotNone(result.before)


if __name__ == "__main__":
    asyncio.run(unittest.main())
