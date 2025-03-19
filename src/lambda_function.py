import json
import jwt
import boto3
import requests
from jose import jwt as jose_jwt, jwk
from jose.utils import base64url_decode
import time
from jwt import ExpiredSignatureError, InvalidTokenError
import os

ADMIN_ROUTES = {("POST", "products"), ("PUT", "products"), ("DELETE", "products"), 
                ("POST", "customers"), ("GET", "customers"), ("GET", "orders")}

def lambda_handler(event, context):
    http_method, resource = get_resource_and_method(event)

    token = event['authorizationToken'].replace('Bearer ', '')

    if (http_method, resource) in ADMIN_ROUTES:
        return validade_with_cognito(token, event['methodArn'])
    else:
        try:
            jwt.decode(token, get_jwt_secret(), algorithms=['HS256'])

            return generate_policy('user','Allow', event['methodArn'])
        except ExpiredSignatureError:
            return generate_policy('user','Deny', event['methodArn'])
        except InvalidTokenError:
            return validade_with_cognito(token, event['methodArn'])

def get_resource_and_method(event):
    method_arn_parts = event['methodArn'].split('/')
    http_method = method_arn_parts[2]
    resource_parts = method_arn_parts[3:]
    return http_method, '/'.join(resource_parts)

def validade_with_cognito(token, method_arn):
    try:
        validate_with_cognito_jwks(token)
        return generate_policy('user','Allow', method_arn)
    except:
        return generate_policy('user','Deny', method_arn)

def validate_with_cognito_jwks(token):
    REGION = "us-east-1"
    user_pool_id = os.getenv("USER_POOL_ID", "us-east-1_example")
    jwks_data = fetch_jwks_data(REGION, user_pool_id)
    headers = jose_jwt.get_unverified_header(token)
    chosen_jwk = find_jwk(headers, jwks_data)
    if not chosen_jwk:
        raise Exception("JWK not found")

    verify_signature(token, chosen_jwk)
    claims = jose_jwt.get_unverified_claims(token)
    if time.time() > claims["exp"]:
        raise Exception("Token expired")

    return True

def fetch_jwks_data(region, user_pool_id):
    jwks_url = f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json"
    return requests.get(jwks_url).json()["keys"]

def find_jwk(headers, jwks_data):
    return next((k for k in jwks_data if k["kid"] == headers["kid"]), None)

def verify_signature(token, chosen_jwk):
    public_key = jwk.construct(chosen_jwk)
    message, signature = token.rsplit(".", 1)
    decoded_signature = base64url_decode(signature.encode("utf-8"))
    if not public_key.verify(message.encode("utf-8"), decoded_signature):
        raise Exception("Invalid signature")

def get_jwt_secret():
    secret_name = "jwt_secret"
    region_name = "us-east-1"

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    secret = client.get_secret_value(SecretId=secret_name)
    secret_string = json.loads(secret['SecretString'])
    return secret_string['key']

def generate_policy(principal_id, effect, resource):
    auth_response = {}
    auth_response['principalId'] = principal_id

    if effect and resource:
        policy_document = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': effect,
                    'Resource': resource
                }
            ]
        }
        auth_response['policyDocument'] = policy_document

    return auth_response
