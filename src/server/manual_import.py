import json
import base64
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.githubImportService import GithubImportService
from app_sql import get_sql_connection_string
from app_logger import logger
from db.repository.repository import Repository
from db.model.githubOrg import GithubOrg

org_id = 86411290

logger.info("Started import handler")
connection_string = get_sql_connection_string()
engine = create_engine(connection_string, echo=False)
Session = sessionmaker(bind=engine)

session = Session()
githubService = GithubImportService(session, True)    

orgRepository = Repository(GithubOrg, session)
org = orgRepository.get(org_id)
    
githubService.create_import_request(org.tenant, org)
    
session.commit()
