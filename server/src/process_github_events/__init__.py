import json
import logging

from azure.functions import EventHubEvent
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..services.githubWebhookService import GithubWebhookService
import app_config


if app_config.DB_HOSTNAME:
    connection_string = f"postgresql://{app_config.DB_USERNAME}:{app_config.DB_PASSWORD}@{app_config.DB_HOSTNAME}:5432/{app_config.DB_NAME}"
else: connection_string = app_config.SQL_DATABASE_URI 

engine = create_engine(connection_string, echo=True)
Session = sessionmaker(bind=engine)

def lambda_handler(event, context):
    session = Session()
    githubService = GithubWebhookService(session)
    try:
        for event in event['Records']:
            bodyStr = event.get_body().decode('utf-8')
            logging.info('Python EventHub trigger processed an event: %s', bodyStr)
            body = json.loads(bodyStr)
            
            githubService.process_event(body["event_type"], body["delivery_id"], body["data"])
        session.commit()
    except Exception as e:
        session.rollback()
        logging.error('Error processing event: %s', e)
        raise
    finally:
        session.close()