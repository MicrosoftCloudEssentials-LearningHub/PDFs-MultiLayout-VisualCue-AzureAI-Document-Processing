# Demo: Azure Implementation <br/> PDF Layout Extraction with Azure AI Document Intelligence Supporting Multiple Document Versions with Visual Selection Cues (full-code approach)

`Azure Storage + Document Intelligence + AI Vision + Azure Open AI (LLMs) + Function App +  Cosmos DB`

Costa Rica

[![GitHub](https://badgen.net/badge/icon/github?icon=github&label)](https://github.com)
[![GitHub](https://img.shields.io/badge/--181717?logo=github&logoColor=ffffff)](https://github.com/)
[brown9804](https://github.com/brown9804)

Last updated: 2025-07-30

-----------------------------

> This solution is designed to be flexible and robust, supporting multiple versions of PDF documents with varying layouts, including those that use visual selection cues such as gray fills, hand-drawn Xs, checkmarks, or circles. By building on the [PDFs-Layouts-Processing-Fapp-DocIntelligence](https://github.com/MicrosoftCloudEssentials-LearningHub/PDFs-Layouts-Processing-Fapp-DocIntelligence) repository, modular approach aiming to:

- Table structure and text are extracted using Azure Document Intelligence (Layout model).
- Visual selection cues are detected using Azure AI Vision or image preprocessing.
- Visual indicators are mapped to structured data, returning only the selected values in a clean JSON format.
- Advanced semantic understanding is provided by Azure OpenAI to analyze document content and context.
- Multiple file formats are supported, including PDFs and various image formats.
- The logic is abstracted to support multiple layout variations, so the system adapts easily to new document formats and selection styles.

> [!IMPORTANT]
> This example is based on a `public network site and is intended for demonstration purposes only`. It showcases how several Azure resources can work together to achieve the desired result. Consider the section below about [Important Considerations for Production Environment](#important-considerations-for-production-environment). Please note that `these demos are intended as a guide and are based on my personal experiences. For official guidance, support, or more detailed information, please refer to Microsoft's official documentation or contact Microsoft directly`: [Microsoft Sales and Support](https://support.microsoft.com/contactus?ContactUsExperienceEntryPointAssetId=S.HP.SMC-HOME)

<details>
<summary><b>List of References</b> (Click to expand)</summary>

- [Use Azure AI services with SynapseML in Microsoft Fabric](https://learn.microsoft.com/en-us/fabric/data-science/how-to-use-ai-services-with-synapseml)
- [Plan and manage costs for Azure AI Foundry](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/costs-plan-manage)
- [Azure AI Document Intelligence documentation](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/?view=doc-intel-4.0.0)
- [Get started with the Document Intelligence Sample Labeling tool](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/v21/try-sample-label-tool?view=doc-intel-2.1.0#prerequisites-for-training-a-custom-form-model)
- [Document Intelligence Sample Labeling tool](https://fott-2-1.azurewebsites.net/)
- [Assign an Azure role for access to blob data](https://learn.microsoft.com/en-us/azure/storage/blobs/assign-azure-role-data-access?tabs=portal)
- [Build and train a custom extraction model](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/how-to-guides/build-a-custom-model?view=doc-intel-2.1.0)
- [Compose custom models - Document Intelligence](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/how-to-guides/compose-custom-models?view=doc-intel-2.1.0&tabs=studio)
- [Deploy the Sample Labeling tool](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/v21/deploy-label-tool?view=doc-intel-2.1.0)
- [Train a custom model using the Sample Labeling tool](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/v21/label-tool?view=doc-intel-2.1.0)
- [Train models with the sample-labeling tool](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/v21/supervised-table-tags?view=doc-intel-2.1.0)
- [Azure Cosmos DB - Database for the AI Era](https://learn.microsoft.com/en-us/azure/cosmos-db/introduction)
- [Consistency levels in Azure Cosmos DB](https://learn.microsoft.com/en-us/azure/cosmos-db/consistency-levels)
- [Azure Cosmos DB SQL API client library for Python](https://learn.microsoft.com/en-us/python/api/overview/azure/cosmos-readme?view=azure-python)
- [CosmosClient class documentation](https://learn.microsoft.com/en-us/python/api/azure-cosmos/azure.cosmos.cosmos_client.cosmosclient?view=azure-python)
- [Cosmos AAD Authentication](https://learn.microsoft.com/en-us/python/api/overview/azure/cosmos-readme?view=azure-python#aad-authentication)
- [Cosmos python examples](https://learn.microsoft.com/en-us/python/api/overview/azure/cosmos-readme?view=azure-python#examples)
- [Use control plane role-based access control with Azure Cosmos DB for NoSQL](https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/security/how-to-grant-control-plane-role-based-access?tabs=built-in-definition%2Ccsharp&pivots=azure-interface-portal)
- [Use data plane role-based access control with Azure Cosmos DB for NoSQL](https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/security/how-to-grant-data-plane-role-based-access?tabs=built-in-definition%2Ccsharp&pivots=azure-interface-cli)
- [Create or update Azure custom roles using Azure CLI](https://learn.microsoft.com/en-us/azure/role-based-access-control/custom-roles-cli)
- [Document Intelligence query field extraction](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/concept/query-fields?view=doc-intel-4.0.0)
- [What's new in Azure AI Document Intelligence](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/whats-new?view=doc-intel-4.0.0)
- [Managed identities for Document Intelligence](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/authentication/managed-identities?view=doc-intel-4.0.0)
  
</details>

<details>
<summary><b>Table of Content</b> (Click to expand)</summary>
  
- [Important Considerations for Production Environment](#important-considerations-for-production-environment)
- [Prerequisites](#prerequisites)
- [Where to start?](#where-to-start)
- [Overview](#overview)
- [Function App Hosting Options](#function-app-hosting-options)
- [Function App: Configure/Validate the Environment variables](#function-app-configurevalidate-the-environment-variables)
- [Function App: Develop the logic](#function-app-develop-the-logic)
- [Test the solution](#test-the-solution)

</details>

> `How can you extract layout, text, visual, and other elements` from `PDFs` stored in an Azure Storage Account, process them using Azure AI services, and `store the results` in Cosmos DB for `further analysis?` This solution is `designed to accelerate the process` of building your own implementation. Please `feel free to use any of the provided reference.` I'm happy to contribute. Once this solution is deployed:
>
> 1. Upload your documents: Just `drop your PDFs or images into an Azure Storage container`and the system takes over from there. 
> 2. Automated intelligent processing: Behind the scenes, `Azure Functions orchestrates a powerful AI workflow`: 
>     - Document Intelligence pulls out tables, text, and form data
>     - AI Vision spots visual cues like checkmarks and highlights
>     - Azure OpenAI understands what the document actually means 
> 3. Centralized information management: `All extracted data is stored in Cosmos DB`, organized and accessible. The system `adapts to differents document layouts without requiring custom code for each format.`

> [!NOTE]
> Advantages of Document Intelligence for organizations handling with large volumes of documents: <br/>
>
> - Utilizes natural language processing, computer vision, deep learning, and machine learning. <br/>
> - Handles structured, semi-structured, and unstructured documents. <br/>
> - Automates the extraction and transformation of layout data into usable formats like JSON or CSV.

<div align="center">
  <img src="https://github.com/user-attachments/assets/322c8d9b-5ca3-4ba4-b0cd-ac14f198229e" alt="Centered Image" style="border: 2px solid #4CAF50; border-radius: 5px; padding: 5px;"/>
</div>

> [!NOTE]
> Azure Event Grid System Topics are free to create and manage, a System Topic is automatically created and managed by Azure for certain Azure services that emit events. It represents a source of events from an Azure resource (like a Storage Account, Key Vault, or Azure Maps). `You don't need to create or manage the topic yourself, Azure does it for you when you enable event publishing on a supported resource.` <br/>
>
> - Emits predefined event types (e.g., Microsoft.Storage.BlobCreated, Microsoft.Resources.ResourceWriteSuccess). <br/>
> - You can attach event handlers (like Azure Functions, Logic Apps, Webhooks) to respond to these events. <br/>
> - Works seamlessly with serverless architectures for real-time automation. <br/>
> For example:
> Suppose you have a Storage Account and want to trigger a function every time a new blob is uploaded: <br/>
> - Azure automatically creates a System Topic for the Storage Account.
> - You subscribe to the BlobCreated event.
> - When a blob is uploaded, Event Grid routes the event to your Azure Function.

<div align="center">
  <img src="https://github.com/user-attachments/assets/298ce8db-af28-487c-8126-9ba74986e8a5" alt="Centered Image" style="border: 2px solid #4CAF50; border-radius: 5px; padding: 5px;"/>
</div>

## Important Considerations for Production Environment

<details>
  <summary>Private Network Configuration</summary>

 > For enhanced security, consider configuring your Azure resources to operate within a private network. This can be achieved using Azure Virtual Network (VNet) to isolate your resources and control inbound and outbound traffic. Implementing private endpoints for services like Azure Blob Storage and Azure Functions can further secure your data by restricting access to your VNet.

</details>

<details>
  <summary>Security</summary>

  > Ensure that you implement appropriate security measures when deploying this solution in a production environment. This includes: <br/>
  >
  > - Securing Access: Use Azure Entra ID (formerly known as Azure Active Directory or Azure AD) for authentication and role-based access control (RBAC) to manage permissions. <br/>
  > - Managing Secrets: Store sensitive information such as connection strings and API keys in Azure Key Vault. <br/>
  > - Data Encryption: Enable encryption for data at rest and in transit to protect sensitive information.

</details>

<details>
  <summary>Scalability</summary>

  > While this example provides a basic setup, you may need to scale the resources based on your specific requirements. Azure services offer various scaling options to handle increased workloads. Consider using: <br/>
  >
  > - Auto-scaling: Configure auto-scaling for Azure Functions and other services to automatically adjust based on demand. <br/>
  > - Load Balancing: Use Azure Load Balancer or Application Gateway to distribute traffic and ensure high availability.

</details>

<details>
  <summary>Cost Management</summary>

  > Monitor and manage the costs associated with your Azure resources. Use Azure Cost Management and Billing to track usage and optimize resource allocation.

</details>

<details>
  <summary>Compliance</summary>

  > Ensure that your deployment complies with relevant regulations and standards. Use Azure Policy to enforce compliance and governance policies across your resources.
</details>

<details>
  <summary>Disaster Recovery</summary>
   
> Implement a disaster recovery plan to ensure business continuity in case of failures. Use Azure Site Recovery and backup solutions to protect your data and applications.

</details>

## Prerequisites

- An `Azure subscription is required`. All other resources, including instructions for creating a Resource Group, are provided in this workshop.
- `Contributor role assigned or any custom role that allows`: access to manage all resources, and the ability to deploy resources within subscription.
- If you choose to use the Terraform approach, please ensure that:
  - [Terraform is installed on your local machine](https://developer.hashicorp.com/terraform/tutorials/azure-get-started/install-cli#install-terraform).
  - [Install the Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) to work with both Terraform and Azure commands.

## Where to start? 

1. Please follow the [Terraform guide](./terraform-infrastructure/) to deploy the necessary Azure resources for the workshop.
2. Next, as this method `skips the creation of each resource` manually. Proceed with the configuration from [Configure/Validate the Environment variables](#function-app-configurevalidate-the-environment-variables).

> [!IMPORTANT]
> Regarding `Networking`, this example will cover `Public access configuration`, and `system-managed identity`. However, please ensure you `review your privacy requirements and adjust network and access settings as necessary for your specific case`.

## Overview 

> Using Cosmos DB provides you with a flexible, scalable, and globally distributed database solution that can handle both structured and semi-structured data efficiently. <br/>
>
> - `Azure Blob Storage`: Store the PDF invoices. <br/>
> - `Azure Functions`: Trigger on new PDF uploads, extract data, and process it. <br/>
> - `Azure SQL Database or Cosmos DB`: Store the extracted data for querying and analytics. <br/> 

| Resource                  | Recommendation                                                                                                      |
|---------------------------|----------------------------------------------------------------------------------------------------------------------|
| **Azure Blob Storage**    | Use for storing the PDF files. This keeps your file storage separate from your data storage, which is a common best practice. |
| **Azure SQL Database**    | Use if your data is highly structured and you need complex queries and transactions.                                  |
| **Azure Cosmos DB**       | Use if you need a globally distributed database with low latency and the ability to handle semi-structured data.      |

## Function App Hosting Options 

> In the context of Azure Function Apps, a `hosting option refers to the plan you choose to run your function app`. This choice affects how your function app is scaled, the resources available to each function app instance, and the support for advanced functionalities like virtual network connectivity and container support.

> [!TIP]  
>
> - `Scale to Zero`: Indicates whether the service can automatically scale down to zero instances when idle.  
>   - **IDLE** stands for:  
>     - **I** – Inactive  
>     - **D** – During  
>     - **L** – Low  
>     - **E** – Engagement  
>   - In other words, when the application is not actively handling requests or events (it's in a low-activity or paused state).
> - `Scale Behavior`: Describes how the service scales (e.g., `event-driven`, `dedicated`, or `containerized`).  
> - `Virtual Networking`: Whether the service supports integration with virtual networks for secure communication.  
> - `Dedicated Compute & Reserved Cold Start`: Availability of always-on compute to avoid cold starts and ensure low latency.  
> - `Max Scale Out (Instances)`: Maximum number of instances the service can scale out to.  
> - `Example AI Use Cases`: Real-world scenarios where each plan excels.

<details>
<summary><strong>Flex Consumption</strong></summary>

| Feature | Description |
|--------|-------------|
| **Scale to Zero** | `Yes` |
| **Scale Behavior** | `Fast event-driven` |
| **Virtual Networking** | `Optional` |
| **Dedicated Compute & Reserved Cold Start** | `Optional (Always Ready)` |
| **Max Scale Out (Instances)** | `1000` |
| **Example AI Use Cases** | `Real-time data processing` for AI models, `high-traffic AI-powered APIs`, `event-driven AI microservices`. Ideal for fraud detection, real-time recommendations, NLP, and computer vision services. |

</details>

<details>
<summary><strong>Consumption</strong></summary>

| Feature | Description |
|--------|-------------|
| **Scale to Zero** | `Yes` |
| **Scale Behavior** | `Event-driven` |
| **Virtual Networking** | `Optional` |
| **Dedicated Compute & Reserved Cold Start** | `No` |
| **Max Scale Out (Instances)** | `200` |
| **Example AI Use Cases** | `Lightweight AI APIs`, `scheduled AI tasks`, `low-traffic AI event processing`. Great for sentiment analysis, simple image recognition, and batch ML tasks. |

</details>

<details>
<summary><strong>Functions Premium</strong></summary>

| Feature | Description |
|--------|-------------|
| **Scale to Zero** | `No` |
| **Scale Behavior** | `Event-driven with premium options` |
| **Virtual Networking** | `Yes` |
| **Dedicated Compute & Reserved Cold Start** | `Yes` |
| **Max Scale Out (Instances)** | `100` |
| **Example AI Use Cases** | `Enterprise AI applications`, `low-latency AI APIs`, `VNet integration`. Ideal for secure, high-performance AI services like customer support and analytics. |

</details>

<details>
<summary><strong>App Service</strong></summary>

| Feature | Description |
|--------|-------------|
| **Scale to Zero** | `No` |
| **Scale Behavior** | `Dedicated VMs` |
| **Virtual Networking** | `Yes` |
| **Dedicated Compute & Reserved Cold Start** | `Yes` |
| **Max Scale Out (Instances)** | `Varies` |
| **Example AI Use Cases** | `AI-powered web applications`, `dedicated resources`. Great for chatbots, personalized content, and intensive AI inference. |

</details>

<details>
<summary><strong>Container Apps Env.</strong></summary>

| Feature | Description |
|--------|-------------|
| **Scale to Zero** | `No` |
| **Scale Behavior** | `Containerized microservices environment` |
| **Virtual Networking** | `Yes` |
| **Dedicated Compute & Reserved Cold Start** | `Yes` |
| **Max Scale Out (Instances)** | `Varies` |
| **Example AI Use Cases** | `AI microservices architecture`, `containerized AI workloads`, `complex AI workflows`. Ideal for orchestrating AI services like image processing, text analysis, and real-time analytics. |

</details>

## Function App: Configure/Validate the Environment variables

> [!IMPORTANT]
> `All environment variable names must exactly match between` your `Terraform deployment configuration` (in `main.tf`) and your `Function App environment settings`. Any mismatch will cause runtime failures when the application tries to access Azure resources.

> [!NOTE]
> This example is using system-assigned managed identity to assign RBACs (Role-based Access Control).

- Under `Settings`, go to `Environment variables`. And `+ Add` the following variables. For example:

  <img width="550" alt="image" src="https://github.com/user-attachments/assets/ec5d60f3-5136-489d-8796-474b7250865d">

- Click on `Apply` to save your configuration.
  
    <img width="550" alt="image" src="https://github.com/user-attachments/assets/437b44bb-7735-4d17-ae49-e211eca64887">

- Here are a few examples of how to get those values. `If a Terraform deployment template was used, these are linked automatically`, so please remember to review them.

  <img width="550" alt="image" src="https://github.com/user-attachments/assets/31d813e7-38ba-46ff-9e4b-d091ae02706a">
  
  <img width="550" alt="image" src="https://github.com/user-attachments/assets/45313857-b337-4231-9184-d2bb46e19267">
  
  <img width="550" alt="image" src="https://github.com/user-attachments/assets/074d2fa5-c64d-43bd-8ed7-af6da46d86a2">
  
> `These values depend on the specific you choose and deploy, like the AI models`, you can also adjust `LLM_MAX_TOKENS` based on your model's capabilities and `LLM_TEMPERATURE` based on your use case requirements.

- `FUNCTIONS_EXTENSION_VERSION`: `~4` 🡢 `Review the existence of this, if not create it`
- `WEBSITE_RUN_FROM_PACKAGE`: `1` 🡢 `Review the existence of this, if not create it`
- `FUNCTIONS_WORKER_RUNTIME`: `python` 🡢 `Review the existence of this, if not create it`
- `FUNCTIONS_NODE_BLOCK_ON_ENTRY_POINT_ERROR`: `true` (This setting ensures that all entry point errors are visible in your application insights logs) 🡢 `Review the existence of this, if not create it`
- `COSMOS_DB_ENDPOINT`: Your Cosmos DB account endpoint 🡢 `Review the existence of this, if not create it`
    
<details>
<summary><b> </b> Click to see more</summary>

- `COSMOS_DB_KEY`: Your Cosmos DB account key 🡢 `Review the existence of this, if not create it`
- `COSMOS_DB_CONNECTION_STRING`: Your Cosmos DB connection string 🡢 `Review the existence of this, if not create it`
- `invoicecontosostorage_STORAGE`: Your Storage Account connection string 🡢 `Review the existence of this, if not create it`
- `FORM_RECOGNIZER_ENDPOINT`: For example: `https://<your-form-recognizer-endpoint>.cognitiveservices.azure.com/` 🡢 `Review the existence of this, if not create it`
- `FORM_RECOGNIZER_KEY`: Your Document Intelligence Key (Form Recognizer) 🡢 `Review the existence of this, if not create it`
- `APPINSIGHTS_INSTRUMENTATIONKEY`: Your Application Insights instrumentation key 🡢 `Review the existence of this, if not create it`
- `APPLICATIONINSIGHTS_CONNECTION_STRING`: Your Application Insights connection string 🡢 `Review the existence of this, if not create it`
- `VISION_API_ENDPOINT`: Your Azure AI Vision endpoint for visual cue detection 🡢 `Review the existence of this, if not create it`
- `VISION_API_KEY`: Your Azure AI Vision API key 🡢 `Review the existence of this, if not create it`
- `VISION_API_VERSION`: `2024-02-01` (Latest stable API version) 🡢 `Review the existence of this, if not create it`.  These values depend on the specific you choose and deploy
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI service endpoint 🡢 `Review the existence of this, if not create it`
- `AZURE_OPENAI_KEY`: Your Azure OpenAI API key 🡢 `Review the existence of this, if not create it`
- `AZURE_OPENAI_API_VERSION`: e.g `2025-04-14`  🡢 `Review the existence of this, if not create it`. These values depend on the specific you choose and deploy
- `AZURE_OPENAI_GPT4_DEPLOYMENT`: Your e.g GPT-4 deployment name for complex reasoning and analysis 🡢 `Review the existence of this, if not create it`. These values depend on the specific you choose and deploy
- `AZURE_OPENAI_GPT4O_DEPLOYMENT`: Your e.g GPT-4o deployment name for advanced multimodal processing 🡢 `Review the existence of this, if not create it`. These values depend on the specific you choose and deploy
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`: Your text embedding deployment name for semantic search 🡢 `Review the existence of this, if not create it`
- `AI_HUB_NAME`: Your AI Studio Hub name for model management 🡢 `Review the existence of this, if not create it`
- `AI_PROJECT_NAME`: Your AI Studio Project name 🡢 `Review the existence of this, if not create it`
- `AI_HUB_WORKSPACE_URL`: Your AI Hub workspace URL 🡢 `Review the existence of this, if not create it`
- `AI_PROJECT_WORKSPACE_URL`: Your AI Project workspace URL 🡢 `Review the existence of this, if not create it`
- `AI_STORAGE_ACCOUNT_NAME`: Your AI storage account name for model artifacts 🡢 `Review the existence of this, if not create it`
- `AI_STORAGE_CONNECTION`: Your AI storage connection string 🡢 `Review the existence of this, if not create it`
- `ENABLE_LLM_PROCESSING`: `true` (Enable LLM-powered PDF processing features) 🡢 `Review the existence of this, if not create it`
- `LLM_MAX_TOKENS`: `4000` (Maximum tokens per request - adjust based on your model choice) 🡢 `Review the existence of this, if not create it`
- `LLM_TEMPERATURE`: `0.1` (Low temperature for consistent extraction - adjust based on use case) 🡢 `Review the existence of this, if not create it`
- `LLM_TIMEOUT_SECONDS`: `120` (Timeout for LLM requests - may need adjustment depending on model response time) 🡢 `Review the existence of this, if not create it`

</details>
  
## Function App: Develop the logic

- You need to install [VSCode](https://code.visualstudio.com/download)
- Install python from Microsoft store:
    
     <img width="550" alt="image" src="https://github.com/user-attachments/assets/30f00c27-da0d-400f-9b98-817fd3e03b1c">

- Open VSCode, and install some extensions: `python`, and `Azure Tools`.

     <img width="550" alt="image" src="https://github.com/user-attachments/assets/715449d3-1a36-4764-9b07-99421fb1c834">

     <img width="550" alt="image" src="https://github.com/user-attachments/assets/854aa665-dc2f-4cbf-bae2-2dc0a8ef6e46">

- Click on the `Azure` icon, and `sign in` into your account. Allow the extension `Azure Resources` to sign in using Microsoft, it will open a browser window. After doing so, you will be able to see your subscription and resources.

    <img width="550" alt="image" src="https://github.com/user-attachments/assets/4824ca1c-4959-4242-95af-ad7273c5530d">

- Under Workspace, click on `Create Function Project`, and choose a path in your local computer to develop your function.

    <img width="550" alt="image" src="https://github.com/user-attachments/assets/2c42d19e-be8b-48ef-a7e4-8a39989cea5a">

- Choose the language, in this case is `python`:

   <img width="550" alt="image" src="https://github.com/user-attachments/assets/2fb19a1e-bb2d-47e5-a56e-8dc8a708647a">

- Select the model version, for this example let's use `v2`:
  
   <img width="550" alt="image" src="https://github.com/user-attachments/assets/fd46ee93-d788-463d-8b28-dbf2487e9a7f">

- For the python interpreter, let's use the one installed via `Microsoft Store`:

   <img width="550" alt="image" src="https://github.com/user-attachments/assets/3605c959-fc59-461f-9e8d-01a6a92004a8">

- Choose a template (e.g., **Blob trigger**) and configure it to trigger on new PDF uploads in your Blob container.

   <img width="550" alt="image" src="https://github.com/user-attachments/assets/0a4ed541-a693-485c-b6ca-7d5fb55a61d2">

- Provide a function name, like `BlobTriggerPDFsMultiLayoutsDocIntelligence`:

   <img width="550" alt="image" src="https://github.com/user-attachments/assets/263cef5c-4460-46cb-8899-fb609b191d81">

- Next, it will prompt you for the path of the blob container where you expect the function to be triggered after a file is uploaded. In this case is `pdfinvoices` as was previously created.

  <img width="550" alt="image" src="https://github.com/user-attachments/assets/7005dc44-ffe2-442b-8373-554b229b3042">

- Click on `Create new local app settings`, and then choose your subscription.

  <img width="550" alt="image" src="https://github.com/user-attachments/assets/07c211d6-eda0-442b-b428-cdaed2bf12ac">

- Choose `Azure Storage Account for remote storage`, and select one. I'll be using the `invoicecontosostorage`. 

  <img width="550" alt="image" src="https://github.com/user-attachments/assets/3b5865fc-3e84-4582-8f06-cb5675d393f0">

- Then click on `Open in the current window`. You will see something like this:

  <img width="550" alt="image" src="https://github.com/user-attachments/assets/f30e8e10-0c37-4efc-8158-c83faf22a7d8">

- Now we need to update the function code to extract data from PDFs and store it in Cosmos DB, use this an example:

  > 1. **PDF Upload**: A PDF file is uploaded to the Azure Blob Storage container (`pdfinvoices`).
  > 2. **Trigger Azure Function**: The upload triggers the Azure Function `BlobTriggerPDFsMultiLayoutsAIDocIntelligence`.
  > 3. **Initialize Clients**: Sets up connections to Azure Document Intelligence, AI Vision, OpenAI, and Cosmos DB.  
  >    - Initializes the `DocumentAnalysisClient` using the `FORM_RECOGNIZER_ENDPOINT` and `FORM_RECOGNIZER_KEY` environment variables.  
  >    - Initializes the `AzureOpenAI` client for LLM analysis using OpenAI deployment details.
  >    - Configures the Vision API for visual cue detection.
  >    - Sets up the `CosmosClient` for data storage.
  > 4. **Read PDF from Blob Storage**: Reads the PDF content from the blob into a byte stream.
  > 5. **Analyze PDF**: Uses Azure Document Intelligence to analyze the layout of the PDF.  
  >    - Calls `begin_analyze_document` with the `prebuilt-layout` model.  
  >    - Waits for the analysis to complete and retrieves the layout result.
  > 6. **Extract Layout Data**: Parses and structures the layout data from the analysis result.  
  >    - Extracts lines, tables, and selection marks from each page.  
  >    - Identifies visual selection cues using AI Vision for enhanced form recognition.
  >    - Logs styles (e.g., handwritten content) and organizes data into a structured dictionary.
  > 7. **Enhance with AI Vision**: Analyzes visual elements for additional insights.
  >    - Detects and processes visual selection cues that Document Intelligence might miss.
  >    - Combines visual analysis with document structure understanding.
  > 8. **Apply LLM Analysis**: Uses Azure OpenAI for semantic understanding of document content.
  >    - Prepares structured content for the LLM with meaningful context.
  >    - Analyzes content relationships and extracts high-level insights.
  > 9. **Save Data to Cosmos DB**: Saves the structured layout data to Cosmos DB.  
  >    - Ensures the database (`DocumentAnalysisDB`) and container (`ProcessedDocuments`) exist or creates them.  
  >    - Prepares document for storage with metadata and timestamps.
  >    - Inserts or updates the layout data using `upsert_item`.
  > 10. **Logging (Process and Errors)**: Logs each step of the process, including success messages and detailed error handling for debugging and monitoring.
  >     - Uses structured logging for better traceability.
  >     - Includes processing time metrics for performance analysis.
  >     - Provides comprehensive error handling with meaningful diagnostics.

  - Update the function_app.py, for example [see the code used in this demo](./src/function_app.py):

      | Template Blob Trigger | Function Code updated |
      | --- | --- |
      |   <img width="550" alt="image" src="https://github.com/user-attachments/assets/07a7b285-eed2-4b42-bb1f-e41e8eafd273"> |  <img width="550" alt="image" src="https://github.com/user-attachments/assets/d364591b-817e-4f36-8c50-7de187c32a1e">|

  - Now, let's update the `requirements.txt`, [see the code used in this demo](./src/requirements.txt):

    | Template `requirements.txt` | Updated `requirements.txt` |
    | --- | --- |
    | <img width="550" alt="image" src="https://github.com/user-attachments/assets/239516e0-a4b7-4e38-8c2b-9be12ebb00de"> | <img width="550" alt="image" src="https://github.com/user-attachments/assets/91bd6bd8-ec21-4e1a-ae86-df577d37bcbb">| 

  - Since this function has already been tested, you can deploy your code to the function app in your subscription. If you want to test, you can use run your function locally for testing.
    - Click on the `Azure` icon.
    - Under `workspace`, click on the `Function App` icon.
    - Click on `Deploy to Azure`.

         <img width="550" alt="image" src="https://github.com/user-attachments/assets/12405c04-fa43-4f09-817d-f6879fbff035">

    - Select your `subscription`, your `function app`, and accept the prompt to overwrite:

         <img width="550" alt="image" src="https://github.com/user-attachments/assets/b69212a5-ab79-45e2-8344-73198b231d07">

    - After completing, you see the status in your terminal:

         <img width="550" alt="image" src="https://github.com/user-attachments/assets/6214e246-5beb-4ae4-a54b-9101cac3e241">

         <img width="550" alt="image" src="https://github.com/user-attachments/assets/78aab42c-af43-43aa-a4c0-545f4445755b">

> [!IMPORTANT]
> If you need further assistance with the code, please click [here to view all the function code](./src/).

> [!NOTE]
> Please ensure that all specified roles are assigned to the Function App. The provided example used `System assigned` for the Function App to facilitate the role assignment.

## Test the solution

> [!IMPORTANT]
> Please ensure that the user/system admin responsible for uploading the PDFs to the blob container has the necessary permissions. The error below illustrates what might occur if these roles are missing. <br/> 
> <img width="550" alt="image" src="https://github.com/user-attachments/assets/d827775a-d419-467e-9b2d-35cb05bc0f8a"> <br/>
> In that case, go to `Access Control (IAM)`, click on `+ Add`, and `Add role assignment`: <br/>
> <img width="550" alt="image" src="https://github.com/user-attachments/assets/aa4deff1-b6e1-49ec-9395-831ce2f982f5"> <br/>
> Search for `Storage Blob Data Contributor`, click `Next`. <br/>
> <img width="550" alt="image" src="https://github.com/user-attachments/assets/1fd40ef8-53f7-42df-a263-5bc3c80e61ba"> <br/>
> Then, click on `select members` and search for your user/systen admin. Finally click on `Review + assign`.

> Upload sample PDF invoices to the Blob container and verify that data is correctly ingested and stored in Cosmos DB.

- Click on `Upload`, then select `Browse for files` and choose your PDF invoices to be stored in the blob container, which will trigger the function app to parse them.

   <img width="950" alt="image" src="https://github.com/user-attachments/assets/a8456461-400b-4c68-b3d3-ac0b1630374d">

- Check the logs, and traces from your function with `Application Insights`:

   <img width="550" alt="image" src="https://github.com/user-attachments/assets/d499580a-76cb-4b4f-bb36-fd60c563a91c">

- Under `Investigate`, click on `Performance`. Filter by time range, and `drill into the samples`. Sort the results by date (if you have many, like in my case) and click on the last one.

   <img width="550" alt="image" src="https://github.com/user-attachments/assets/e266131c-e46f-4848-96ed-db2c04c5c18f">

- Click on `View all`:

   <img width="550" alt="image" src="https://github.com/user-attachments/assets/19356900-00c8-43ca-b888-fe493b25f258">

- Check all the logs, and traces generated. Also review the information parsed:

  <img width="550" alt="image" src="https://github.com/user-attachments/assets/2f28cc69-d389-4ef6-9209-57f76c9a09aa" />

- Validate that the information was uploaded to the Cosmos DB. Under `Data Explorer`, check your `Database`.

   <img width="550" alt="image" src="https://github.com/user-attachments/assets/27309a6d-c654-4c76-bbc1-990a9338973c">

<!-- START BADGE -->
<div align="center">
  <img src="https://img.shields.io/badge/Total%20views-1787-limegreen" alt="Total views">
  <p>Refresh Date: 2025-08-04</p>
</div>
<!-- END BADGE -->
