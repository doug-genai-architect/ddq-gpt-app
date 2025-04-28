# Azure Deployment Guide: DDQ Chat Application

## 1. Introduction

This document provides comprehensive instructions for deploying the DDQ Chat Application, consisting of a Next.js frontend and a Flask backend, to Azure App Service. The application leverages several Azure services, including Azure OpenAI, Azure AI Search, Azure Blob Storage, and Azure Monitor, integrated with Entra ID for authentication.

## 2. Prerequisites

Before starting the deployment, ensure you have the following:

*   **Azure Subscription:** An active Azure subscription with permissions to create and manage resources.
*   **Azure CLI:** Installed and configured on your local machine. You can install it from [here](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli).
*   **Git:** Installed on your local machine.
*   **Node.js and npm/pnpm:** Required for building the Next.js frontend. (pnpm is used in this project).
*   **Python:** Required for the Flask backend (Python 3.10+ recommended).
*   **Application Code:** Access to the complete source code for both the frontend (`ddq-chat-app-frontend`) and backend (`backend`) applications.

## 3. Azure Resource Setup

Several Azure resources need to be provisioned. You can create these using the Azure Portal, Azure CLI, or ARM/Bicep templates.

**Required Resources:**

1.  **Resource Group:** A logical container for all related resources.
    ```bash
    az group create --name <YourResourceGroupName> --location <YourAzureRegion>
    ```
2.  **App Service Plan:** Defines the underlying compute resources for your web apps.
    ```bash
    # Choose a suitable SKU (e.g., B1, S1, P1v2) and OS (Linux)
    az appservice plan create --name <YourAppServicePlanName> --resource-group <YourResourceGroupName> --sku B1 --is-linux
    ```
3.  **Web App for Backend (Flask):** Hosts the Python Flask application.
    ```bash
    # Replace <YourBackendAppName> with a unique name
    az webapp create --name <YourBackendAppName> --resource-group <YourResourceGroupName> --plan <YourAppServicePlanName> --runtime "PYTHON|3.10"
    ```
4.  **Web App for Frontend (Next.js):** Hosts the static build output of the Next.js application.
    ```bash
    # Replace <YourFrontendAppName> with a unique name
    az webapp create --name <YourFrontendAppName> --resource-group <YourResourceGroupName> --plan <YourAppServicePlanName> --runtime "NODE|20-lts" # Node runtime is needed for build/deployment steps, even if serving static files
    ```
5.  **Azure OpenAI Service:** Provides the chat completion capabilities. (Ensure you have access and have deployed the required model, e.g., `o4-mini-custom-gpt`). Note the endpoint URL.
6.  **Azure AI Search Service:** Indexes and searches documents from SharePoint. Note the service name, index name, and an Admin or Query API key.
7.  **Azure Storage Account:** Used for Blob Storage to store generated DOCX files.
    ```bash
    # Replace <YourStorageAccountName> with a unique name
    az storage account create --name <YourStorageAccountName> --resource-group <YourResourceGroupName> --location <YourAzureRegion> --sku Standard_LRS
    
    # Create a Blob Container (e.g., 'generated-docs')
    az storage container create --name generated-docs --account-name <YourStorageAccountName> --auth-mode login
    ```
    Note the Storage Account Name and the container name (`generated-docs`).
8.  **Azure Monitor:** (Optional but recommended) For monitoring application performance and logs. Create an Application Insights resource.
    ```bash
    az monitor app-insights component create --app <YourAppInsightsName> --location <YourAzureRegion> --resource-group <YourResourceGroupName>
    ```
    Note the Application Insights Connection String.
