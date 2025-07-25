output "resource_group_name" {
  description = "The name of the resource group."
  value       = azurerm_resource_group.rg.name
}

output "storage_account_name" {
  description = "The name of the storage account"
  value       = azurerm_storage_account.storage.name
}

output "input_container_name" {
  description = "The name of the input container"
  value       = azurerm_storage_container.input_container.name
}

output "output_container_name" {
  description = "The name of the output container"
  value       = azurerm_storage_container.output_container.name
}

output "function_app_name" {
  description = "The name of the Linux Function App."
  value       = azurerm_linux_function_app.function_app.name
}

output "app_service_plan_name" {
  description = "The name of the Service Plan"
  value       = azurerm_service_plan.asp.name
}

output "app_insights_name" {
  description = "The name of the Application Insights instance"
  value       = azurerm_application_insights.appinsights.name
}

output "log_analytics_workspace_name" {
  description = "The name of the Log Analytics workspace"
  value       = azurerm_log_analytics_workspace.loganalytics.name
}

output "key_vault_name" {
  description = "The name of the Key Vault"
  value       = azurerm_key_vault.keyvault.name
}


output "cosmosdb_account_name" {
  description = "The name of the CosmosDB account."
  value       = azurerm_cosmosdb_account.cosmosdb.name
}

# Output the Form Recognizer name
output "form_recognizer_name" {
  value = azurerm_cognitive_account.form_recognizer.name
}

# Output the Form Recognizer endpoint
output "form_recognizer_endpoint" {
  value = azurerm_cognitive_account.form_recognizer.endpoint
}

# Azure OpenAI Outputs
output "openai_account_name" {
  description = "The name of the Azure OpenAI account"
  value       = azurerm_cognitive_account.openai.name
}

output "openai_endpoint" {
  description = "The endpoint URL for the Azure OpenAI service"
  value       = azurerm_cognitive_account.openai.endpoint
}

output "openai_resource_id" {
  description = "The resource ID of the Azure OpenAI account"
  value       = azurerm_cognitive_account.openai.id
}

# Model Deployment Outputs
output "gpt4_deployment_name" {
  description = "The name of the GPT-4 model deployment"
  value       = azurerm_cognitive_deployment.gpt4.name
}

output "gpt4o_deployment_name" {
  description = "The name of the GPT-4o model deployment"
  value       = azurerm_cognitive_deployment.gpt4o.name
}

output "text_embedding_deployment_name" {
  description = "The name of the text embedding model deployment"
  value       = azurerm_cognitive_deployment.text_embedding.name
}

# AI Studio Hub Outputs
output "ai_hub_name" {
  description = "The name of the AI Studio Hub"
  value       = azurerm_machine_learning_workspace.ai_hub.name
}

output "ai_hub_id" {
  description = "The resource ID of the AI Studio Hub"
  value       = azurerm_machine_learning_workspace.ai_hub.id
}

output "ai_hub_workspace_url" {
  description = "The workspace URL for the AI Studio Hub"
  value       = "https://ml.azure.com/workspaces/${azurerm_machine_learning_workspace.ai_hub.workspace_id}/computes?region=${azurerm_machine_learning_workspace.ai_hub.location}"
}

# AI Project Outputs  
output "ai_project_name" {
  description = "The name of the AI Studio Project"
  value       = azurerm_machine_learning_workspace.ai_project.name
}

output "ai_project_id" {
  description = "The resource ID of the AI Studio Project"
  value       = azurerm_machine_learning_workspace.ai_project.id
}

output "ai_project_workspace_url" {
  description = "The workspace URL for the AI Studio Project"
  value       = "https://ml.azure.com/workspaces/${azurerm_machine_learning_workspace.ai_project.workspace_id}/computes?region=${azurerm_machine_learning_workspace.ai_project.location}"
}

# AI Storage Outputs
output "ai_storage_account_name" {
  description = "The name of the AI storage account"
  value       = azurerm_storage_account.runtime.name
}

output "ai_storage_account_id" {
  description = "The resource ID of the AI storage account"
  value       = azurerm_storage_account.runtime.id
}

# Deployment Summary
output "ai_foundry_summary" {
  description = "Summary of deployed AI Foundry resources"
  value = {
    openai_account       = azurerm_cognitive_account.openai.name
    openai_endpoint      = azurerm_cognitive_account.openai.endpoint
    ai_hub               = azurerm_machine_learning_workspace.ai_hub.name
    ai_project           = azurerm_machine_learning_workspace.ai_project.name
    gpt4_deployment      = azurerm_cognitive_deployment.gpt4.name
    gpt4o_deployment     = azurerm_cognitive_deployment.gpt4o.name
    embedding_deployment = azurerm_cognitive_deployment.text_embedding.name
    ai_storage           = azurerm_storage_account.runtime.name
  }
}
