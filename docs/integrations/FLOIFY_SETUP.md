# Floify Integration Setup Guide

This guide explains how to configure Floify credentials from the custom-cmre-mcp server on dell-brain.

## Current Status

- ✅ Backend configured to use `FLOIFY_API_KEY` environment variable
- ✅ Docker Compose configured to load from `.env.local` file
- ✅ `.env.local` template created
- ⏳ **Action Required**: Get credentials from dell-brain

## Quick Setup (3 Steps)

### Step 1: SSH to dell-brain and get credentials

```bash
ssh dell-brain
cd /code/custom-cmre-mcp
cat secrets.json | python3 -m json.tool | grep -A 5 "floify\|FLOIFY"
```

### Step 2: Add credentials to local environment

Edit `unified-platform/backend/.env.local` and replace the placeholder:

```bash
# Change this:
FLOIFY_API_KEY=your-floify-api-key-here

# To the actual key from dell-brain:
FLOIFY_API_KEY=actual-key-from-secrets-json
```

### Step 3: Restart backend container

```bash
cd unified-platform
docker-compose restart backend
```

Verify it's working:
```bash
docker logs unified-platform-backend-1 | grep FLOIFY
# Should NOT show: "FLOIFY_API_KEY not found in environment"
```

## Architecture

### MCP Server Location
- **Server**: dell-brain (Dell Precision 7720)
- **Path**: `/code/custom-cmre-mcp/`
- **Secrets**: `/code/custom-cmre-mcp/secrets.json`

### Where Credentials Are Used

1. **Backend API** (`unified-platform/backend/api/integrations/floify.py`)
   - Creates prospects (leads) when users submit quote wizard
   - Fetches application data from Floify
   - Processes webhook events

2. **Environment Variable Flow**:
   ```
   .env.local → docker-compose.yml → backend container → Django settings → FloifyClient
   ```

## Testing Floify Integration

After adding credentials:

```bash
# Test health endpoint
curl http://localhost:8001/api/v1/health/

# Test lead submission endpoint
curl -X POST http://localhost:8001/api/v1/leads/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Test",
    "last_name": "User",
    "email": "test@example.com",
    "phone": "555-1234",
    "loan_amount": 500000
  }'
```

## Security Notes

⚠️ **Important:**
- `.env.local` is in `.gitignore` - **never commit credentials to git**
- Credentials should only be on dell-brain and local dev machines
- Production uses separate credentials (not in this file)

## Alternative: Connect MCP Server Directly (Future)

To avoid manual credential copying, configure Claude Code to connect to the dell-brain MCP server:

```json
// ~/.config/claude-code/mcp/servers/config.json
{
  "mcpServers": {
    "custom-cmre-mcp": {
      "command": "ssh",
      "args": ["dell-brain", "python", "/code/custom-cmre-mcp/server.py"],
      "env": {}
    }
  }
}
```

Then credentials can be fetched programmatically via MCP resources.

## Troubleshooting

### "FLOIFY_API_KEY not found in environment"
- Verify `.env.local` exists in `unified-platform/backend/`
- Check file has actual API key (not placeholder)
- Restart backend: `docker-compose restart backend`

### "Floify integration will be disabled"
- This is just a warning if key is missing
- Backend will work but lead submission won't connect to Floify

### Test credentials are valid
```bash
docker exec unified-platform-backend-1 python manage.py shell -c "
from django.conf import settings
print(f'FLOIFY_API_KEY configured: {bool(settings.FLOIFY_API_KEY)}')
print(f'Key length: {len(settings.FLOIFY_API_KEY) if settings.FLOIFY_API_KEY else 0}')
"
```

## Next Steps

After Floify is configured:
1. ✅ Test lead submission from quote wizard
2. ✅ Configure Floify webhook endpoint
3. ✅ Test application sync from Floify → backend
4. ✅ Phase F.8 complete!
