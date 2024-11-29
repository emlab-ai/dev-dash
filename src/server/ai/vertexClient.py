import json

from cachetools import TTLCache, cached
import app_config
from aws.secret import get_aws_secret
import vertexai
from vertexai.generative_models import GenerativeModel
from google.oauth2 import service_account

from utils import log_exceptions
from app_logger import logger
key_info: str = None



access_token_cache = TTLCache(maxsize=10000, ttl=3000)

@log_exceptions()
def setup_vertex_client():
    credentials = get_gcp_credentials()
    logger.info("Credentials loaded")
    vertexai.init(project="firefly-dev-2018", credentials=credentials)

@cached(access_token_cache)
def get_gcp_credentials() :
    global key_info
    logger.info("Setting up Vertex AI client")
    if key_info == None:
        secret_name = "prod/gcp_gemini_key"
        certStr = get_aws_secret(secret_name, app_config.AWS_REGION)
        logger.info("Secret retrieved")
        key_info = json.loads(certStr)

    credentials = service_account.Credentials.from_service_account_info(key_info)
    logger.info("Credentials loaded")
    return credentials