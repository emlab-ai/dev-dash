from azure.eventhub import EventHubProducerClient, EventData
import app_config

connection_str = app_config.EVENT_HUB_CONNECTION
eventhub_name = app_config.EVENT_HUB_GITHUB

producer = EventHubProducerClient.from_connection_string(conn_str=connection_str, eventhub_name=eventhub_name)
