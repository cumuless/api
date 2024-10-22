import os
import requests
import base64

from server.app.utils.constants import llm_boilerplate

# Configuration
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
headers = {
    "api-key": API_KEY,
}
print(API_KEY)
ENDPOINT = "https://cumuless-demo.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview"

class AzureOpenAIService:
    def __init__(self):
        pass

    def query(self, query = '', messages = [], sources = []):
        if len(messages) == 0:
            messages = llm_boilerplate

        queryWithSources = "**Sources**\n\n"
        index = 1
        for source in sources:
            queryWithSources += f"**{index}**\n {source['title']}\n {source['content']}\n\n"
            index += 1
        queryWithSources += f"**END OF SOURCES**\n\n**QUERY**\n\n{query}\n"
        messages.append({"role": "user", "content": [{"type": "text", "text": query}]})
        messagesWithQuery = messages.copy()
        messages.remove(messages[-1])

        messages.append({"role": "user", "content": [{"type": "text", "text": queryWithSources}]})
        messagesWithQueryAndSources = messages.copy()

        payload = {
            "messages": messagesWithQueryAndSources,
            "temperature": 0.7,
            "top_p": 0.95,
            "max_tokens": 800
        }

        print("sending request")
        try:
            response = requests.post(ENDPOINT, headers=headers, json=payload)
            response.raise_for_status()
        except requests.RequestException as e:
            return "I don't know. **SOURCES_USED: []**"

        try:
            response = response.json().get('choices', [{}])[0]['message']['content']
        except e:
            print("failed 2")
            print(e)

        return response
