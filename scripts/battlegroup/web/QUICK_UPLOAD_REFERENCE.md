# Quick Database Upload Reference

## What I Just Did

1. ✅ Created `railway_app_with_upload.py` with secure database upload endpoint
2. ✅ Updated `render.yaml` to use upload version and configure persistent disk
3. ✅ Committed and pushed changes → Render will auto-redeploy

## What You Need To Do Now

### Step 1: Add Upload Token to Render (2 minutes)

1. Go to: https://dashboard.render.com
2. Click: `north-africa-toe-api`
3. Click: "Environment" tab
4. Click: "Add Environment Variable"
5. Enter:
   - **Key**: `UPLOAD_TOKEN`
   - **Value**: `temp-upload-token-remove-after-use`
6. Click: "Save Changes"
7. **Wait for redeploy to complete** (~2-3 minutes)

### Step 2: Upload Database (1 minute)

Once redeploy is done, run this from PowerShell:

```powershell
cd D:\north-africa-toe-builder

curl.exe -X POST `
  -H "X-Upload-Token: temp-upload-token-remove-after-use" `
  -F "database=@scripts/battlegroup/web/database/web_database.db" `
  https://north-africa-toe-api.onrender.com/api/admin/upload-database
```

**Expected Success Response:**
```json
{
  "status": "success",
  "message": "Database uploaded successfully",
  "size_mb": 6.58
}
```

### Step 3: Verify Database Works (30 seconds)

```powershell
# Check health
curl.exe https://north-africa-toe-api.onrender.com/api/health

# Should show: "database_exists": true

# Test equipment search
curl.exe "https://north-africa-toe-api.onrender.com/api/equipment/search?name=Panzer"

# Should return actual German tank data
```

### Step 4: Remove Upload Endpoint for Security (5 minutes)

**⚠️ CRITICAL - Do not skip this step!**

I'll help you remove the upload endpoint after we confirm database upload succeeded.

The steps are:
1. Edit `render.yaml` back to `python railway_app.py`
2. Remove `UPLOAD_TOKEN` from Render dashboard
3. Delete `railway_app_with_upload.py`
4. Commit and push

## Troubleshooting

### "Unauthorized" Error
→ Make sure you added `UPLOAD_TOKEN` to Render environment and redeployed

### "No such file" Error
→ Make sure you're in `D:\north-africa-toe-builder` directory

### Upload hangs or times out
→ Database file is 6.58MB, should take 5-15 seconds. If it hangs >1 minute, cancel and check Render logs

### "database_exists: false" after upload
→ Check Render logs for filesystem errors, may need to reconfigure disk

## Files Created

- `railway_app_with_upload.py` - Temporary Flask app with upload endpoint
- `DATABASE_UPLOAD_STEPS.md` - Detailed instructions with alternatives
- `UPLOAD_DATABASE.md` - Background info on upload options
- `QUICK_UPLOAD_REFERENCE.md` - This file (quick steps)

## Current Status

- ✅ Code pushed to GitHub
- ⏳ Render auto-deploying (check dashboard for progress)
- ⏳ You need to add UPLOAD_TOKEN to Render dashboard
- ⏳ Then upload database via curl
- ⏳ Then we'll remove the upload endpoint

**Let me know when Render finishes redeploying and I'll help you with the next steps!**
