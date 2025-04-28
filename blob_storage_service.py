# backend/blob_storage_service.py

import os
from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.identity import DefaultAzureCredential

class BlobStorageService:
    def __init__(self, storage_account_name=None, container_name=None, connection_string=None):
        """Initialize the Azure Blob Storage service.
        
        Args:
            storage_account_name: The name of the Azure Storage account.
            container_name: The name of the blob container.
            connection_string: Optional connection string (if not using DefaultAzureCredential).
        """
        # These would typically come from environment variables in production
        self.storage_account_name = storage_account_name or os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
        self.container_name = container_name or os.getenv("AZURE_STORAGE_CONTAINER_NAME")
        self.connection_string = connection_string or os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        
        if not self.container_name:
            raise ValueError("Missing required Blob Storage container name")
        
        # Initialize the blob service client
        if self.connection_string:
            # Use connection string if provided
            self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        elif self.storage_account_name:
            # Use DefaultAzureCredential if storage account name is provided
            account_url = f"https://{self.storage_account_name}.blob.core.windows.net"
            self.blob_service_client = BlobServiceClient(account_url=account_url, credential=DefaultAzureCredential())
        else:
            raise ValueError("Either storage_account_name or connection_string must be provided")
        
        # Get a reference to the container
        self.container_client = self.blob_service_client.get_container_client(self.container_name)
        
        # Create the container if it doesn't exist
        try:
            self.container_client.get_container_properties()
        except Exception:
            self.container_client.create_container()
    
    def upload_document(self, document_content, blob_name, content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"):
        """Upload a document to Azure Blob Storage.
        
        Args:
            document_content: The content of the document (bytes).
            blob_name: The name of the blob.
            content_type: The content type of the document.
            
        Returns:
            The URL of the uploaded document if successful, None otherwise.
        """
        try:
            # Get a blob client
            blob_client = self.container_client.get_blob_client(blob_name)
            
            # Set content settings
            content_settings = ContentSettings(content_type=content_type)
            
            # Upload the document
            blob_client.upload_blob(document_content, overwrite=True, content_settings=content_settings)
            
            # Return the URL of the uploaded document
            return blob_client.url
        except Exception as e:
            print(f"Error uploading document: {e}")
            return None
    
    def download_document(self, blob_name):
        """Download a document from Azure Blob Storage.
        
        Args:
            blob_name: The name of the blob.
            
        Returns:
            The content of the document if successful, None otherwise.
        """
        try:
            # Get a blob client
            blob_client = self.container_client.get_blob_client(blob_name)
            
            # Download the document
            download = blob_client.download_blob()
            
            # Return the content
            return download.readall()
        except Exception as e:
            print(f"Error downloading document: {e}")
            return None
    
    def list_documents(self, prefix=None):
        """List documents in Azure Blob Storage.
        
        Args:
            prefix: Optional prefix to filter blobs.
            
        Returns:
            A list of blob names if successful, None otherwise.
        """
        try:
            # List the blobs
            blobs = self.container_client.list_blobs(name_starts_with=prefix)
            
            # Return the blob names
            return [blob.name for blob in blobs]
        except Exception as e:
            print(f"Error listing documents: {e}")
            return None
    
    def get_document_url(self, blob_name):
        """Get the URL of a document in Azure Blob Storage.
        
        Args:
            blob_name: The name of the blob.
            
        Returns:
            The URL of the document if successful, None otherwise.
        """
        try:
            # Get a blob client
            blob_client = self.container_client.get_blob_client(blob_name)
            
            # Return the URL
            return blob_client.url
        except Exception as e:
            print(f"Error getting document URL: {e}")
            return None

# Example usage (for testing purposes)
if __name__ == "__main__":
    try:
        # This requires environment variables to be set
        blob_storage_service = BlobStorageService()
        
        # Example: List documents
        documents = blob_storage_service.list_documents()
        
        if documents:
            print(f"Found {len(documents)} documents:")
            for doc in documents:
                print(f"Name: {doc}")
                print(f"URL: {blob_storage_service.get_document_url(doc)}")
                print()
        else:
            print("No documents found or error occurred.")
    except Exception as e:
        print(f"Failed to list documents: {e}")
        print("Please ensure Azure Blob Storage environment variables are set.")
