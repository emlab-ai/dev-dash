from flask import g
from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging
import app_config
from flask import has_app_context


def setup_app_insights():
    if not app_config.APP_INSIGHTS_CONNECTION_STRING:
        return

    # Configure Azure log handler
    handler = AzureLogHandler(connection_string=app_config.APP_INSIGHTS_CONNECTION_STRING)
    
    # You can also add custom properties
    handler.add_telemetry_processor(add_custom_properties)

    # Set the logging level and add handler
    logging.basicConfig(level=logging.ERROR)
    logging.getLogger('').addHandler(handler)

def add_custom_properties(envelope):
    envelope.tags['ai.cloud.role'] = 'emlab.ai Web App'  
    if has_app_context():
        envelope.tags['trace_id'] = g.trace_id
