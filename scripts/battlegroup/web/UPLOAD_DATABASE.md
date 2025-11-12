# Database Upload Instructions for Render

## Option 1: Upload via Render Shell (Recommended)

1. Go to your Render dashboard: https://dashboard.render.com
2. Click on your service: `north-africa-toe-api`
3. Click the "Shell" tab in the left sidebar
4. This opens a web-based terminal connected to your running service

5. In the Shell, run these commands:
```bash
cd /opt/render/project/src/scripts/battlegroup/web/database
pwd  # Confirm you're in the database directory
ls -lh  # Check current contents
```

6. From your local machine, use `curl` to upload the database:
```bash
# On your local Windows machine (PowerShell or WSL):
cd D:\north-africa-toe-builder

# Option A: If you have SSH access to Render (requires paid plan)
scp database/master_database.db render-service:/opt/render/project/src/scripts/battlegroup/web/database/

# Option B: Use Render's file upload endpoint (if available)
# This requires Render API key
```

## Option 2: Use Render Disk + Manual Upload

Since the free tier doesn't support direct file uploads, we'll use a temporary upload endpoint:

1. Add a temporary upload endpoint to the Flask app (will remove after upload)
2. Deploy the updated app
3. Use curl to POST the database file
4. Remove the upload endpoint and redeploy

**This is the safest option for the free tier.**

## Option 3: Store Database in Git LFS (Git Large File Storage)

The database is 16MB, which is within GitHub's 50MB file limit but not ideal for git.

1. Install Git LFS: `git lfs install`
2. Track the database: `git lfs track "database/*.db"`
3. Commit and push:
```bash
git add .gitattributes database/master_database.db
git commit -m "Add database via Git LFS"
git push
```
4. Update `render.yaml` build command to copy from git:
```yaml
buildCommand: "cd scripts/battlegroup/web && pip install -r requirements.txt && mkdir -p database && cp ../../../database/master_database.db database/"
```

## Option 4: Use External Database Service

Convert SQLite to PostgreSQL (Render provides free PostgreSQL):

1. Create a PostgreSQL database on Render
2. Use `sqlite3` + `psycopg2` to migrate data
3. Update Flask app to use PostgreSQL instead of SQLite

**This is the most production-ready solution but requires code changes.**

## Recommended Approach: Option 2 (Temporary Upload Endpoint)

I'll create a temporary upload endpoint next.
