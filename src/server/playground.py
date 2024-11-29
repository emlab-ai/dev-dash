       
from sqlalchemy import create_engine
import app_config
from app_sql import get_sql_connection_string
from services.aiAgentService import AiAgentService
from sqlalchemy.orm import sessionmaker
import asyncio


if __name__ == '__main__':
    connection_string = get_sql_connection_string()

    engine = create_engine(connection_string, echo=app_config.DEBUG_SQL)
    Session = sessionmaker(bind=engine)
    session = Session()
    aiService = AiAgentService(session)
    
    asyncio.run(aiService._perform_pr_review_async(1, 49639210, {"pr_id": 2200763035}))