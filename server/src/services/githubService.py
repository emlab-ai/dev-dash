import json
from events.producer import producer
from azure.eventhub import EventData

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
    
    def process_issue_comment(self, data):
        pass

    def process_pull_request(self, data):
        pass

    def process_pull_request_review_comment(self, data):
        pass

    def process_pull_request_review(self, data):
        pass    

