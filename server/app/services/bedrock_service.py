import boto3
import json

class BedrockService:
    def __init__(self, region_name="us-east-1"):
        self.client = boto3.client('bedrock-runtime', region_name=region_name)

    def embed_text(self, text):
        input_payload = json.dumps({"inputText": text, "dimensions": 1024})
        
        try:
            response = self.client.invoke_model(
                modelId='amazon.titan-embed-text-v2:0',
                body=input_payload,
                contentType='application/json'
            )

            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                response_body = response['body'].read().decode('utf-8')
                response_json = json.loads(response_body)
                return response_json.get('embedding')
            else:
                print(f"Failed to get embedding: {response}")
                return None
        except Exception as e:
            print(f"Error embedding text: {e}")
            return None