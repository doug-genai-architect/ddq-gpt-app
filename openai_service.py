# backend/openai_service.py

import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
from azure.identity import DefaultAzureCredential

# Use the specific endpoint provided by the user
AZURE_OAI_ENDPOINT = "https://bfija-m83d9xpw-eastus2.services.ai.azure.com/models"
AZURE_OAI_MODEL_NAME = "o4-mini-custom-gpt"

# Initialize the client using DefaultAzureCredential
# Ensure environment variables like AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID are set
# in the Azure App Service configuration for this to work.
credential = DefaultAzureCredential()
client = ChatCompletionsClient(endpoint=AZURE_OAI_ENDPOINT, credential=credential)

def get_openai_completion(messages: list, max_tokens: int = 1500):
    """Gets a completion from the Azure OpenAI service.

    Args:
        messages: A list of message objects (SystemMessage, UserMessage, AssistantMessage).
        max_tokens: The maximum number of tokens to generate.

    Returns:
        The response object from the ChatCompletionsClient.
    """
    try:
        response = client.complete(
            messages=messages,
            model=AZURE_OAI_MODEL_NAME,
            max_tokens=max_tokens
        )
        return response
    except Exception as e:
        print(f"Error calling Azure OpenAI: {e}")
        # In a real app, you'd want more robust error handling/logging
        raise

# Example usage (for testing purposes, will be integrated into Flask app later)
if __name__ == '__main__':
    try:
        # Example requires environment variables for DefaultAzureCredential to work
        print("Attempting to call Azure OpenAI with example prompt...")
        example_messages = [
            SystemMessage(content="You are a helpful AI assistant designed to answer questions based on provided documents."),
            UserMessage(content="What is the capital of France?")
        ]
        completion = get_openai_completion(example_messages)
        print("Azure OpenAI Response:")
        print(completion)
        if completion.choices and len(completion.choices) > 0:
            print("\nAssistant Message:")
            print(completion.choices[0].message.content)
    except Exception as e:
        print(f"Failed to get completion during example run: {e}")
        print("Please ensure Azure credentials (AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID) are set as environment variables.")

