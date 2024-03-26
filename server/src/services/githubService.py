import json
from events.producer import producer
from azure.eventhub import EventData

class GithubService:
    def record_event(self, event, deliveryId, installationTargetType, installationTargetId, data):
        try:
            # Create a batch.
            with producer:
                event_batch = producer.create_batch()

                body = {
                    "data": data,
                    "event_type": event,
                    "delivery_id": deliveryId,
                    "installation_target_type": installationTargetType,
                    "installation_target_id": installationTargetId 
                }
                
                data_bytes = json.dumps(body).encode('utf-8')

                # Wrap the data in an EventData object
                event_data = EventData(body=data_bytes)

                # Adding custom properties (optional)
                event_data.properties = {
                    "event_type": event,
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