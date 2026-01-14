# GitHub Automation Workflow - Quick Start Guide

This guide will help you set up and use the GitHub automation workflow integrated with Jules and Conductor.

## Prerequisites

✅ GitHub CLI (`gh`) installed and authenticated
✅ Gemini CLI with Jules extension installed
✅ MCP Vault server running on dell-brain
✅ Admin access to `samtheloanman/unified-cmtg` repository

## Setup Steps

### 1. Verify Prerequisites

```bash
cd .github/scripts
./verify-github-app.sh
```

### 2. Create GitHub App

The GitHub App allows the workflows to authenticate and interact with your repository.

```bash
./setup-github-app.sh
```

Follow the instructions to:
1. Create the app via GitHub's web interface
2. Save credentials to MCP Vault
3. Install the app on your repository

### 3. Update MCP Vault Secrets

Edit `/home/samalabam/code/custom-cmre-mcp/config/secrets.json`:

```json
{
  "github": {
    "app_id": "YOUR_APP_ID",
    "installation_id": "YOUR_INSTALLATION_ID",
    "private_key_path": "/app/config/github-app-key.pem",
    "webhook_secret": "GENERATED_SECRET",
    "personal_token": "gho_****"
  },
  "jules": {
    "api_endpoint": "https://jules.google.com/api/v1",
    "auth_token": "optional_if_using_gemini_cli_extension"
  }
}
```

Copy the GitHub App private key:
```bash
cp ~/Downloads/*.private-key.pem /home/samalabam/code/custom-cmre-mcp/config/github-app-key.pem
```

### 4. Restart MCP Vault

```bash
cd /home/samalabam/code/custom-cmre-mcp
docker-compose down
docker-compose build
docker-compose up -d
docker logs -f mcp-vault
```

### 5. Install Self-Hosted Runner

```bash
cd .github/scripts
./setup-runner.sh
```

This will:
- Download GitHub Actions runner
- Configure it for your repository
- Install as a systemd service
- Start the runner automatically

### 6. Verify Runner Registration

Check that the runner appears in GitHub:
```bash
gh api /repos/samtheloanman/unified-cmtg/actions/runners
```

Or visit: https://github.com/samtheloanman/unified-cmtg/settings/actions/runners

## Usage

### Conductor Task Automation

**Trigger**: Label an issue with `conductor`

```bash
# Create an issue and label it
gh issue create \
  --title "Implement feature X" \
  --body "Description of feature" \
  --label "conductor"
```

**What happens**:
1. Workflow detects the label
2. Adds task to `conductor/tasks.md`
3. Comments on the issue confirming task added

**Mark complete**: Edit `conductor/tasks.md` and change `[ ]` to `[x]`

The bridge script (run automatically on push) will close the GitHub issue.

### Jules Task Delegation

**Option 1: Issue Comment**

Comment on any issue with:
```
/jules add unit tests for the authentication module
```

**What happens**:
1. Workflow detects `/jules` command
2. Executes Jules via Gemini CLI
3. Jules works asynchronously
4. Jules creates a PR when complete

**Option 2: Issue Label**

Label an issue with `jules`:

```bash
gh issue label 123 --add "jules"
```

**Option 3: Manual Workflow Dispatch**

Trigger Jules manually:
```bash
gh workflow run jules-pr-automation.yml \
  -f task_description="Refactor database migrations" \
  -f target_branch="main" \
  -f auto_merge="false"
```

Or via GitHub UI:
https://github.com/samtheloanman/unified-cmtg/actions/workflows/jules-pr-automation.yml

### Available Workflows

#### 1. Conductor Task Trigger
- **File**: `.github/workflows/conductor-task-trigger.yml`
- **Triggers**: Issue labels, comments, PR events
- **Purpose**: Sync GitHub issues with Conductor tasks

#### 2. Jules PR Automation
- **File**: `.github/workflows/jules-pr-automation.yml`
- **Trigger**: Manual workflow dispatch
- **Purpose**: Execute Jules tasks and create PRs

## MCP Vault Tools

The enhanced MCP Vault provides these tools for workflows:

### `get_github_app_token()`
Generates a JWT for GitHub App authentication

### `get_jules_config()`
Retrieves Jules API configuration

### `get_github_webhook_secret()`
Gets webhook validation secret

## Monitoring

### Check Runner Status
```bash
sudo systemctl status actions.runner.samtheloanman-unified-cmtg.dell-brain-conductor.service
```

### View Runner Logs
```bash
journalctl -u actions.runner.samtheloanman-unified-cmtg.dell-brain-conductor.service -f
```

### Check Workflow Runs
```bash
gh run list --limit 10
```

### View MCP Vault Logs
```bash
cd /home/samalabam/code/custom-cmre-mcp
docker logs -f mcp-vault
```

## Troubleshooting

### Runner not starting
1. Check runner token is valid: `cd ~/actions-runner && ./run.sh`
2. Regenerate token: `gh api /repos/OWNER/REPO/actions/runners/registration-token`
3. Rerun configuration: `./config.sh --url ... --token ...`

### MCP Vault not accessible
1. Check Docker container: `docker ps | grep mcp-vault`
2. Test endpoint: `curl http://localhost:8888/sse`
3. Rebuild: `cd /home/samalabam/code/custom-cmre-mcp && docker-compose up --build -d`

### Workflows not triggering
1. Check runner labels match workflow requirements
2. Verify GitHub App permissions
3. Check workflow file syntax: `gh workflow view conductor-task-trigger.yml`

## Security Best Practices

- ✅ Secrets stored in MCP Vault, not in repository
- ✅ Runner runs locally on dell-brain (secrets don't leave network)
- ✅ GitHub App uses minimal required permissions
- ✅ Webhook validation using secret signatures
- ✅ Short-lived tokens (JWT expires in 10 minutes)

## Next Steps

1. Test the automation by creating a test issue
2. Monitor workflow runs
3. Customize workflows for your specific needs
4. Set up GitHub Environments for production protection
5. Add more automation patterns as needed

## Support

- View implementation plan: `implementation_plan.md`
- Check capabilities: `capabilities_summary.md`
- Task checklist: `task.md`
