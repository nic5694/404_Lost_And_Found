resource "azurerm_cognitive_account" "AiVision404LostAndFound" {
  name                  = "VisionAI404LostAndFound"
  location              = "eastus"
  resource_group_name   = azurerm_resource_group.rg.name
  kind                  = "ComputerVision"
  sku_name              = "S1"
  custom_subdomain_name = "404LostAndFoundVision"
  network_acls {
    default_action = "Allow"
    ip_rules       = []
  }
}
