output "resource_group_name" {
  value = azurerm_resource_group.rg.name
}

output "container_ipv4_address" {
  value = azurerm_container_group.container.ip_address
}