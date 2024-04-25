import logging
from pythonjsonlogger import jsonlogger


logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)

# Configure logger
logger = logging.getLogger('app')
logger.setLevel(logging.DEBUG)

# Create a log handler (console handler for example)
log_handler = logging.StreamHandler()
log_handler.setLevel(logging.DEBUG)

# Use JSON formatter
formatter = jsonlogger.JsonFormatter()
log_handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(log_handler)
logging.getLogger('sqlalchemy.engine').addHandler(log_handler)