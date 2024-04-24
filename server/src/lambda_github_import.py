import json
import logging
import base64
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from services.githubImportService import GithubImportService
import app_config

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    logger.info("Started import handler")
    
    try:
        
        if app_config.DB_HOSTNAME:
            connection_string = f"postgresql://{app_config.DB_USERNAME}:{app_config.DB_PASSWORD}@{app_config.DB_HOSTNAME}:5432/{app_config.DB_NAME}"
        else: connection_string = app_config.SQL_DATABASE_URI 

        engine = create_engine(connection_string, echo=True)
        Session = sessionmaker(bind=engine)

        session = Session()
        githubService = GithubImportService(session)    
        
        for event in event['Records']:
            data = event['kinesis']['data']
            bodyStr = base64.b64decode(data).decode('utf-8')
            logger.info('Processed an event: %s', bodyStr)
            body = json.loads(bodyStr)
            
            githubService.process_event(body)
            
        session.commit()
    except Exception as e:
        print('Error processing event: %s', e)
        logger.error('Error processing event: %s', e)
        session.rollback()
        # raise
    finally:
        session.close()
    logger.info("Completed import handler")
    # Your Lambda function logic
    return {
        'statusCode': 200,
        'body': 'ok'
    }
