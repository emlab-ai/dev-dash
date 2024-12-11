import os
from dotenv import load_dotenv

load_dotenv()


# Application (client) ID of app registration
CLIENT_ID = os.getenv("CLIENT_ID")
TENANT_ID = os.getenv("TENANT_ID", "common")
AUDIENCE = os.getenv("AUDIENCE")
ISSUER = os.getenv("ISSUER")

DEBUG = os.getenv("DEBUG", False)
DEBUG_SQL = os.getenv("DEBUG_SQL", False)


AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN", "dev-emlab.uk.auth0.com")

SQL_DATABASE_URI = os.getenv(
    "SQL_DATABASE_URI",
    "postgresql://postgres:bonaventura@localhost:5432/developer_dashboard",
)
EVENT_HUB_CONNECTION = os.getenv("EVENT_HUB_CONNECTION")

EVENT_HUB_GITHUB = os.getenv("EVENT_HUB_GITHUB", "githubevents")
EVENT_HUB_GITHUB_IMPORT = os.getenv("EVENT_HUB_GITHUB_IMPORT", "githubimport")

GITHUB_APP_ID = os.getenv("GITHUB_APP_ID", "861923")

KEY_VAULT_NAME = os.getenv("KEY_VAULT_NAME", "emlabaivault")

AWS_REGION = os.getenv("AWS_REGION", "eu-west-2")

IMPORT_STREAM_ARN = os.getenv(
    "IMPORT_STREAM_ARN", "arn:aws:kinesis:eu-west-2:834803522181:stream/github_import"
)
EVENTS_STREAM_ARN = os.getenv(
    "EVENTS_STREAM_ARN", "arn:aws:kinesis:eu-west-2:834803522181:stream/github_events"
)
AI_AGENT_STREAM_ARN = os.getenv(
    "AI_AGENT_STREAM_ARN",
    "arn:aws:kinesis:eu-west-2:834803522181:stream/ai_agent_events",
)

DB_SQL_SECRET_ARN = os.getenv(
    "DB_SQL_SECRET_ARN",
    "arn:aws:secretsmanager:eu-west-2:834803522181:secret:rds!db-a90903e6-e624-477c-b17e-66e7bd4dce76-b5ZhUM",
)
GEMINI_SECRET_ARN = os.getenv(
    "GEMINI_SECRET_ARN",
    "arn:aws:secretsmanager:eu-west-2:834803522181:secret:prod/gcp_gemini_key-UXAptV",
)

DB_HOST = os.getenv("DB_HOST", "emlab.cfugkypxw81e.eu-west-2.rds.amazonaws.com")
DB_NAME = os.getenv("DB_NAME", "EmlabDatabase")
DB_PORT = os.getenv("DB_PORT", "5432")
