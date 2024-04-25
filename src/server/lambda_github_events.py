import json
import logging
import base64
from azure.functions import EventHubEvent
from typing import List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .services.githubWebhookService import GithubWebhookService
import app_config
from app_sql import get_sql_connection_string
from app_logger import logger

def handler(event, context):
    logger.info('Started import handler')
    try:
        connection_string = get_sql_connection_string()

        engine = create_engine(connection_string, echo=app_config.DEBUG_SQL)
        Session = sessionmaker(bind=engine)
        session = Session()
        githubService = GithubWebhookService(session)
        
        for event in event['Records']:
            data = event['kinesis']['data']
            bodyStr = base64.b64decode(data).decode('utf-8')
            logging.info('Trigger processed an event: %s', bodyStr)
            body = json.loads(bodyStr)
            
            githubService.process_event(body["event_type"], body["delivery_id"], body["data"])
        session.commit()
    except Exception as e:
        session.rollback()
        logging.error('Error processing event: %s', e)
        # raise
    finally:
        session.close()
    
    logger.info('Ended import handler')