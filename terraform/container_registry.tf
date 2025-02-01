resource "azurerm_container_registry" "azure_container_registry" {
  name                = "404LostAndFoundRegistry"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Standard"
}

// to login to the registry it is as simple as docker login myregistry.azurecr.io, then you can tag and push the image to the registry
