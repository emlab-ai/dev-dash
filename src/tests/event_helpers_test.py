import unittest
import json
import os
from db.model.githubOrg import GithubOrg
from db.model.pullRequest import PullRequest
from db.model.tenant import Tenant
from services.event_helpers import issue_comment_to_model, issue_to_model, pull_request_event_to_model, pull_request_review_comment_to_model, pull_request_review_to_model, repository_to_model


def get_test_file_path(file_name):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(current_dir, f'samples-payloads/{file_name}')
    return file_path

class TestEventHelpers(unittest.TestCase):
    def test_pull_request_review_comment_to_model(self):
        with open(get_test_file_path('pull_request_review_comment[created].json'), 'r') as f:
            event_data = json.load(f)
            data = event_data["payload"]
            tenant = Tenant(id=1, name="test", oauth_tenant_id="test")
            model = pull_request_review_comment_to_model(tenant, data)
            
            # Assertions
            self.assertEqual(model.id, data["comment"]["id"])
            self.assertEqual(model.tenant_id, tenant.id)
            self.assertEqual(model.org_id, data["organization"]["id"])
            self.assertEqual(model.node_id, data["comment"]["node_id"])
            self.assertEqual(model.is_resolved, False)
            self.assertEqual(model.is_outdated, False)
            self.assertEqual(model.author, data["comment"]["user"]["login"])
            self.assertEqual(model.author_id, data["comment"]["user"]["id"])
            self.assertEqual(model.reactions_count, data["comment"]["reactions"]["total_count"])
            self.assertEqual(model.created_at, data["comment"]["created_at"])
            self.assertEqual(model.updated_at, data["comment"]["updated_at"])
            self.assertEqual(model.pr_id, data["pull_request"]["id"])
            self.assertEqual(model.pr_number, data["pull_request"]["number"])
            self.assertEqual(model.repo_id, data["repository"]["id"])
            self.assertEqual(model.body, data["comment"]["body"])
            self.assertEqual(model.pr_review_id, data["comment"]["pull_request_review_id"])
            self.assertEqual(model.commit_id, data["comment"]["commit_id"])
            self.assertEqual(model.author_association, data["comment"]["author_association"])
            
    def test_pull_request_event_to_model(self):
        with open(get_test_file_path('pull_request[opened].json'), 'r') as f:
            event_data = json.load(f)
            data = event_data["payload"]
            tenant = Tenant(id=1, name="test", oauth_tenant_id="test")
            pull_request = pull_request_event_to_model(tenant, data)

            self.assertIsInstance(pull_request, PullRequest)
            self.assertEqual(pull_request.id, data["pull_request"]["id"])
            self.assertEqual(pull_request.tenant_id, tenant.id)
            self.assertEqual(pull_request.author, data["pull_request"]["user"]["login"])
            self.assertEqual(pull_request.author_id, data["pull_request"]["user"]["id"])
            self.assertEqual(pull_request.node_id, data["pull_request"]["node_id"])
            self.assertEqual(pull_request.number, data["pull_request"]["number"])
            self.assertEqual(pull_request.org_id, data["organization"]["id"])
            self.assertEqual(pull_request.repository_id, data["repository"]["id"])
            self.assertEqual(pull_request.closed_at, data["pull_request"]["closed_at"])
            self.assertEqual(pull_request.created_at, data["pull_request"]["created_at"])
            self.assertEqual(pull_request.changed_files, data["pull_request"]["changed_files"])
            self.assertEqual(pull_request.deletions, data["pull_request"]["deletions"])
            self.assertEqual(pull_request.additions, data["pull_request"]["additions"])
            self.assertEqual(pull_request.body, data["pull_request"]["body"])
            self.assertEqual(pull_request.title, data["pull_request"]["title"])
            self.assertEqual(pull_request.commits_count, data["pull_request"]["commits"])
            self.assertEqual(pull_request.review_threads_count,data["pull_request"]["review_comments"])
            self.assertEqual(pull_request.comments_count, data["pull_request"]["comments"])
            self.assertEqual(pull_request.url, data["pull_request"]["html_url"])
            self.assertEqual(pull_request.state, data["pull_request"]["state"])

    def test_pull_request_review_submitted_to_model(self):
        with open(get_test_file_path('pull_request_review[submitted].json'), 'r') as f:
            event_data = json.load(f)
            data = event_data["payload"]
            tenant = Tenant(id=1, name="test", oauth_tenant_id="test")
            model = pull_request_review_to_model(tenant, data)
            
            # Assertions
            self.assertEqual(model.id, data["review"]["id"])
            self.assertEqual(model.node_id, data["review"]["node_id"])
            self.assertEqual(model.tenant_id, tenant.id)
            self.assertEqual(model.author_id, data["review"]["user"]["id"])
            self.assertEqual(model.author, data["review"]["user"]["login"])
            self.assertEqual(model.state, data["review"]["state"])
            self.assertEqual(model.body, data["review"]["body"])
            self.assertEqual(model.repo_id, data["repository"]["id"])
            self.assertEqual(model.pr_id, data["pull_request"]["id"])
            self.assertEqual(model.pr_number, data["pull_request"]["number"])
            self.assertEqual(model.commit_id, data["review"]["commit_id"])
            self.assertEqual(model.org_id, data["organization"]["id"])
            
    def test_issue_comment_to_model(self):
        with open(get_test_file_path('issue_comment[created].json'), 'r') as f:
            event_data = json.load(f)
            data = event_data["payload"]
            tenant = Tenant(id=1, name="test", oauth_tenant_id="test")
            model = issue_comment_to_model(tenant, data)
            
            # Assertions
            self.assertEqual(model.id, data["comment"]["id"])
            self.assertEqual(model.node_id, data["comment"]["node_id"])
            self.assertEqual(model.tenant_id, tenant.id)
            self.assertEqual(model.author_id, data["comment"]["user"]["id"])
            self.assertEqual(model.author, data["comment"]["user"]["login"])
            self.assertEqual(model.body, data["comment"]["body"])
            self.assertEqual(model.created_at, data["comment"]["created_at"])
            self.assertEqual(model.updated_at, data["comment"]["updated_at"])
            self.assertEqual(model.author_association, data["comment"]["author_association"])
            self.assertEqual(model.repo_id, data["repository"]["id"])
            self.assertEqual(model.org_id, data["organization"]["id"])
            self.assertEqual(model.issue_id, data["issue"]["id"])
            self.assertEqual(model.issue_number, data["issue"]["number"])
            self.assertEqual(model.is_pr, "pull_request" in data["issue"])
           
    def test_repository_to_model(self):
        with open(get_test_file_path('installation_repositories[added].json'), 'r') as f:
            event_data = json.load(f)
            data = event_data["payload"]
            tenant = Tenant(id=1, name="test", oauth_tenant_id="test")
            org = GithubOrg(id=2, tenant_id=tenant.id, name="test", node_id="test")
            repo = data["repositories_added"][0]
            model = repository_to_model(tenant, org, repo)
            self.assertEqual(model.id, repo["id"])
            self.assertEqual(model.node_id, repo["node_id"])
            self.assertEqual(model.tenant_id, tenant.id)
            self.assertEqual(model.org_id, org.id)
            self.assertEqual(model.name, repo["name"])
            self.assertEqual(model.full_name, repo["full_name"])
            self.assertEqual(model.private, repo["private"])
            
    def test_issue_opened_to_model(self):
        with open(get_test_file_path('issues[opened].json'), 'r') as f:
            event_data = json.load(f)
            data = event_data["payload"]
            tenant = Tenant(id=1, name="test", oauth_tenant_id="test")
            model = issue_to_model(tenant, data)
            self.assertEqual(model.id, data["issue"]["id"])
            self.assertEqual(model.node_id, data["issue"]["node_id"])
            self.assertEqual(model.tenant_id, tenant.id)
            self.assertEqual(model.org_id, data["organization"]["id"])
            self.assertEqual(model.repo_id, data["repository"]["id"])
            self.assertEqual(model.number, data["issue"]["number"])
            self.assertEqual(model.title, data["issue"]["title"])
            self.assertEqual(model.user_id, data["issue"]["user"]["id"])
            self.assertEqual(model.user_login, data["issue"]["user"]["login"])
            self.assertEqual(model.state, data["issue"]["state"])
            self.assertEqual(model.locked, data["issue"]["locked"])
            self.assertEqual(model.comments, data["issue"]["comments"])
            self.assertEqual(model.created_at, data["issue"]["created_at"])
            self.assertEqual(model.updated_at, data["issue"]["updated_at"])
            self.assertEqual(model.closed_at, data["issue"]["closed_at"])
            self.assertEqual(model.author_association, data["issue"]["author_association"])
            self.assertEqual(model.body, data["issue"]["body"])
    
    def test_issue_assigned_to_model(self):
        # get current directory for this file
        
        with open(get_test_file_path('issues[assigned].json'), 'r') as f:
            event_data = json.load(f)
            data = event_data["payload"]
            tenant = Tenant(id=1, name="test", oauth_tenant_id="test")
            model = issue_to_model(tenant, data)
            self.assertEqual(model.id, data["issue"]["id"])
            self.assertEqual(model.node_id, data["issue"]["node_id"])
            self.assertEqual(model.tenant_id, tenant.id)
            self.assertEqual(model.org_id, data["organization"]["id"])
            self.assertEqual(model.repo_id, data["repository"]["id"])
            self.assertEqual(model.number, data["issue"]["number"])
            self.assertEqual(model.title, data["issue"]["title"])
            self.assertEqual(model.user_id, data["issue"]["user"]["id"])
            self.assertEqual(model.user_login, data["issue"]["user"]["login"])
            self.assertEqual(model.state, data["issue"]["state"])
            self.assertEqual(model.locked, data["issue"]["locked"])
            self.assertEqual(model.comments, data["issue"]["comments"])
            self.assertEqual(model.created_at, data["issue"]["created_at"])
            self.assertEqual(model.updated_at, data["issue"]["updated_at"])
            self.assertEqual(model.closed_at, data["issue"]["closed_at"])
            self.assertEqual(model.author_association, data["issue"]["author_association"])
            self.assertEqual(model.body, data["issue"]["body"])
        
        
if __name__ == '__main__':
    unittest.main()