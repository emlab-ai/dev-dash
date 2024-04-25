import os
from dotenv import load_dotenv
load_dotenv()


# Application (client) ID of app registration
CLIENT_ID = os.getenv("CLIENT_ID")
TENANT_ID = os.getenv('TENANT_ID', 'common')
AUDIENCE = os.getenv('AUDIENCE')
ISSUER = os.getenv('ISSUER')

DEBUG = os.getenv("DEBUG", False)

# AUTHORITY = "https://login.microsoftonline.com/common"  # For multi-tenant app
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"

REDIRECT_PATH = "/getAToken"  # Used for forming an absolute URL to your redirect URI.
# The absolute URL must match the redirect URI you set
# in the app's registration in the Azure portal.

# You can find more Microsoft Graph API endpoints from Graph Explorer
# https://developer.microsoft.com/en-us/graph/graph-explorer
ENDPOINT = 'https://graph.microsoft.com/v1.0/users'  # This resource requires no admin consent

# You can find the proper permission names from this document
# https://docs.microsoft.com/en-us/graph/permissions-reference
SCOPE = ["User.ReadBasic.All"]

# Tells the Flask-session extension to store sessions in the filesystem
SESSION_TYPE = "filesystem"
# Using the file system will not work in most production systems,
# it's better to use a database-backed session store instead.

SQL_DATABASE_URI = os.getenv('SQL_DATABASE_URI', 'postgresql://postgres:bonaventura@localhost:5432/developer_dashboard') 
EVENT_HUB_CONNECTION = os.getenv('EVENT_HUB_CONNECTION')

EVENT_HUB_GITHUB = os.getenv('EVENT_HUB_GITHUB', "githubevents")
EVENT_HUB_GITHUB_IMPORT = os.getenv('EVENT_HUB_GITHUB_IMPORT', "githubimport")

GITHUB_APP_ID = os.getenv('GITHUB_APP_ID', '861923')

KEY_VAULT_NAME = os.getenv('KEY_VAULT_NAME', 'emlabaivault')

AWS_REGION = os.getenv('AWS_REGION', 'eu-west-2')

IMPORT_STREAM_ARN=os.getenv('IMPORT_STREAM_ARN', "arn:aws:kinesis:eu-west-2:834803522181:stream/github_import")
EVENTS_STREAM_ARN=os.getenv('EVENTS_STREAM_ARN', "arn:aws:kinesis:eu-west-2:834803522181:stream/github_events")

DB_SQL_SECRET_ARN = os.getenv('DB_SQL_SECRET_ARN', 'arn:aws:secretsmanager:eu-west-2:834803522181:secret:EmlabCdkStackEmlabDatabaseS-D5QySQGBugFQ-erMizP')