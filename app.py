# backend/app.py

import os
import json
from flask import Flask, request, jsonify
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
from azure.identity import DefaultAzureCredential

# Import custom services
from openai_service import get_openai_completion, AZURE_OAI_ENDPOINT, AZURE_OAI_MODEL_NAME
from search_service import AzureSearchService
from blob_storage_service import BlobStorageService
# SharePoint service might be used later for direct access or indexing setup
# from sharepoint_service import SharePointService

# --- Monitoring Setup (Azure Monitor OpenTelemetry) ---
# Configure OpenTelemetry to use Azure Monitor Exporter
# Ensure AZURE_MONITOR_CONNECTION_STRING is set in environment variables
from azure.monitor.opentelemetry import configure_azure_monitor

# Configure Azure Monitor
if os.getenv("AZURE_MONITOR_CONNECTION_STRING"):
    configure_azure_monitor()
    print("Azure Monitor configured for OpenTelemetry.")
else:
    print("Azure Monitor connection string not found. Skipping OpenTelemetry configuration.")

# --- Flask App Initialization ---
app = Flask(__name__)

# --- Load System Prompt ---
try:
    with open("system_prompt.txt", "r") as f:
        SYSTEM_PROMPT = f.read()
    print("System prompt loaded successfully.")
except FileNotFoundError:
    SYSTEM_PROMPT = "You are a helpful AI assistant." # Fallback prompt
    print("Warning: system_prompt.txt not found. Using default prompt.")

# --- Initialize Services ---
# Use environment variables for configuration
# These should be set in the Azure App Service configuration
try:
    search_service = AzureSearchService()
    print("Azure AI Search service initialized.")
except ValueError as e:
    print(f"Error initializing Azure AI Search: {e}. Search functionality will be disabled.")
    search_service = None

try:
    blob_service = BlobStorageService()
    print("Azure Blob Storage service initialized.")
except ValueError as e:
    print(f"Error initializing Azure Blob Storage: {e}. Document upload will be disabled.")
    blob_service = None

# --- API Routes ---
@app.route("/api/chat", methods=["POST"])
def chat_handler():
    """Handles chat requests, performs search, calls OpenAI, and prepares response."""
    try:
        data = request.get_json()
        user_question = data.get("prompt")
        # history = data.get("history", []) # Future use: maintain conversation history

        if not user_question:
            return jsonify({"error": "No prompt provided"}), 400

        # 1. Search for relevant documents (Context Retrieval)
        search_context = ""
        source_files = set() # Keep track of unique source files
        if search_service:
            try:
                search_results = search_service.search_documents(user_question, top=3)
                if search_results and search_results["results"]:
                    search_context += "\n\nRelevant Document Snippets:\n"
                    for result in search_results["results"]:
                        # Include content and source file information
                        content_snippet = result.get("content", "")
                        source_file = result.get("sourceFile", "Unknown Source")
                        search_context += f"\n---\nSource: {source_file}\nSnippet: {content_snippet}\n---"
                        source_files.add(source_file)
                else:
                    search_context = "\n\nNo relevant documents found in the search index for this query."
            except Exception as e:
                print(f"Error during Azure AI Search query: {e}")
                search_context = "\n\nError retrieving documents from search index."
        else:
            search_context = "\n\nAzure AI Search service is not configured."

        # 2. Prepare messages for OpenAI
        messages = [
            SystemMessage(content=SYSTEM_PROMPT + search_context), # Add search context to system prompt
            UserMessage(content=user_question)
        ]

        # 3. Call Azure OpenAI
        try:
            completion = get_openai_completion(messages)
            ai_response_text = completion.choices[0].message.content if completion.choices else "Sorry, I could not generate a response."
        except Exception as e:
            print(f"Error calling Azure OpenAI: {e}")
            return jsonify({"error": "Failed to get response from AI model"}), 500

        # 4. Generate Document and Upload (Placeholder for Step 013)
        # This part will be implemented in the next step
        # For now, we simulate the document URL
        document_url = None
        if blob_service:
            # Simulate document generation and upload
            try:
                # In reality, call a function like: generate_and_upload_docx(user_question, ai_response_text, list(source_files))
                simulated_blob_name = f"generated_docs/response_{user_question[:20].replace(' ', '_')}_{os.urandom(4).hex()}.docx"
                # Simulate content (replace with actual docx bytes)
                simulated_content = f"Question: {user_question}\n\nAnswer: {ai_response_text}\n\nSources: {', '.join(source_files) if source_files else 'N/A'}".encode("utf-8")
                document_url = blob_service.upload_document(simulated_content, simulated_blob_name, content_type="text/plain") # Use text/plain for simulation
                print(f"Simulated document uploaded to: {document_url}")
            except Exception as e:
                print(f"Error during simulated document upload: {e}")
        else:
            print("Blob service not configured. Skipping document upload.")

        # 5. Return response to frontend
        return jsonify({
            "ai_response": ai_response_text,
            "document_url": document_url,
            "sources": list(source_files) # Send back sources used
        })

    except Exception as e:
        print(f"An unexpected error occurred in /api/chat: {e}")
        # Log the exception details using OpenTelemetry if configured
        # tracer = trace.get_tracer(__name__)
        # with tracer.start_as_current_span("chat_handler_error") as span:
        #     span.set_attribute("error.message", str(e))
        #     span.record_exception(e)
        return jsonify({"error": "An internal server error occurred"}), 500

@app.route("/health", methods=["GET"])
def health_check():
    """Basic health check endpoint."""
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    # Run the Flask app
    # Use 0.0.0.0 to make it accessible externally (within container/VM)
    # Port 5000 is common for Flask development
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

