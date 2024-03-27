from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging
import app_config

def setup_app_insights(app):
    app.config['APP_INSIGHTS_KEY'] = app_config.APP_INSIGHTS_KEY

    if not app or not app.config['APP_INSIGHTS_KEY']:
        return

    # Configure Azure log handler
    handler = AzureLogHandler(connection_string=app_config.APP_INSIGHTS_CONNECTION_STRING)
    
    # You can also add custom properties
    handler.add_telemetry_processor(add_custom_properties)

    # Set the logging level and add handler
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('').addHandler(handler)

def add_custom_properties(envelope):
    # Add custom properties to every log message
    envelope.tags['ai.cloud.role'] = 'emlab.ai Web App'  # Example role name
    # envelope.data.baseData.properties['customProperty'] = 'customValue'  # Example custom property
