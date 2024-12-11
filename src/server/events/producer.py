import boto3
import json

kinesis_client = boto3.client("kinesis")


def publish_to_kinesis(stream_arn, partition_key, message):
    # Convert the message to a JSON string and encode it to bytes
    message_bytes = json.dumps(message).encode("utf-8")

    # Put the record to the Kinesis stream
    response = kinesis_client.put_record(
        # StreamName=stream_name,
        Data=message_bytes,
        PartitionKey=partition_key,
        StreamARN=stream_arn,
    )
    return response
