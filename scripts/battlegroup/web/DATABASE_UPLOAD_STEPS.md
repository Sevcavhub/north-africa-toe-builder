# Database Upload Steps for Render.com

## Step 1: Update Render Configuration

The `render.yaml` has been updated to use a persistent disk at `/opt/render/project/src/scripts/battlegroup/web/database`.

## Step 2: Deploy Upload-Enabled Version

We'll temporarily deploy a version with an upload endpoint, use it once to upload the database, then remove it.

### 2a. Update render.yaml startCommand

Edit `render.yaml` to use the upload-enabled version:

```yaml
startCommand: "cd scripts/battlegroup/web && python railway_app_with_upload.py"
```

### 2b. Add Upload Token Environment Variable in Render Dashboard

1. Go to https://dashboard.render.com
2. Click on `north-africa-toe-api`
3. Go to "Environment" tab
4. Add new environment variable:
   - Key: `UPLOAD_TOKEN`
   - Value: `temp-upload-token-remove-after-use`
5. Click "Save Changes" (this will trigger a redeploy)

## Step 3: Upload Database File

Once the service redeploys with the upload endpoint active, use curl to upload:

```bash
# From PowerShell or WSL in D:\north-africa-toe-builder
curl -X POST `
  -H "X-Upload-Token: temp-upload-token-remove-after-use" `
  -F "database=@database/master_database.db" `
  https://north-africa-toe-api.onrender.com/api/admin/upload-database
```

Expected response:
```json
{
  "status": "success",
  "message": "Database uploaded successfully",
  "path": "/opt/render/project/src/scripts/battlegroup/web/database/master_database.db",
  "size_bytes": 16777216,
  "size_mb": 16.0
}
```

## Step 4: Verify Database Upload

Check that the database is accessible:

```bash
curl https://north-africa-toe-api.onrender.com/api/health
```

Should return:
```json
{
  "status": "healthy",
  "database_exists": true,
  "upload_endpoint_active": true
}
```

Test equipment search:
```bash
curl "https://north-africa-toe-api.onrender.com/api/equipment/search?name=Panzer"
```

Should return actual equipment data.

## Step 5: Remove Upload Endpoint (SECURITY)

⚠️ **CRITICAL**: The upload endpoint is a security risk and must be removed after use.

### 5a. Update render.yaml

Change back to the standard version:

```yaml
startCommand: "cd scripts/battlegroup/web && python railway_app.py"
```

### 5b. Remove Upload Token

1. Go to Render dashboard → Environment
2. Delete the `UPLOAD_TOKEN` environment variable
3. Save changes (triggers redeploy)

### 5c. Delete Upload File

```bash
git rm scripts/battlegroup/web/railway_app_with_upload.py
git commit -m "Remove temporary upload endpoint after database initialization"
git push
```

## Step 6: Final Verification

After redeploying without the upload endpoint:

```bash
curl https://north-africa-toe-api.onrender.com/api/health
```

Should return:
```json
{
  "status": "healthy",
  "database_exists": true,
  "upload_endpoint_active": false  # or this field won't exist
}
```

```bash
curl "https://north-africa-toe-api.onrender.com/api/equipment/search?nation=german&category=tank"
```

Should return German tank data.

## Troubleshooting

### Upload fails with 401 Unauthorized
- Check that `UPLOAD_TOKEN` environment variable matches the header value
- Verify the service redeployed after adding the environment variable

### Upload fails with 413 Request Entity Too Large
- The database might be larger than the 50MB limit
- Check file size: `ls -lh database/master_database.db`
- If >50MB, we'll need to use a different approach (PostgreSQL migration)

### Database upload succeeds but API still returns database_exists: false
- The Render Disk might not be properly configured
- Check logs in Render dashboard for filesystem errors
- Verify mountPath matches the database path in railway_config.py

### API returns 500 errors after database upload
- Database file might be corrupted during upload
- Check Render logs for SQLite errors
- Try re-uploading the database

## Alternative: Git LFS (If Upload Endpoint Doesn't Work)

If the upload endpoint approach fails, we can use Git Large File Storage:

```bash
# Install Git LFS
git lfs install

# Track the database file
git lfs track "database/*.db"

# Commit
git add .gitattributes database/master_database.db
git commit -m "Add database via Git LFS"
git push

# Update render.yaml buildCommand to copy database
buildCommand: "cd scripts/battlegroup/web && pip install -r requirements.txt && mkdir -p database && cp ../../../database/master_database.db database/"
```

This makes the database part of the git repository and Render will automatically have access to it during builds.
