import json
import logging
import base64
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.aiAgentService import AiAgentService
import app_config
from app_sql import get_sql_connection_string
from app_logger import logger
import asyncio

def handler(event, context):
    logger.info('Started ai agent handler')
    try:
        connection_string = get_sql_connection_string()

        engine = create_engine(connection_string, echo=app_config.DEBUG_SQL)
        Session = sessionmaker(bind=engine)
        session = Session()
        aiAgentService = AiAgentService(session)
        
        for event in event['Records']:
            data = event['kinesis']['data']
            bodyStr = base64.b64decode(data).decode('utf-8')
            logging.info('Trigger processed an event: %s', bodyStr)
            body = json.loads(bodyStr)
            
            asyncio.run(aiAgentService.process_event_async(body))
        session.commit()
    except Exception as e:
        session.rollback()
        logging.error('Error processing event: %s', e)
        # raise
    finally:
        session.close()
    
    logger.info('Ended ai agent handler')