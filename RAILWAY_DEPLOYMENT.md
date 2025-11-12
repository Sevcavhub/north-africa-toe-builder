# Railway Deployment Guide

## ✅ Changes Made (Commit 8515e7e9)

Created isolated Flask deployment to avoid 22-minute timeout:

1. **railway_app.py** - Simplified Flask app without external dependencies
2. **railway_config.py** - Railway-specific configuration
3. **nixpacks.toml** - Updated to use Railway root directory approach

## 🚀 Railway Configuration Steps

### Step 1: Configure Root Directory

In your Railway project "brilliant-optimism":

1. Go to **Settings** tab
2. Scroll to **Build & Deploy** section
3. Find **Root Directory** setting
4. Set to: `scripts/battlegroup/web`
5. Click **Save**

This tells Railway to build from the Flask app directory only, avoiding the entire project.

### Step 2: Re-deploy

After saving Root Directory:

1. Go to **Deployments** tab
2. Click **Deploy** → **Trigger Deploy**
3. Railway will:
   - Install Python 3.13
   - Install Flask dependencies (5 packages only)
   - Run `python railway_app.py`
   - Should complete in **under 2 minutes**

### Step 3: Upload Database (After Successful Deploy)

The database file is too large for git, so upload via Railway dashboard:

1. After deployment succeeds, go to **Variables** tab
2. Note the deployment URL (e.g., `https://brilliant-optimism-production.up.railway.app`)
3. Test health check: `curl https://YOUR_URL/api/health`
   - Should show `"database_exists": false` initially
4. Upload database via Railway CLI or dashboard file upload:
   - File: `database/master_database.db`
   - Target path: `/app/database/master_database.db`

### Step 4: Verify Deployment

Test endpoints:

```bash
# Health check
curl https://YOUR_URL/api/health

# API info
curl https://YOUR_URL/api

# Equipment search
curl https://YOUR_URL/api/equipment/search?name=Panzer

# Specific equipment
curl https://YOUR_URL/api/equipment/1
```

Expected response for health check:
```json
{
  "status": "healthy",
  "api_version": "1.0.0",
  "service": "North Africa TO&E Builder API",
  "database_exists": true
}
```

## 🔧 Environment Variables (Optional)

Railway automatically sets:
- `PORT` - HTTP port (Railway manages this)
- `RAILWAY_ENVIRONMENT` - Set to "production"

No additional environment variables needed for basic deployment.

## 📊 Expected Build Time

- **Previous attempt**: 22 minutes → TIMEOUT (installing 250+ unnecessary packages)
- **With Root Directory**: **< 2 minutes** (only Flask dependencies)

## 🐛 Troubleshooting

### Build still timing out?
- Verify **Root Directory** is set to `scripts/battlegroup/web`
- Check Railway build logs for unexpected package installations
- Ensure `.railwayignore` is committed to git

### Database not found?
- Upload `database/master_database.db` via Railway dashboard
- Verify file path is `/app/database/master_database.db`
- Check `/api/health` endpoint for `database_exists` status

### CORS errors from GitHub Pages?
- Verify Railway URL is added to `railway_config.py` CORS_ORIGINS
- Check browser console for specific CORS error details
- Test API directly (should work) vs from GitHub Pages

## 🎯 Next Steps After Successful Deployment

1. Note Railway URL (e.g., `https://brilliant-optimism-production.up.railway.app`)
2. Update `books/tools.html` with production API URL
3. Test full stack: GitHub Pages → Railway API
4. Deploy updated tools.html to GitHub Pages

## 📝 Technical Details

**Root Directory Approach**:
- Railway builds from `scripts/battlegroup/web/` as project root
- `railway_app.py` uses local paths (not parent directory traversal)
- Database copied during build phase (or uploaded post-deploy)
- Only 5 Python packages installed (Flask, flask-cors, SQLAlchemy, python-dotenv, marshmallow)

**Why This Works**:
- Railway doesn't see Node.js files (they're in parent directories)
- No X11/GTK/font packages detected
- Clean, minimal Flask deployment
- Fast build times (< 2 minutes vs 22+ minute timeout)
