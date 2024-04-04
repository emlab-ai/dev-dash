import json
import logging

from app_insights import setup_app_insights
from azure.functions import EventHubEvent
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from services.githubImportService import GithubImportService
import app_config

connection_string = app_config.SQL_DATABASE_URI 
engine = create_engine(connection_string, echo=True)
Session = sessionmaker(bind=engine)

setup_app_insights()

def main(events: List[EventHubEvent]):
    session = Session()
    githubService = GithubImportService(session)
    
    try:
        for event in events:
            bodyStr = event.get_body().decode('utf-8')
            logging.info('Python EventHub trigger processed an event: %s', bodyStr)
            body = json.loads(bodyStr)
            
            githubService.process_event(body)
        session.commit()
    except Exception as e:
        logging.error('Error processing event: %s', e)
        session.rollback()
        raise
    finally:
        session.close()
