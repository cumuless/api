import json

import os
import json
import http.client
from datetime import datetime

ZILLIZ_API_URL = os.getenv('ZILLIZ_API_URL')
ZILLIZ_API_KEY = os.getenv('ZILLIZ_API_KEY')
url_parts = ZILLIZ_API_URL.split('/')
host = url_parts[2]

headers = {
    "Authorization": f"Bearer {ZILLIZ_API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

class VectorDBService:
    def __init__(self):
        pass

    def vector_search(self, embedding, email):
        conn = http.client.HTTPSConnection(host)

        # Prepare payload
        payload = json.dumps({
            "collectionName": "MainCollection",
            "data": [embedding],
            "filter": f"ARRAY_CONTAINS(access, '{email}')",
            "limit": 70,
            "outputFields": ['content', 'contentType', 'docId', 'lastUpdated', 'sourceType', 'title', 'url'],
        })

        # Make the request
        conn.request("POST", "/v2/vectordb/entities/search", payload, headers)

        # Get the response
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        data = json.loads(data)

        # Close connection
        conn.close()

        # Handle the response
        if data['code'] != 0:
            print(f'Failed to search: {data}')
            return None

        data = data['data']

        
        def partition_by_year(data):
            # Define a function to extract the year from the 'lastUpdated' field
            def get_year(date_str):
                return datetime.fromisoformat(date_str.replace('Z', '+00:00')).year

            # Partition data into two lists
            newer = [item for item in data if get_year(item['lastUpdated']) >= 2024]
            older = [item for item in data if get_year(item['lastUpdated']) < 2024]

            # Concatenate the lists
            return newer + older
        
        data = partition_by_year(data)

        return data
    
    def filter_search(self, filter, email):
        conn = http.client.HTTPSConnection(host)

        # Prepare payload
        payload = json.dumps({
            "collectionName": "MainCollection",
            "filter": f"(ARRAY_CONTAINS(access, '{email}')) and ({filter})",
            "limit": 5,
            "outputFields": ['content', 'contentType', 'docId', 'lastUpdated', 'sourceType', 'title', 'url'],
        })

        # Make the request
        conn.request("POST", "/v2/vectordb/entities/query", payload, headers)

        # Get the response
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        data = json.loads(data)

        # Close connection
        conn.close()

        # Handle the response
        if data['code'] != 0:
            print(f'Failed to search: {data}')
            return None

        data = data['data']

        
        def partition_by_year(data):
            # Define a function to extract the year from the 'lastUpdated' field
            def get_year(date_str):
                return datetime.fromisoformat(date_str.replace('Z', '+00:00')).year

            # Partition data into two lists
            newer = [item for item in data if get_year(item['lastUpdated']) >= 2024]
            older = [item for item in data if get_year(item['lastUpdated']) < 2024]

            # Concatenate the lists
            return newer + older
        
        data = partition_by_year(data)
        return data