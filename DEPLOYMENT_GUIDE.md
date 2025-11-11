# Deployment Guide - Phase 9B Web Integration

Complete deployment guide for the North Africa TO&E Builder web interface (landing page + Flask REST API + interactive tools).

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [GitHub Pages Deployment (Static Site)](#github-pages-deployment)
3. [Flask API Deployment Options](#flask-api-deployment)
4. [Railway.app Deployment (Recommended)](#railwayapp-deployment)
5. [PythonAnywhere Deployment (Alternative)](#pythonanywhere-deployment)
6. [Local Development](#local-development)
7. [CORS Configuration](#cors-configuration)
8. [Environment Variables](#environment-variables)
9. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Architecture Overview

**Two-Tier Deployment**:

1. **Static Frontend** (GitHub Pages):
   - `books/index.html` - Landing page with 12 battle books
   - `books/tools.html` - Interactive tools UI
   - All MDBook HTML files (12 books)
   - No server-side code, pure HTML/CSS/JavaScript

2. **Dynamic Backend** (Railway/PythonAnywhere):
   - `scripts/battlegroup/web/app.py` - Flask REST API
   - 11 API endpoints for scenarios, army lists, equipment search
   - SQLite database access
   - Python generator scripts

**Communication**: JavaScript in tools.html makes AJAX requests to Flask API (configured via CORS)

---

## GitHub Pages Deployment

### Step 1: Enable GitHub Pages

1. Go to your repository: `https://github.com/yourusername/north-africa-toe-builder`
2. Navigate to: **Settings** → **Pages**
3. Configure:
   - **Source**: Deploy from a branch
   - **Branch**: `main`
   - **Folder**: `/books`
4. Click **Save**

### Step 2: Wait for Deployment

- GitHub Actions will automatically build and deploy
- Check status in **Actions** tab
- Deployment typically takes 1-2 minutes

### Step 3: Access Your Site

- **URL**: `https://yourusername.github.io/north-africa-toe-builder/`
- **Landing Page**: `https://yourusername.github.io/north-africa-toe-builder/index.html`
- **Interactive Tools**: `https://yourusername.github.io/north-africa-toe-builder/tools.html`
- **Example Book**: `https://yourusername.github.io/north-africa-toe-builder/battleaxe/book/book/index.html`

### Step 4: Custom Domain (Optional)

1. Purchase domain (e.g., `northafricacampaign.com`)
2. Add CNAME record pointing to: `yourusername.github.io`
3. In GitHub Pages settings, add custom domain
4. Enable **Enforce HTTPS**

### Troubleshooting GitHub Pages

**Problem**: 404 errors for MDBook pages
- **Solution**: Ensure `books/` directory contains all 12 book subdirectories
- Check that each book has `book/book/index.html` structure

**Problem**: CSS not loading
- **Solution**: Use relative paths in HTML (already configured)
- Verify `index.html` is in `books/` root directory

**Problem**: Site not updating
- **Solution**: Check Actions tab for build errors
- Clear browser cache (Ctrl+Shift+R)
- Wait 5-10 minutes for CDN propagation

---

## Flask API Deployment

### Requirements

- Python 3.9+
- SQLite database: `database/master_database.db` (469 equipment items, 18 tables)
- Dependencies: Flask 3.0+, flask-cors 4.0+, SQLAlchemy 2.0+

### Deployment Options

1. **Railway.app** (Recommended) - Free tier, easy deployment, automatic HTTPS
2. **PythonAnywhere** (Alternative) - Free tier, manual setup, good for learning
3. **Heroku** (Not recommended) - No longer has free tier
4. **AWS/GCP/Azure** (Overkill) - Enterprise-grade, requires significant setup

---

## Railway.app Deployment

**Why Railway?**
- Free tier: 500 hours/month + $5 credit
- Automatic HTTPS
- Git-based deployment (push to deploy)
- Built-in logging and monitoring
- Support for SQLite databases

### Step 1: Create Railway Account

1. Go to: `https://railway.app`
2. Sign up with GitHub account
3. Authorize Railway to access your repository

### Step 2: Create New Project

1. Click **New Project**
2. Select **Deploy from GitHub repo**
3. Choose: `north-africa-toe-builder`
4. Railway will automatically detect Python project

### Step 3: Configure Project

1. Click **Settings** tab
2. **Root Directory**: Leave blank (Railway will detect)
3. **Start Command**:
   ```bash
   python scripts/battlegroup/web/app.py
   ```
4. **Environment Variables** (click **Variables** tab):
   ```
   FLASK_ENV=production
   PORT=5000
   CORS_ORIGINS=https://yourusername.github.io
   ```

### Step 4: Add Database File

Railway doesn't automatically include large binary files. Two options:

**Option A: Include in Git** (if < 50MB)
```bash
git lfs track "database/master_database.db"
git add .gitattributes database/master_database.db
git commit -m "Add database for Railway deployment"
git push origin main
```

**Option B: Upload via Railway CLI**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# Upload database
railway run python scripts/upload_db.py
```

### Step 5: Deploy

1. Railway will auto-deploy on every push to `main`
2. Check **Deployments** tab for build logs
3. Once deployed, Railway provides a URL: `https://your-project.railway.app`

### Step 6: Update Frontend

Edit `books/tools.html`, line 383:
```javascript
// Change from:
const API_URL = 'http://localhost:5000';

// To:
const API_URL = 'https://your-project.railway.app';
```

Commit and push:
```bash
git add books/tools.html
git commit -m "Update API URL for production"
git push origin main
```

### Step 7: Test API

```bash
# Health check
curl https://your-project.railway.app/api/health

# List endpoints
curl https://your-project.railway.app/api

# Test scenario generation
curl -X GET https://your-project.railway.app/api/scenarios/locations/1941q2
```

---

## PythonAnywhere Deployment

**Why PythonAnywhere?**
- Free tier: 1 web app + limited CPU
- Good for learning
- Web-based interface (no CLI required)

### Step 1: Create Account

1. Go to: `https://www.pythonanywhere.com`
2. Sign up for free account
3. Verify email

### Step 2: Upload Project Files

**Option A: Git Clone**
```bash
# In PythonAnywhere Bash console:
cd ~
git clone https://github.com/yourusername/north-africa-toe-builder.git
cd north-africa-toe-builder
```

**Option B: Upload via Web**
1. Go to **Files** tab
2. Create directory: `north-africa-toe-builder`
3. Upload files manually (tedious, not recommended)

### Step 3: Create Virtual Environment

```bash
cd ~/north-africa-toe-builder
python3.9 -m venv venv
source venv/bin/activate
pip install -r scripts/battlegroup/web/requirements.txt
```

### Step 4: Configure Web App

1. Go to **Web** tab
2. Click **Add a new web app**
3. Choose **Manual configuration**
4. Python version: **3.9**
5. **Source code**: `/home/yourusername/north-africa-toe-builder`
6. **Working directory**: `/home/yourusername/north-africa-toe-builder`
7. **Virtual env**: `/home/yourusername/north-africa-toe-builder/venv`

### Step 5: Configure WSGI File

Edit `/var/www/yourusername_pythonanywhere_com_wsgi.py`:

```python
import sys
import os

# Add project directory
project_home = '/home/yourusername/north-africa-toe-builder'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['CORS_ORIGINS'] = 'https://yourusername.github.io'

# Import Flask app
from scripts.battlegroup.web.app import create_app
application = create_app('production')
```

### Step 6: Database Configuration

Ensure `database/master_database.db` is in the correct location:
```bash
cd ~/north-africa-toe-builder
ls -lh database/master_database.db
# Should show file size (e.g., 15MB)
```

### Step 7: Start Web App

1. Go back to **Web** tab
2. Click **Reload** button (green)
3. Your API will be available at: `https://yourusername.pythonanywhere.com`

### Step 8: Update Frontend

Edit `books/tools.html`:
```javascript
const API_URL = 'https://yourusername.pythonanywhere.com';
```

### Limitations of PythonAnywhere Free Tier

- No HTTPS for custom domains (only `*.pythonanywhere.com`)
- Limited CPU seconds per day
- Daily scheduled task (web app goes to sleep after inactivity)
- Cannot access external APIs (firewall restrictions)

---

## Local Development

### Setup

1. **Install Dependencies**:
   ```bash
   cd scripts/battlegroup/web
   pip install -r requirements.txt
   ```

2. **Verify Database**:
   ```bash
   sqlite3 database/master_database.db "SELECT COUNT(*) FROM equipment;"
   # Should return: 469
   ```

3. **Start Flask Server**:
   ```bash
   cd scripts/battlegroup/web
   python app.py
   ```
   Output:
   ```
   Starting North Africa TO&E Builder API
   Environment: development
   URL: http://0.0.0.0:5000
   API Info: http://0.0.0.0:5000/api
   * Running on http://127.0.0.1:5000
   ```

4. **Test API**:
   ```bash
   # In another terminal:
   curl http://localhost:5000/api/health
   ```

5. **Open Tools UI**:
   - Open `books/tools.html` in browser
   - API Status should show: **Online**
   - Try generating a random scenario

### Development Workflow

1. Make changes to `app.py` or service files
2. Flask auto-reloads in debug mode (no restart needed)
3. Refresh `tools.html` in browser
4. Check Flask console for errors
5. Commit changes when satisfied

---

## CORS Configuration

**What is CORS?**
Cross-Origin Resource Sharing allows JavaScript from GitHub Pages (`https://yourusername.github.io`) to make API requests to Flask backend (`https://your-project.railway.app`).

### Development CORS (Current)

`config.py` - DevelopmentConfig:
```python
CORS_ORIGINS = ["*"]  # Allow all origins
```

### Production CORS (Required for Deployment)

`config.py` - ProductionConfig:
```python
CORS_ORIGINS = [
    "https://yourusername.github.io",
    "https://yourusername.github.io/*"
]
```

### Update CORS for Your Domain

1. **Edit `scripts/battlegroup/web/config.py`**:
   ```python
   class ProductionConfig(Config):
       CORS_ORIGINS = [
           os.getenv("GITHUB_PAGES_URL", "https://yourusername.github.io"),
           "https://yourusername.github.io"
       ]
   ```

2. **Set Environment Variable** (Railway/PythonAnywhere):
   ```bash
   GITHUB_PAGES_URL=https://yourusername.github.io
   ```

3. **Test CORS**:
   ```bash
   curl -H "Origin: https://yourusername.github.io" \
        -H "Access-Control-Request-Method: POST" \
        -X OPTIONS https://your-project.railway.app/api/scenarios/random
   ```
   Should return `Access-Control-Allow-Origin` header.

---

## Environment Variables

### Required Variables

| Variable | Description | Development | Production |
|----------|-------------|-------------|------------|
| `FLASK_ENV` | Environment mode | `development` | `production` |
| `PORT` | Server port | `5000` | `5000` (Railway auto-detects) |
| `CORS_ORIGINS` | Allowed origins | `*` | `https://yourusername.github.io` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_PATH` | SQLite database path | `database/master_database.db` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Setting Environment Variables

**Railway**:
1. Go to project → **Variables** tab
2. Add key-value pairs
3. Click **Add** and **Deploy**

**PythonAnywhere**:
1. Edit WSGI file (see Step 5 above)
2. Add `os.environ[' KEY'] = 'value'`
3. Reload web app

**Local**:
```bash
export FLASK_ENV=development
export CORS_ORIGINS="*"
python app.py
```

---

## Monitoring & Maintenance

### Health Checks

**API Health**:
```bash
curl https://your-project.railway.app/api/health
# Response: {"status": "healthy", "api_version": "1.0.0", "service": "North Africa TO&E Builder API"}
```

**Database Connection**:
```bash
curl https://your-project.railway.app/api/equipment/search?name=Panzer
# Should return equipment results
```

### Logs

**Railway**:
- Go to project → **Deployments** tab
- Click on latest deployment
- View real-time logs

**PythonAnywhere**:
- Go to **Web** tab
- Click **Log files** → **Error log**
- Check for Python exceptions

### Common Issues

**Problem**: API returns 500 errors
- **Check**: Flask logs for Python exceptions
- **Solution**: Verify database path, check service imports

**Problem**: CORS errors in browser console
- **Check**: Browser dev tools → Network tab
- **Solution**: Update `CORS_ORIGINS` in production config

**Problem**: Scenarios fail to generate
- **Check**: `ScenarioAutoGenerator` import paths
- **Solution**: Ensure all Phase 9B scripts are in correct directories

**Problem**: Equipment search returns 0 results
- **Check**: Database contains 469 items: `SELECT COUNT(*) FROM equipment;`
- **Solution**: Re-upload database file

### Performance Monitoring

**Railway**:
- Go to **Metrics** tab
- Monitor: CPU usage, memory, request count
- Free tier: 500 hours/month

**PythonAnywhere**:
- Go to **Web** tab
- Check **CPU seconds used today**
- Free tier: 100 seconds/day

### Database Backups

**Automated Backup Script**:
```bash
#!/bin/bash
# backup_db.sh
DATE=$(date +%Y%m%d)
cp database/master_database.db backups/master_database_$DATE.db
echo "Backup created: backups/master_database_$DATE.db"
```

Run weekly via cron or GitHub Actions.

---

## Quick Start Checklist

- [ ] **Phase 1**: Enable GitHub Pages from `books/` directory
- [ ] **Phase 2**: Create Railway.app account and link repository
- [ ] **Phase 3**: Configure Railway environment variables (FLASK_ENV, CORS_ORIGINS)
- [ ] **Phase 4**: Deploy Flask API to Railway (auto-deploy on push)
- [ ] **Phase 5**: Update `books/tools.html` with production API URL
- [ ] **Phase 6**: Test all 3 tools: Random Scenario, Historical Scenario, Equipment Search
- [ ] **Phase 7**: Configure production CORS in `config.py`
- [ ] **Phase 8**: Monitor logs for first 24 hours
- [ ] **Phase 9**: Set up weekly database backups
- [ ] **Phase 10**: Share URL with community for testing

---

## Support & Troubleshooting

**GitHub Issues**: https://github.com/yourusername/north-africa-toe-builder/issues

**Flask Documentation**: https://flask.palletsprojects.com/

**Railway Documentation**: https://docs.railway.app/

**GitHub Pages Documentation**: https://docs.github.com/en/pages

---

**Deployment Status**: Ready for production deployment (November 11, 2025)

**Next Steps**: Complete Phase 5a (GitHub Pages) and Phase 5b (Railway deployment)
