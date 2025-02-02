
resource "azurerm_monitor_action_group" "consumption_action_group" {
  name                = "action_group"
  resource_group_name = azurerm_resource_group.rg.name
  short_name          = "ag404"
}

resource "azurerm_consumption_budget_resource_group" "resource_group_consumption_budget" {
  name              = "404ressourcegroupconsumptionbudget"
  resource_group_id = azurerm_resource_group.rg.id

  amount     = 50
  time_grain = "Monthly"

  time_period {
    start_date = "2025-02-01T00:00:00Z"
    end_date   = "2025-03-01T00:00:00Z"
  }

  notification {
    enabled        = true
    threshold      = 50.0
    operator       = "EqualTo"
    threshold_type = "Forecasted"

    contact_emails = var.action_members_emails

    contact_groups = [
      azurerm_monitor_action_group.consumption_action_group.id
    ]

    contact_roles = [
      "Owner",
    ]
  }

  notification {
    enabled        = true
    threshold      = 100.0
    operator       = "GreaterThan"
    contact_emails = var.action_members_emails
    contact_groups = [
      azurerm_monitor_action_group.consumption_action_group.id
    ]
  }
}
