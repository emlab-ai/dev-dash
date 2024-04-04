


from flask import abort, g, redirect, request
import app_config
from jose import jwt
from jose.exceptions import JWTError
import requests
from db.repository import TenantRepository, UserRepository
from db.model.user import User
from db.model.tenant import Tenant

def get_signing_keys(jwks_uri):
    response = requests.get(jwks_uri)
    jwks = response.json()
    return {key["kid"]: key for key in jwks["keys"]}

jwks = get_signing_keys('https://login.microsoftonline.com/common/discovery/keys')

def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header"""
    auth = request.headers.get("Authorization", None)
    if not auth:
        abort(401, description="Invalid or missing token.")

    parts = auth.split()

    if parts[0].lower() != "bearer":
        abort(401, description="Authorization header must start with Bearer.")
    elif len(parts) == 1:
        abort(401, description="Token not found.")
    elif len(parts) > 2:
        abort(401, description="Authorization header must be Bearer token.")

    token = parts[1]
    return token

def validate_token():
    token = get_token_auth_header()
    if not token:
        return False
    
    header = jwt.get_unverified_header(token)
    if header["kid"] not in jwks:
        abort(401, description="Invalid or missing token.")
    
    key = jwks[header["kid"]]

    decoded_token = jwt.decode(token, key, algorithms=['RS256'], audience=app_config.AUDIENCE, issuer=app_config.ISSUER)

    if not decoded_token:
        abort(401, description="Invalid or missing token.")

    tid = decoded_token["tid"]
    upn = decoded_token["upn"]

    g.tid = tid
    g.upn = upn

    tenantRepository = TenantRepository(g.session)
    userRepository = UserRepository(g.session)

    tenant = tenantRepository.get_by_oauth_tenant_id(tid)
    if not tenant:
        tenant = Tenant(name="", oauth_tenant_id=tid)
        tenantRepository.create(tenant)

    g.tenant = tenant

    user = userRepository.get_by_email(upn)
    if not user:
        user = User(
                    email=upn,
                    tenant_id=tenant.id,
                    name=decoded_token["name"])
        userRepository.create(user)

        

    g.user = user
    
    return True
