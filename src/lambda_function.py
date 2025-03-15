import json
import jwt
import boto3
from jwt import ExpiredSignatureError, InvalidTokenError

def lambda_handler(event, context):
    token = event['authorizationToken']
    secret_key = get_jwt_secret()

    token = token.replace('Bearer ', '')

    try:
        jwt.decode(token, secret_key, algorithms=['HS256'])
    except ExpiredSignatureError:
        return generate_policy('user', 'Deny', event['methodArn'])
    except InvalidTokenError:
        return generate_policy('user', 'Deny', event['methodArn'])

    return generate_policy('user', 'Allow', event['methodArn'])

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
