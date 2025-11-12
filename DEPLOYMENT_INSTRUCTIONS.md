# Deployment Instructions - Step-by-Step Guide

**Status**: Code is complete and pushed to GitHub. Now we need to deploy it.

Follow these steps in order to get your web integration live.

---

## Part 1: Deploy Static Site to GitHub Pages (5 minutes)

### Step 1.1: Enable GitHub Pages

1. Open your browser and go to:
   ```
   https://github.com/Sevcavhub/north-africa-toe-builder/settings/pages
   ```

2. Under **"Build and deployment"** section:
   - **Source**: Click dropdown and select **"GitHub Actions"**
   - (Do NOT select "Deploy from a branch" - we're using the workflow I created)

3. Click **Save** (if there's a save button)

4. The page should now show:
   ```
   Your site is ready to be published at https://sevcavhub.github.io/north-africa-toe-builder/
   ```

### Step 1.2: Verify Deployment

1. Go to the Actions tab:
   ```
   https://github.com/Sevcavhub/north-africa-toe-builder/actions
   ```

2. You should see a workflow named **"Deploy to GitHub Pages"** running

3. Wait 2-3 minutes for it to complete (it will show a green checkmark ✓)

4. Once complete, open your browser and test:
   ```
   https://sevcavhub.github.io/north-africa-toe-builder/
   ```

   You should see the landing page with 12 battle books!

### Step 1.3: Test the Landing Page

Click through a few book links to verify they work:
- https://sevcavhub.github.io/north-africa-toe-builder/battleaxe/book/book/index.html
- https://sevcavhub.github.io/north-africa-toe-builder/crusader/book/book/index.html

**✅ Checkpoint**: Landing page is live and accessible

---

## Part 2: Deploy Flask API to Railway.app (15-20 minutes)

### Step 2.1: Create Railway Account

1. Go to: https://railway.app

2. Click **"Login with GitHub"** button (top right)

3. Authorize Railway to access your GitHub account
   - You'll see a popup asking for permissions
   - Click **"Authorize Railway"**

4. You'll be redirected to Railway dashboard

### Step 2.2: Create New Project

1. On Railway dashboard, click **"+ New Project"** button

2. Select **"Deploy from GitHub repo"**

3. Find and select: **`Sevcavhub/north-africa-toe-builder`**
   - If you don't see it, click "Configure GitHub App" and grant access

4. Railway will automatically:
   - Detect it's a Python project
   - Start analyzing the repository
   - Show you a deployment screen

### Step 2.3: Configure Start Command

1. Click on your project (should say "north-africa-toe-builder")

2. Click the **"Settings"** tab

3. Scroll down to **"Deploy"** section

4. Find **"Start Command"** and enter:
   ```bash
   cd scripts/battlegroup/web && python app.py
   ```

5. Click outside the box to save (it auto-saves)

### Step 2.4: Set Environment Variables

1. Click the **"Variables"** tab (top of screen)

2. Click **"+ New Variable"** button

3. Add these three variables one by one:

   **Variable 1:**
   - Key: `FLASK_ENV`
   - Value: `production`

   **Variable 2:**
   - Key: `PORT`
   - Value: `5000`

   **Variable 3:**
   - Key: `CORS_ORIGINS`
   - Value: `https://sevcavhub.github.io`

4. After adding all three, Railway will auto-redeploy

### Step 2.5: Wait for Deployment

1. Click the **"Deployments"** tab

2. You'll see a deployment in progress (spinning icon)

3. Wait 3-5 minutes for build to complete

4. When complete, you'll see:
   - Green checkmark ✓
   - A URL like: `https://north-africa-toe-builder-production-xxxx.up.railway.app`

5. **COPY THIS URL** - you'll need it for the next step!

### Step 2.6: Test the API

1. Open your browser and go to your Railway URL + `/api/health`:
   ```
   https://your-project-name.up.railway.app/api/health
   ```

2. You should see:
   ```json
   {
     "status": "healthy",
     "api_version": "1.0.0",
     "service": "North Africa TO&E Builder API"
   }
   ```

3. Test the API endpoints:
   ```
   https://your-project-name.up.railway.app/api
   ```
   Should show list of all endpoints

**✅ Checkpoint**: Flask API is deployed and responding

---

## Part 3: Connect Frontend to Backend (YOU TELL ME THE URL)

### Step 3.1: Give Me Your Railway URL

**Copy your Railway deployment URL** and paste it in the chat. Tell me:

```
My Railway URL is: https://north-africa-toe-builder-production-xxxx.up.railway.app
```

I will then:
1. Update `books/tools.html` to point to your Railway API
2. Commit and push the change
3. GitHub Pages will auto-redeploy (2-3 minutes)

### Step 3.2: Test Full Integration

Once I've updated the URL and it's deployed:

1. Go to: https://sevcavhub.github.io/north-africa-toe-builder/

2. Click **"Launch Interactive Tools"** button

3. You should see **"API Status: Online"** (green indicator)

4. Test each tool:
   - **Random Scenario Generator**: Select 1000 points, German + British, 1941 Q2 → Generate
   - **Historical Scenario Generator**: Select battle → Generate
   - **Equipment Search**: Type "Panzer" → Search

**✅ Final Checkpoint**: Full stack is live and working!

---

## Troubleshooting

### GitHub Pages Issues

**Problem**: 404 error when accessing site
- **Solution**: Wait 5 minutes for DNS propagation, clear browser cache

**Problem**: Workflow failed in Actions tab
- **Solution**: Check error logs, ensure `books/` directory exists

### Railway Issues

**Problem**: Build fails with "No module named 'flask'"
- **Solution**: Verify `requirements.txt` exists in `scripts/battlegroup/web/`

**Problem**: "Internal Server Error" when accessing API
- **Solution**:
  1. Click "Logs" tab in Railway
  2. Look for Python errors
  3. Common issue: Database path incorrect
  4. Fix: Set `DATABASE_PATH` environment variable

**Problem**: CORS errors in browser console
- **Solution**: Verify `CORS_ORIGINS` variable is exactly: `https://sevcavhub.github.io`

### API Connection Issues

**Problem**: Tools page shows "API Status: Offline"
- **Check**: Is Railway deployment running? (Green checkmark in Railway)
- **Check**: Can you access `https://your-railway-url.up.railway.app/api/health` directly?
- **Solution**: If Railway is down, click "Redeploy" in Railway dashboard

---

## Summary Checklist

- [ ] Step 1.1: Enabled GitHub Pages with "GitHub Actions" source
- [ ] Step 1.2: Verified workflow completed successfully (green checkmark)
- [ ] Step 1.3: Tested landing page loads at https://sevcavhub.github.io/north-africa-toe-builder/
- [ ] Step 2.1: Created Railway account via GitHub login
- [ ] Step 2.2: Created new Railway project from your repository
- [ ] Step 2.3: Set start command: `cd scripts/battlegroup/web && python app.py`
- [ ] Step 2.4: Added 3 environment variables (FLASK_ENV, PORT, CORS_ORIGINS)
- [ ] Step 2.5: Waited for deployment to complete
- [ ] Step 2.6: Tested `/api/health` endpoint returns healthy status
- [ ] Step 3.1: **Gave me your Railway URL so I can update tools.html**
- [ ] Step 3.2: Tested full integration (API Status shows Online)

---

## What to Do Right Now

1. **Complete Part 1** (GitHub Pages setup) - Takes 5 minutes
2. **Complete Part 2** (Railway deployment) - Takes 15-20 minutes
3. **Tell me your Railway URL** so I can complete Part 3

Then we'll test everything together!

---

## Current Status

✅ All code written and tested locally
✅ All code committed to GitHub (main branch)
✅ GitHub Actions workflow created
⏳ **YOU NEED TO**: Enable GitHub Pages in settings
⏳ **YOU NEED TO**: Create Railway project and deploy
⏳ **I WILL DO**: Update tools.html with your Railway URL

**Start with Part 1 now!** Let me know when GitHub Pages is live.
