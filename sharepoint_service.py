# backend/sharepoint_service.py

import os
import requests
from azure.identity import DefaultAzureCredential
import msal

class SharePointService:
    def __init__(self, tenant_id=None, client_id=None, client_secret=None, 
                 sharepoint_site_url=None, sharepoint_site_name=None, document_library=None):
        """Initialize the SharePoint service.
        
        Args:
            tenant_id: The Azure tenant ID.
            client_id: The Azure client ID.
            client_secret: The Azure client secret.
            sharepoint_site_url: The SharePoint site URL.
            sharepoint_site_name: The SharePoint site name.
            document_library: The document library name.
        """
        # These would typically come from environment variables in production
        self.tenant_id = tenant_id or os.getenv("AZURE_TENANT_ID")
        self.client_id = client_id or os.getenv("AZURE_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("AZURE_CLIENT_SECRET")
        self.sharepoint_site_url = sharepoint_site_url or os.getenv("SHAREPOINT_SITE_URL")
        self.sharepoint_site_name = sharepoint_site_name or os.getenv("SHAREPOINT_SITE_NAME")
        self.document_library = document_library or os.getenv("SHAREPOINT_DOCUMENT_LIBRARY")
        
        if not all([self.tenant_id, self.client_id, self.client_secret, 
                   self.sharepoint_site_url, self.sharepoint_site_name]):
            raise ValueError("Missing required SharePoint configuration")
        
        # Microsoft Graph API endpoint
        self.graph_api_endpoint = "https://graph.microsoft.com/v1.0"
        
        # Initialize the MSAL app
        self.app = msal.ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}"
        )
    
    def get_access_token(self):
        """Get an access token for the Microsoft Graph API.
        
        Returns:
            The access token if successful, None otherwise.
        """
        try:
            # Acquire token for Microsoft Graph API
            scopes = ["https://graph.microsoft.com/.default"]
            result = self.app.acquire_token_for_client(scopes=scopes)
            
            if "access_token" in result:
                return result["access_token"]
            else:
                print(f"Error acquiring token: {result.get('error')}")
                print(f"Error description: {result.get('error_description')}")
                return None
        except Exception as e:
            print(f"Error getting access token: {e}")
            return None
    
    def list_documents(self, folder_path=""):
        """List documents in a SharePoint folder.
        
        Args:
            folder_path: The path to the folder within the document library.
            
        Returns:
            A list of documents if successful, None otherwise.
        """
        try:
            access_token = self.get_access_token()
            if not access_token:
                return None
            
            # Construct the API URL
            folder_path = folder_path.strip("/")
            if folder_path:
                api_url = f"{self.graph_api_endpoint}/sites/{self.sharepoint_site_name}/drives/{self.document_library}/root:/{folder_path}:/children"
            else:
                api_url = f"{self.graph_api_endpoint}/sites/{self.sharepoint_site_name}/drives/{self.document_library}/root/children"
            
            # Make the API request
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            }
            response = requests.get(api_url, headers=headers)
            
            if response.status_code == 200:
                return response.json().get("value", [])
            else:
                print(f"Error listing documents: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"Error listing documents: {e}")
            return None
    
    def get_document_content(self, file_path):
        """Get the content of a document from SharePoint.
        
        Args:
            file_path: The path to the file within the document library.
            
        Returns:
            The document content if successful, None otherwise.
        """
        try:
            access_token = self.get_access_token()
            if not access_token:
                return None
            
            # Construct the API URL
            file_path = file_path.strip("/")
            api_url = f"{self.graph_api_endpoint}/sites/{self.sharepoint_site_name}/drives/{self.document_library}/root:/{file_path}:/content"
            
            # Make the API request
            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            response = requests.get(api_url, headers=headers)
            
            if response.status_code == 200:
                return response.content
            else:
                print(f"Error getting document content: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"Error getting document content: {e}")
            return None

# Example usage (for testing purposes)
if __name__ == "__main__":
    try:
        # This requires environment variables to be set
        sharepoint_service = SharePointService()
        
        # Example: List documents in a folder
        documents = sharepoint_service.list_documents("DDQ Documents")
        
        if documents:
            print(f"Found {len(documents)} documents:")
            for doc in documents:
                print(f"Name: {doc.get('name')}")
                print(f"Type: {doc.get('file', {}).get('mimeType', 'Folder')}")
                print(f"Last Modified: {doc.get('lastModifiedDateTime')}")
                print()
        else:
            print("No documents found or error occurred.")
    except Exception as e:
        print(f"Failed to list documents: {e}")
        print("Please ensure SharePoint environment variables are set.")
