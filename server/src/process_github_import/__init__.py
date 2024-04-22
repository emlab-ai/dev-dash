import json
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from services.githubImportService import GithubImportService
import app_config

if app_config.DB_HOSTNAME:
    connection_string = f"postgresql://{app_config.DB_USERNAME}:{app_config.DB_PASSWORD}@{app_config.DB_HOSTNAME}:5432/{app_config.DB_NAME}"
else: connection_string = app_config.SQL_DATABASE_URI 

engine = create_engine(connection_string, echo=True)
Session = sessionmaker(bind=engine)

def lambda_handler(event, context):
    session = Session()
    githubService = GithubImportService(session)
    
    try:
        for event in event['Records']:
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
