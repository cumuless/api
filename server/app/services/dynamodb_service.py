import boto3
from botocore.exceptions import ClientError
import uuid

class DynamoDBService:
    def __init__(self, table_name, pk, region_name="us-east-1"):
        self.table_name = table_name
        self.pk = pk
        self.client = boto3.client('dynamodb', region_name=region_name)
        self.resource = boto3.resource('dynamodb', region_name=region_name)
        self.table = self.resource.Table(table_name)

    def get_user(self, user_id):
        try:
            response = self.table.get_item(
                Key={
                    self.pk: user_id
                }
            )
            return response.get('Item', {})
        except Exception as e:
            print(f"Error getting user: {e}")
            return None

    def add_to_array(self, user_id, array_key, value):
        try:
            response = self.table.update_item(
                Key={
                    self.pk: user_id
                },
                UpdateExpression=f"SET {array_key} = list_append(if_not_exists({array_key}, :empty_list), :value)",
                ExpressionAttributeValues={
                    ':value': [value],
                    ':empty_list': []
                },
                ReturnValues="UPDATED_NEW"
            )
            return response.get('Attributes', {})
        except ClientError as e:
            print(f"Error updating array: {e}")
            return None
        
    def add_to_array_with_replacement(self, id, array_key, value):
        try:
            # First, get the current array
            response = self.table.get_item(
                Key={
                    self.pk: id
                },
                ProjectionExpression=array_key
            )
            current_array = response.get('Item', {}).get(array_key, [])

            # Remove the value if it already exists
            if value in current_array:
                current_array.remove(value)

            # Add the value to the array
            current_array.append(value)

            # Update the item in DynamoDB
            response = self.table.update_item(
                Key={
                    self.pk: id
                },
                UpdateExpression=f"SET {array_key} = :value",
                ExpressionAttributeValues={
                    ':value': current_array
                },
                ReturnValues="UPDATED_NEW"
            )
            return response.get('Attributes', {})
        except ClientError as e:
            print(f"Error updating array: {e}")
            return None

    def create_user(self, user_id, email):
        default_properties = {
            "bookmarks": [],
            "quickLinks": [],
            "recent_searches": [],
            "recents": [],
            "email": email,
            "userId": user_id
        }
        try:
            response = self.table.put_item(
                Item=default_properties
            )
            return response
        except ClientError as e:
            print(f"Error creating user: {e}")
            return None

    def add_item(self, id = '', item = {}):
        if id == '':
            item[self.pk] = uuid.uuid4().hex
        else:
            item[self.pk] = id
        
        try:
            response = self.table.put_item(
                Item=item
            )
            return response
        except ClientError as e:
            print(f"Error adding item to table {self.table_name}: {e}")
            return None
        
    def get_all_items(self):
        try:
            response = self.table.scan()
            items = response.get('Items', [])
            while 'LastEvaluatedKey' in response:
                response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                items.extend(response.get('Items', []))
            return items
        except ClientError as e:
            print(f"Error getting all items: {e}")
            return []
