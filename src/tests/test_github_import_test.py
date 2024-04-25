import os
from types import SimpleNamespace
import unittest
import json
from db.model.githubOrg import GithubOrg
from db.model.tenant import Tenant
from db.repository import UserRepository
from db.model import User
from services.githubImportService import pull_request_response_to_model


def get_test_file_path(file_name):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(current_dir, f'gql-data/{file_name}')
    return file_path

class UserRepositoryTests(unittest.TestCase):
    def test_pull_request_review_comment_to_model(self):
        with open(get_test_file_path('pull_requests.json'), 'r') as f:
            result = json.load(f, object_hook=lambda d: SimpleNamespace(**d) if isinstance(d, dict) else d)
            
            org = GithubOrg(
                id = 2,
                name = "org",
                tenant_id = 1,
            )   
            
            tenant = Tenant(
                id = 1,
                name = 'test',
                oauth_tenant_id = 'test'
            )
            
            prs = pull_request_response_to_model(tenant, org, result)
            self.assertEqual(len(prs), 8)   
            
if __name__ == '__main__':
    unittest.main()