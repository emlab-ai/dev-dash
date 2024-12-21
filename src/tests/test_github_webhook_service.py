import asyncio
import json
import os
import unittest
from db.model.githubInstallation import GithubInstallation
from db.model.githubOrg import GithubOrg
from db.model.githubRepo import GithubRepo
from db.repository.asyncRepository import AsyncRepository
from services.githubWebhookService import GithubWebhookService
from tests.baseIntegrationTest import BaseIntegrationTest


def get_test_file_path(file_name):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(current_dir, f"samples-payloads/{file_name}")
    return file_path


class GithubWebhookServiceTests(BaseIntegrationTest):
    async def test_pull_request_received_async(self):
        service = GithubWebhookService(self.session)

        instRepo = AsyncRepository(GithubInstallation, self.session)
        await instRepo.create_async(
            GithubInstallation(
                installation_token="token",
                installation_id=49031331,
                tenant_id=self.tenant.id,
            )
        )

        orgRepo = AsyncRepository(GithubOrg, self.session)
        await orgRepo.create_async(GithubOrg(id=162922992, tenant_id=self.tenant.id, name="org"))

        repoRepo = AsyncRepository(GithubRepo, self.session)
        await repoRepo.create_async(
            GithubRepo(
                id=777192323,
                org_id=162922992,
                tenant_id=self.tenant.id,
                name="repo",
                full_name="org/repo",
                node_id="node_id",
            )
        )

        with open(get_test_file_path("pull_request[opened].json"), "r") as f:
            event_data = json.load(f)

            await service.process_event_async(
                "pull_request", "1", event_data["payload"]
            )


if __name__ == "__main__":
    asyncio.run(unittest.main())