9.  **Entra ID App Registration:** Required for user authentication (frontend) and service-to-service authentication (backend).
    *   Create an App Registration in your Entra ID tenant.
    *   Configure Redirect URIs for the frontend app (e.g., `https://<YourFrontendAppName>.azurewebsites.net/`).
    *   Configure a Post Logout Redirect URI (e.g., `https://<YourFrontendAppName>.azurewebsites.net/`).
    *   Enable ID tokens.
    *   Create a Client Secret for the backend service (if using client credentials flow for SharePoint/Graph API access).
    *   Grant necessary API permissions (e.g., `User.Read` for login, `Sites.Read.All` or more specific permissions for SharePoint access via Microsoft Graph).
    *   Note the Application (client) ID and Tenant ID.

## 4. Configuration (Environment Variables)

Configure the necessary environment variables for both the frontend and backend App Services. This is crucial for connecting to other Azure services and for authentication.

**Backend App Service (`<YourBackendAppName>`):**

Navigate to your backend App Service in the Azure Portal -> Configuration -> Application settings.

*   `AZURE_TENANT_ID`: Your Entra ID Tenant ID.
*   `AZURE_CLIENT_ID`: Client ID of the Entra ID App Registration (used for SharePoint/Graph access).
*   `AZURE_CLIENT_SECRET`: Client Secret generated for the App Registration.
*   `AZURE_OAI_ENDPOINT`: Endpoint URL of your Azure OpenAI deployment (e.g., `https://bfija-m83d9xpw-eastus2.services.ai.azure.com/models`).
*   `AZURE_OAI_MODEL_NAME`: The deployed model name (e.g., `o4-mini-custom-gpt`).
*   `AZURE_SEARCH_SERVICE_NAME`: Name of your Azure AI Search service.
*   `AZURE_SEARCH_INDEX_NAME`: Name of the index within your search service.
*   `AZURE_SEARCH_API_KEY`: An Admin or Query API key for your search service.
*   `AZURE_STORAGE_ACCOUNT_NAME`: Name of your Azure Storage Account.
*   `AZURE_STORAGE_CONTAINER_NAME`: Name of the blob container (e.g., `generated-docs`).
*   `SHAREPOINT_SITE_URL`: The URL of the SharePoint site (e.g., `https://yourtenant.sharepoint.com/sites/YourSite`).
*   `SHAREPOINT_SITE_NAME`: The relative path/name used in Graph API calls (e.g., `yourtenant.sharepoint.com:/sites/YourSite`).
*   `SHAREPOINT_DOCUMENT_LIBRARY`: The name or ID of the document library.
*   `AZURE_MONITOR_CONNECTION_STRING`: Connection string for Application Insights (if using monitoring).
*   `WEBSITES_PORT`: Set to `8000` (or the port Gunicorn will use).

**Frontend App Service (`<YourFrontendAppName>`):**

Navigate to your frontend App Service in the Azure Portal -> Configuration -> Application settings.

*   `NEXT_PUBLIC_AZURE_AD_CLIENT_ID`: Client ID of the Entra ID App Registration (used for user login).
*   `NEXT_PUBLIC_AZURE_AD_TENANT_ID`: Your Entra ID Tenant ID.
*   `NEXT_PUBLIC_REDIRECT_URI`: The full redirect URI (e.g., `https://<YourFrontendAppName>.azurewebsites.net/`).
*   `NEXT_PUBLIC_POST_LOGOUT_REDIRECT_URI`: The full post logout redirect URI (e.g., `https://<YourFrontendAppName>.azurewebsites.net/`).
*   `NEXT_PUBLIC_BACKEND_API_URL`: The full URL of your deployed backend API (e.g., `https://<YourBackendAppName>.azurewebsites.net/api`).

**Note:** Variables starting with `NEXT_PUBLIC_` are exposed to the browser. Do not put secrets here.

## 5. Backend Deployment (Flask)

We recommend deploying the Flask backend using Zip Deploy with Azure CLI.

1.  **Navigate to the backend directory:**
    ```bash
    cd /path/to/your/project/backend
    ```
2.  **Create `requirements.txt`:** Ensure all dependencies are listed.
    ```bash
    # Activate your virtual environment if you have one
    # source ../venv/bin/activate 
    pip freeze > requirements.txt
    # Deactivate if needed
    # deactivate
    ```
