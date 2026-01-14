# Zapier Integration Guide

This project is integrated with our Zapier account via the Zapier MCP server, allowing for direct interaction with external services like Zoho, Floify, and LendingPad.

## Available Tools

The following is a non-exhaustive list of available Zapier tools that can be used in this project:

*   `zapier_zoho_create_lead`
*   `zapier_floify_get_application_status`
*   `zapier_lendingpad_create_contact`

For a full list of available tools, please refer to our Zapier account.

## Example Workflows

### Creating a New Zoho Lead

To create a new lead in Zoho CRM, you can use the following command:

> `create a new zoho lead with the name "John Doe" and email "john.doe@example.com"`

This will invoke the `zapier_zoho_create_lead` tool and create a new lead in Zoho CRM.

### Syncing Floify Applications to LendingPad

You can create a multi-step workflow to sync new Floify applications to LendingPad:

> "Get the latest new applications from Floify, and for each one, create a new contact in LendingPad."
