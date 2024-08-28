import boto3
from botocore.exceptions import ClientError
from server.config.config import Config

class CognitoService:
    @staticmethod
    def authenticate(username, password):
        client = boto3.client('cognito-idp', region_name=Config.COGNITO_REGION)
        try:
            response = client.initiate_auth(
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password
                },
                ClientId=Config.COGNITO_APP_CLIENT_ID
            )
            return response['AuthenticationResult']['AccessToken']
        except ClientError as e:
            print(e)
            return None
