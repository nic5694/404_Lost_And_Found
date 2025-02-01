resource "azurerm_storage_account" "projectBlobStorageAccount" {
depends_on = [ azurerm_resource_group.rg ]
  name                     = "404lostandfoundacccount"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}
resource "azurerm_storage_container" "blobStorageContainer" {
    depends_on = [ azurerm_resource_group.rg, azurerm_storage_account.projectBlobStorageAccount ]
  name                  = "lostitemcontainer"
  storage_account_id    = azurerm_storage_account.projectBlobStorageAccount.id
  container_access_type = "blob"
}

