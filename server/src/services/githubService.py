import json
from events.producer import producer
from azure.eventhub import EventData

from db.model.pullRequest import PullRequest
from services.githubClient import github_gql_query

class GithubService:
    def record_event(self, event_type, deliveryId, installationTargetType, installationTargetId, data):
        try:
            # Create a batch.
            with producer:
                event_batch = producer.create_batch()

                body = {
                    "data": data,
                    "event_type": event_type,
                    "delivery_id": deliveryId,
                    "installation_target_type": installationTargetType,
                    "installation_target_id": installationTargetId 
                }
                
                data_bytes = json.dumps(body).encode('utf-8')

                # Wrap the data in an EventData object
                event_data = EventData(body=data_bytes)

                # Adding custom properties (optional)
                event_data.properties = {
                    "event_type": event_type,
                    "delivery_id": deliveryId,
                    "installation_target_type": installationTargetType,
                    "installation_target_id": installationTargetId                
                }
                # Add events to the batch.
                event_batch.add(event_data)

                producer.send_batch(event_batch)
        except Exception as e:
            print(e)
            return False
        
    def process_event(self, event_type, deliveryId, installationTargetType, installationTargetId, data):

        # TODO: record event in database, and check if it was already processed

        if event_type == "issue_comment":
            self.process_issue_comment(deliveryId, installationTargetType, installationTargetId, data)
        elif event_type == "pull_request":
            self.process_pull_request(deliveryId, installationTargetType, installationTargetId, data)
        elif event_type == "pull_request_review_comment":
            self.process_pull_request_review_comment(deliveryId, installationTargetType, installationTargetId, data)
        elif event_type == "pull_request_review":
            self.process_pull_request_review(deliveryId, installationTargetType, installationTargetId, data)

        # TODO: record delivery_id 

        return True
    
    def process_issue_comment(self, deliveryId, installationTargetType, installationTargetId, data):

        pass

    def process_pull_request(self, deliveryId, installationTargetType, installationTargetId, data):
        payload = data["payload"]
        action = payload["action"]
        pull_request = payload["pull_request"]
        installation_id = data["installation"]["id"]
        prId = pull_request["node_id"]

        # TODO: find org from installation_id

        query = f"""
            query {{
            node(id: "{prId}") {{
                ... on PullRequest {{
                id
                createdAt
                commits(first:1) {{
                    totalCount
                    nodes {{
                        commit  {{
                            committedDate
                            message
                        }}
                    }}
                    }}
                }}                
                }}
            }}
        """

        result = github_gql_query(query, installation_id)
        if "errors" in result:
            print(result["errors"])
            raise Exception("Error fetching data from GitHub")
        if not "data" in result:
            raise Exception("No data found in GitHub response")

        firstCommitDate = result["data"]["node"]["commits"]["nodes"][0]["commit"]["committedDate"]
        firstCommitMessage = result["data"]["node"]["commits"]["nodes"][0]["commit"]["committedMessage"]

        preRecord = PullRequest(
            tenant_id = tenant_id,
            author = pull_request["user"]["login"],
            authorId = pull_request["user"]["id"], # TODO
            prId = pull_request["node_id"],
            number = pull_request["number"],
            closedAt = pull_request["closed_at"],
            createdAt = pull_request["created_at"],
            changedFiles = pull_request["changed_files"],
            deletions = pull_request["deletions"],
            additions = pull_request["additions"],
            bodyText = pull_request["body"],
            title = pull_request["title"],
            commitsCount = pull_request["commits"],
            firstCommitMessage = firstCommitMessage,
            firstCommitDate = firstCommitDate,
            repositoryName = data["repository"]["name"],
            repositoryUrl = data["repository"]["html_url"],
            reviewThreadsCount = pull_request["review_comments"],
            commentsCount = pull_request["comments"],
            reactionsCount = pull_request["reactions"]["total_count"],
            url = pull_request["html_url"]
        )
        

    def process_pull_request_review_comment(self, deliveryId, installationTargetType, installationTargetId, data):
        pass

    def process_pull_request_review(self, deliveryId, installationTargetType, installationTargetId, data):
        pass    

