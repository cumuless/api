from flask import Blueprint, request, g
from flask_cognito import cognito_auth_required
from server.app.services.bedrock_service import BedrockService
from server.app.utils import schemas as s
from server.app.utils.helpers import get_source_indeces_from_chat
from server.app.utils.schemas import validate_schema
from server.app.services.dynamodb_service import DynamoDBService
from server.app.services.vectordb_service import VectorDBService
from server.app.services.azure_openai_service import AzureOpenAIService
from server.app.utils.helpers import title_query_string

main_bp = Blueprint('main', __name__)

bedrock_service = BedrockService()
dynamodb_service = DynamoDBService('Users', 'userId')
vectordb_service = VectorDBService()
azure_openai_service = AzureOpenAIService()

@main_bp.route('/')
def index():
    return "Hello, World!"

@main_bp.route('/me', methods=['GET'])
@cognito_auth_required
@validate_schema(s.GetFromUserObjectSchema)
def me():
    userId = g.validated_data['userId']
    user = dynamodb_service.get_user(userId)
    return user

@main_bp.route('/new_user', methods=['POST'])
@cognito_auth_required
@validate_schema(s.NewUserSchema)
def new_user():
    userId, email = g.validated_data['userId'], g.validated_data['email']
    dynamodb_service.create_user(userId, email)
    user = dynamodb_service.get_user(userId)
    return user

@main_bp.route('/bookmarks', methods=['GET'])
@cognito_auth_required
@validate_schema(s.GetFromUserObjectSchema)
def bookmarks():
    userId = g.validated_data['userId']
    user = dynamodb_service.get_user(userId)
    return user.get('bookmarks', [])

@main_bp.route('/bookmarks', methods=['POST'])
@cognito_auth_required
@validate_schema(s.UserAndSourceSchema)
def bookmarks_post():
    userId, sourceId = g.validated_data['userId'], g.validated_data['sourceId']
    user = dynamodb_service.get_user(userId)
    email = user.get('email', '')

    vectordb_filter = f"docId == '{sourceId}'"

    results = vectordb_service.filter_search(vectordb_filter, email)
    
    try:
        result = results[0]
        contentType, sourceType, url, title = result['contentType'], result['sourceType'], result['url'], result['title']
        return dynamodb_service.add_to_array_with_replacement(userId, 'bookmarks', {'title': title, 'url': url, 'contentType': contentType, 'sourceType': sourceType})
    except:
        print("No results found for the click.")
        return None

@main_bp.route('/recents', methods=['GET'])
@cognito_auth_required
@validate_schema(s.GetFromUserObjectSchema)
def recents():
    userId = g.validated_data['userId']
    user = dynamodb_service.get_user(userId)
    return user.get('recents', [])

@main_bp.route('/recent_searches', methods=['GET'])
@cognito_auth_required
@validate_schema(s.GetFromUserObjectSchema)
def recent_searches():
    userId = g.validated_data['userId']
    user = dynamodb_service.get_user(userId)
    return user.get('recent_searches', [])

@main_bp.route('/quick_search', methods=['POST'])
@cognito_auth_required
@validate_schema(s.UserAndQuerySchema)
def quick_search():
    userId, query = g.validated_data['userId'], g.validated_data['query']
    user = dynamodb_service.get_user(userId)
    email = user.get('email', '')

    vectordb_filter = title_query_string(query)
    results = vectordb_service.filter_search(vectordb_filter, email)
    return results

@main_bp.route('/search', methods=['POST'])
@cognito_auth_required
@validate_schema(s.UserAndQuerySchema)
def search():
    userId, query = g.validated_data['userId'], g.validated_data['query']
    user = dynamodb_service.get_user(userId)
    email = user.get('email', '')

    embedding = bedrock_service.embed_text(query)
    vectordb_filter = title_query_string(query)

    dynamodb_service.add_to_array_with_replacement(userId, 'recent_searches', query)
    results = vectordb_service.filter_search(vectordb_filter, email)
    vectorsearch_results = vectordb_service.vector_search(embedding, email)
    results.extend(vectorsearch_results)

    return results

@main_bp.route('/chat', methods=['POST'])
@cognito_auth_required
@validate_schema(s.UserAndQuerySchema)
def chat():
    userId, query = g.validated_data['userId'], g.validated_data['query']
    user = dynamodb_service.get_user(userId)
    email = user.get('email', '')

    embedding = bedrock_service.embed_text(query)
    
    vectorsearch_results = vectordb_service.vector_search(embedding, email)
    vectorsearch_results = vectorsearch_results[:8]
    resp = azure_openai_service.query(query, sources=vectorsearch_results)
    source_indeces, resp = get_source_indeces_from_chat(resp)

    # Removing 'content' key from each dictionary
    vectorsearch_results = [{key: value for key, value in item.items() if key != 'content'} for item in vectorsearch_results]
    for result in vectorsearch_results:
        print(result['title'])
    vectorsearch_results = [item for index, item in enumerate(vectorsearch_results) if index + 1 in source_indeces]
    print(source_indeces)

    response = {'message': resp, 'sources': vectorsearch_results}
    return response

@main_bp.route('/click', methods=['POST'])
@cognito_auth_required
@validate_schema(s.UserAndSourceSchema)
def click():
    userId, sourceId = g.validated_data['userId'], g.validated_data['sourceId']
    user = dynamodb_service.get_user(userId)
    email = user.get('email', '')

    vectordb_filter = f"docId == '{sourceId}'"

    results = vectordb_service.filter_search(vectordb_filter, email)
    
    try:
        result = results[0]
        contentType, sourceType, url, title = result['contentType'], result['sourceType'], result['url'], result['title']
        return dynamodb_service.add_to_array_with_replacement(userId, 'recents', {'title': title, 'url': url, 'contentType': contentType, 'sourceType': sourceType})
    except:
        print("No results found for the click.")
        return None
