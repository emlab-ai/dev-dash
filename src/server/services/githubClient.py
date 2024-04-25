import datetime
import json
from types import SimpleNamespace
from aws.secret import get_aws_secret
import jwt
import time
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import app_config
import requests
from cachetools import cached, TTLCache
from utils import log_exceptions

import base64

# global variables
private_key: str = None
token_generated_time:datetime = None
token: str = None
access_token_cache = TTLCache(maxsize=10000, ttl=3000)

@log_exceptions()
def setup_github_app():
    global app_id
    global private_key
    
    secret_name = "prod/githubcert"

    certStr = get_aws_secret(secret_name, app_config.AWS_REGION)

    app_id = app_config.GITHUB_APP_ID

    private_key = serialization.load_pem_private_key(
        certStr.encode(),
        password=None,
        backend=default_backend()
    )

def get_app_access_token() -> str:
    global token_generated_time
    global token

    if not private_key:
        setup_github_app()

    if token and  token_generated_time and (time.time() - token_generated_time) < 540:  
        return token      

    time_now = int(time.time())
    payload = {
        'iat': time_now,
        'exp': time_now + (10 * 60),
        'iss': app_id
    }

    token = jwt.encode(
        payload,
        private_key,
        algorithm='RS256'
    )
    token_generated_time = time_now
    return token



@cached(access_token_cache)
def get_installation_access_token(installation_id:str) -> str: 
    token = get_app_access_token()

    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json'
    }

    response = requests.post(
        f'https://api.github.com/app/installations/{installation_id}/access_tokens',
        headers=headers
    )

    access_token = response.json()['token']

    return access_token

@log_exceptions(log_args=True)
def github_gql_query(query:str, installation_id:str) -> dict:
    access_token = get_installation_access_token(installation_id)

    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github+json'
    }

    response = requests.post(
        'https://api.github.com/graphql',
        json={'query': query},
        headers=headers
    )

    if response.status_code != 200:
        raise Exception(f'Error fetching data from GitHub: {response.text}')
    
    result = response.json(object_hook=lambda d: SimpleNamespace(**d) if isinstance(d, dict) else d)

    if hasattr(result, "errors"):
        print(result.errors)
        raise Exception(f"Error fetching data from GitHub, {result.errors}")
    if not hasattr(result, "data"):
        raise Exception("No data found in GitHub response")
    
    return result

def get_org_repos(installation_id, org_name, cursor=None):
    afterFilter = f', after: "{cursor}"' if cursor else ''
    query = f"""
    {{
        organization(login: "{org_name}") {{
            repositories(first: 100{afterFilter}) {{
                totalCount
                pageInfo {{
                    hasNextPage
                    endCursor
                }}
                nodes {{
                    name
                    url
                    id
                    databaseId
                    isPrivate
                    isArchived
                    isDisabled
                    isLocked
                    nameWithOwner
                }}
            }}
        }}
    }}"""
    return github_gql_query(query, installation_id)
   
    
def get_repo_pull_requests(installation_id, repo_full_name, cursor=None):
    afterFilter = f', after: {cursor}' if cursor else ''
    [owner, name] = repo_full_name.split('/')
    query = f"""
    {{
      repository(owner: "{owner}", name: "{name}") {{
        databaseId
        pullRequests(first: 100{afterFilter}) {{
          totalCount
          pageInfo {{
            hasNextPage
            endCursor
          }}
          nodes {{
            createdAt
            id
            number
            closedAt
            changedFiles
            deletions
            additions
            bodyText
            title
            url
            databaseId  
            state
            author {{
                login
              	... on User {{
                    id
                    databaseId
                }}
            }}
            commits(first:1) {{
                totalCount
                nodes {{
                    commit  {{
                        committedDate
                        message
                    }}
                }}
            }}
            
            repository {{
                name
                url
            }}
            reviewThreads(first: 15) {{
                totalCount
                nodes {{
                    isResolved
                    id
                    isOutdated
                    comments(first: 20) {{
                        nodes {{
                            createdAt
                            author {{
                                login
                            }}
                            body
                            reactions {{
                                totalCount
                            }}
                        }}
                        pageInfo {{
                            hasNextPage
                            endCursor
                        }}
                    }}
                }}
            }}
            reviews(first: 10) {{
                nodes {{
                state
                createdAt
                publishedAt
                author {{
                    login
                }}
                bodyText
                }}
            }}
            comments (first: 20) {{
                totalCount
                edges {{
                    node {{
                        createdAt
                        author {{
                            login
                        }}
                        reactions {{
                            totalCount
                        }}
                        bodyText              
                        id
                    }}
                }}
            }}
          
          }}
        }}
      }}
    }}
    """
    return github_gql_query(query, installation_id)