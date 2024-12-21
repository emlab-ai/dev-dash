import datetime
import boto3
import app_config

# Initialize DynamoDB resource
dynamodb = boto3.resource("dynamodb", region_name=app_config.AWS_REGION)

# Select the DynamoDB table
table = dynamodb.Table("emlab_githubevents")


class GithubEventsRepository:
    def __init__(self):
        pass

    def insert(
        self,
        tenant_id: int,
        event_type: str,
        delivery_id: str,
        received_at: datetime.datetime,
        data,
        failed=False,
        error_text: str = None,
    ):
        response = table.put_item(
            Item={
                "tenant_id": str(tenant_id),
                "event_type": event_type,
                "received_at": str(received_at),
                "delivery_id": delivery_id,
                "data": data,
                "failed": failed,
                "error_text": error_text,
            }
        )
        return response

    def get(self, tenant_id: int, delivery_id: str):
        response = table.get_item(
            Key={"tenant_id": str(tenant_id), "delivery_id": delivery_id}
        )
        return response["Item"]
