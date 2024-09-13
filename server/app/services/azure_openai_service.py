import os
import requests
import base64

from server.app.utils.constants import llm_boilerplate

# Configuration
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
headers = {
    "Content-Type": "application/json",
    "api-key": API_KEY,
}

ENDPOINT = "https://cumuless-dev.openai.azure.com/openai/deployments/CumulessChatLLM/chat/completions?api-version=2024-02-15-preview"

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
        messagesWithQuery = messages.append({"role": "user", "content": [{"type": "text", "text": query}]})
        messagesWithQueryAndSources = messages.append({"role": "user", "content": [{"type": "text", "text": queryWithSources}]})

        payload = {
            "messages": messagesWithQueryAndSources,
            "temperature": 0.7,
            "top_p": 0.95,
            "max_tokens": 800
        }

        try:
            response = requests.post(ENDPOINT, headers=headers, json=payload)
            response.raise_for_status()
        except requests.RequestException as e:
            raise SystemExit(f"Failed to make the request. Error: {e}")

        print(response.json())
        return response.json()
