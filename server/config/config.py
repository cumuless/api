import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    COGNITO_USERPOOL_ID = os.getenv('COGNITO_USERPOOL_ID')
    COGNITO_APP_CLIENT_ID = os.getenv('COGNITO_APP_CLIENT_ID')
    COGNITO_REGION = os.getenv('COGNITO_REGION')
    COGNITO_JWK_URL = os.getenv('COGNITO_JWK_URL')
    COGNITO_CHECK_TOKEN_EXPIRATION = False
