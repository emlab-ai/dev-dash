import json
import logging

from app_insights import setup_app_insights
from azure.functions import EventHubEvent
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..services.githubWebhookService import GithubWebhookService
import app_config


connection_string = app_config.SQL_DATABASE_URI 
engine = create_engine(connection_string, echo=True)
Session = sessionmaker(bind=engine)

setup_app_insights()

def main(events: List[EventHubEvent]):
    session = Session()
    githubService = GithubWebhookService(session)
    try:
        for event in events:        
            bodyStr = event.get_body().decode('utf-8')
            logging.info('Python EventHub trigger processed an event: %s', bodyStr)
            body = json.loads(bodyStr)
            
            githubService.process_event(body["event_type"], body["delivery_id"], body["installation_target_type"], body["installation_target_id"], body["data"])
        session.commit()
    except Exception as e:
        session.rollback()
        logging.error('Error processing event: %s', e)
        raise
    finally:
        session.close()