3.  **Create `startup.txt` or configure Startup Command:**
    Azure App Service needs to know how to start your Flask app. Use Gunicorn for production.
    *   **Option A (startup.txt):** Create a file named `startup.txt` in the `backend` directory with the following content (adjust module/app name if needed):
        ```
        gunicorn --bind=0.0.0.0 --timeout 600 app:app
        ```
    *   **Option B (Startup Command):** In the Azure Portal for the backend App Service -> Configuration -> General settings -> Startup Command, enter:
        ```
        gunicorn --bind=0.0.0.0 --timeout 600 app:app
        ```
4.  **Zip the backend code:** Create a zip file containing `app.py`, `openai_service.py`, `search_service.py`, `blob_storage_service.py`, `sharepoint_service.py`, `document_generator.py`, `system_prompt.txt`, `requirements.txt`, and `startup.txt` (if used).
    ```bash
    # Make sure you are in the parent directory of 'backend'
    zip -r backend.zip backend/
    ```
5.  **Deploy using Azure CLI:**
    ```bash
    az webapp deploy --name <YourBackendAppName> --resource-group <YourResourceGroupName> --src-path backend.zip --type zip
    ```

## 6. Frontend Deployment (Next.js)

The Next.js app needs to be built into static assets, which are then deployed.

1.  **Navigate to the frontend directory:**
    ```bash
    cd /path/to/your/project/ddq-chat-app-frontend
    ```
2.  **Install dependencies:**
    ```bash
    pnpm install
    ```
3.  **Build the Next.js application:**
    ```bash
    pnpm build
    ```
    This command typically generates a `.next` or `out` directory containing the built assets.
4.  **Configure App Service for Static Site (Optional but Recommended):**
    While the Node runtime was chosen, you can optimize for serving static files. You might need to configure rewrite rules if using Next.js routing features extensively in static export, or serve from the `.next/static` directory.
    *   A simpler approach for many Next.js apps is to let the default Node server handle serving, which works well with the standard `pnpm build` output.
5.  **Zip the build output:** Create a zip file containing the contents of the `.next` directory and `package.json`, `pnpm-lock.yaml`.
    ```bash
    # Ensure you are in the ddq-chat-app-frontend directory
    # Create a deployment package (adjust if your build output is different)
    zip -r frontend.zip .next/ package.json pnpm-lock.yaml public/
    ```
6.  **Deploy using Azure CLI:**
    ```bash
    az webapp deploy --name <YourFrontendAppName> --resource-group <YourResourceGroupName> --src-path frontend.zip --type zip
    ```

## 7. Post-Deployment Steps

1.  **Verify Deployment:** Access the frontend URL (`https://<YourFrontendAppName>.azurewebsites.net/`) and test the application's functionality.
2.  **Check Logs:** Monitor logs for both frontend and backend App Services via Azure Portal -> Log stream or Diagnostic settings if issues arise.
3.  **Configure CORS (Backend):** If the frontend and backend are on different domains (which they are with separate App Services), you'll need to configure Cross-Origin Resource Sharing (CORS) on the backend App Service. Go to Azure Portal -> Backend App Service -> API -> CORS. Add the frontend URL (`https://<YourFrontendAppName>.azurewebsites.net`) to the allowed origins.
4.  **Monitoring:** Check Application Insights for performance metrics, exceptions, and custom telemetry if configured.

## 8. Alternative Deployment Methods

*   **VS Code Azure App Service Extension:** Provides a UI for deploying applications directly from VS Code.
*   **GitHub Actions / Azure DevOps:** Set up CI/CD pipelines to automate the build and deployment process whenever code is pushed to your repository. This is the recommended approach for production environments.

This guide provides the fundamental steps for deploying the DDQ Chat Application to Azure App Service. Remember to adapt resource names, regions, and specific configurations to your environment.
