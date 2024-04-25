import app_config
import boto3
import json

# connection_str = app_config.EVENT_HUB_CONNECTION

# github_events_producer = EventHubProducerClient.from_connection_string(conn_str=connection_str, eventhub_name=app_config.EVENT_HUB_GITHUB)
# github_import_producer = EventHubProducerClient.from_connection_string(conn_str=connection_str, eventhub_name=app_config.EVENT_HUB_GITHUB_IMPORT)

kinesis_client = boto3.client('kinesis')

def publish_to_kinesis(stream_arn, partition_key, message):
    # Convert the message to a JSON string and encode it to bytes
    message_bytes = json.dumps(message).encode('utf-8')
    
    # Put the record to the Kinesis stream
    response = kinesis_client.put_record(
        # StreamName=stream_name,        
        Data=message_bytes,
        PartitionKey=partition_key,
        StreamARN=stream_arn
    )
    return response
