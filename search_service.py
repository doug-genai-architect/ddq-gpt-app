# backend/search_service.py

import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType

class AzureSearchService:
    def __init__(self, search_service_name=None, search_index_name=None, search_api_key=None):
        """Initialize the Azure AI Search service.
        
        Args:
            search_service_name: The name of the Azure AI Search service.
            search_index_name: The name of the search index.
            search_api_key: The API key for the search service.
        """
        # These would typically come from environment variables in production
        self.search_service_name = search_service_name or os.getenv("AZURE_SEARCH_SERVICE_NAME")
        self.search_index_name = search_index_name or os.getenv("AZURE_SEARCH_INDEX_NAME")
        self.search_api_key = search_api_key or os.getenv("AZURE_SEARCH_API_KEY")
        
        if not all([self.search_service_name, self.search_index_name, self.search_api_key]):
            raise ValueError("Missing required Azure AI Search configuration")
        
        # Create the search endpoint
        self.search_endpoint = f"https://{self.search_service_name}.search.windows.net"
        
        # Initialize the search client
        self.search_client = SearchClient(
            endpoint=self.search_endpoint,
            index_name=self.search_index_name,
            credential=AzureKeyCredential(self.search_api_key)
        )
    
    def search_documents(self, query_text, filter_condition=None, top=5):
        """Search for documents in the Azure AI Search index.
        
        Args:
            query_text: The search query text.
            filter_condition: Optional OData filter condition.
            top: Maximum number of results to return.
            
        Returns:
            A list of search results.
        """
        try:
            # Use semantic search with vector capabilities if available
            results = self.search_client.search(
                search_text=query_text,
                query_type=QueryType.SEMANTIC,  # Use semantic search for better results
                query_language="en-us",
                semantic_configuration_name="default",
                filter=filter_condition,
                top=top,
                include_total_count=True
            )
            
            # Process and return the results
            search_results = []
            for result in results:
                # Extract relevant fields from the search result
                document = {
                    "id": result["id"],
                    "title": result.get("title", "Untitled"),
                    "content": result.get("content", ""),
                    "source": result.get("source", ""),
                    "sourceFile": result.get("sourceFile", ""),
                    "score": result["@search.score"],
                    "captions": result.get("@search.captions", [])
                }
                search_results.append(document)
            
            return {
                "count": results.get_count(),
                "results": search_results
            }
        except Exception as e:
            print(f"Error searching documents: {e}")
            raise

    def get_document_by_id(self, document_id):
        """Get a document by its ID.
        
        Args:
            document_id: The ID of the document to retrieve.
            
        Returns:
            The document if found, None otherwise.
        """
        try:
            return self.search_client.get_document(key=document_id)
        except Exception as e:
            print(f"Error getting document by ID: {e}")
            return None

# Example usage (for testing purposes)
if __name__ == "__main__":
    try:
        # This requires environment variables to be set
        search_service = AzureSearchService()
        
        # Example search query
        results = search_service.search_documents("ESG policy")
        
        print(f"Found {results['count']} results:")
        for idx, result in enumerate(results['results']):
            print(f"\nResult {idx+1}:")
            print(f"Title: {result['title']}")
            print(f"Source: {result['source']}")
            print(f"Score: {result['score']}")
            print(f"Content snippet: {result['content'][:150]}...")
    except Exception as e:
        print(f"Failed to search documents: {e}")
        print("Please ensure Azure AI Search environment variables are set.")
