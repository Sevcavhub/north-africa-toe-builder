# GitHub Pages Deployment Guide

## Quick Setup (Manual)

### Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** tab
3. Scroll to **Pages** section (left sidebar)
4. Under **Source**:
   - Branch: `main`
   - Folder: `/books`
5. Click **Save**

### Access Your Site

After 1-2 minutes, your site will be live at:
```
https://[username].github.io/north-africa-toe-builder/
```

### Custom Domain (Optional)

1. In Pages settings, add custom domain
2. Create CNAME record pointing to `[username].github.io`
3. Enable HTTPS enforcement

---

## Automated Deployment (GitHub Actions)

### Create Workflow File

Create `.github/workflows/deploy-books.yml`:

```yaml
name: Deploy Books to GitHub Pages

on:
  push:
    branches: [ main ]
    paths:
      - 'books/**'
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Pages
        uses: actions/configure-pages@v4

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: './books'

      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### Enable Actions Deployment

1. Go to **Settings** → **Pages**
2. Under **Source**, select **GitHub Actions**
3. Commit the workflow file above
4. Push to main branch
5. Check **Actions** tab for deployment status

---

## Testing Locally

### Option 1: Python HTTP Server

```bash
cd books
python -m http.server 8000
```

Visit: http://localhost:8000

### Option 2: Node.js HTTP Server

```bash
npm install -g http-server
cd books
http-server -p 8000
```

Visit: http://localhost:8000

### Option 3: Windows Batch Script

```bash
cd books
preview_landing.bat
```

Opens in default browser.

---

## File Structure for GitHub Pages

```
north-africa-toe-builder/
├── books/
│   ├── index.html              ← Landing page (entry point)
│   ├── battleaxe/book/book/    ← Battle book 1
│   ├── crusader/book/book/     ← Battle book 2
│   ├── ... (10 more books)
│   └── shared/                 ← Shared resources
└── ... (other project files)
```

GitHub Pages will serve:
- Root: `books/index.html`
- Books: `books/[battle]/book/book/index.html`

---

## Troubleshooting

### Issue: 404 Not Found

**Solution**: Check that:
1. Files are in `/books` folder
2. Repository is public (or you have GitHub Pro for private repos)
3. GitHub Pages is enabled in settings
4. You've pushed latest changes to main branch

### Issue: CSS Not Loading

**Solution**:
- Landing page uses embedded CSS (no external files)
- If MDBook CSS missing, rebuild books: `mdbook build`

### Issue: Links Broken

**Solution**:
- All links use relative paths
- Verify book directories exist: `ls books/*/book/book/index.html`
- Run validation: `python books/validate_links.py`

### Issue: Mobile Not Responsive

**Solution**:
- Clear browser cache
- Check viewport meta tag exists
- Test on actual mobile device (not just browser resize)

---

## Performance Optimization

### Current Stats
- Landing page: 24KB
- Load time: <1 second
- No external requests

### Future Optimizations
- [ ] Compress images (if added)
- [ ] Minify HTML (optional)
- [ ] Enable gzip compression (GitHub Pages auto-enables)
- [ ] Add service worker for offline access

---

## Analytics (Optional)

### Add Google Analytics

Add before `</head>` in `index.html`:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

### Add Plausible Analytics (Privacy-Friendly)

```html
<script defer data-domain="yourdomain.com" src="https://plausible.io/js/script.js"></script>
```

---

## SEO Optimization

### Current SEO Features ✅

- Meta description tag
- Semantic HTML5 structure
- Descriptive page title
- Header hierarchy (h1 → h2 → h3)
- Accessible alt text (if images added)

### Additional SEO (Optional)

```html
<!-- Open Graph for social media -->
<meta property="og:title" content="North Africa Campaign Books">
<meta property="og:description" content="Professional wargaming scenario books covering North Africa 1940-1943">
<meta property="og:image" content="https://yoursite.com/cover.jpg">
<meta property="og:url" content="https://yoursite.com">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="North Africa Campaign Books">
<meta name="twitter:description" content="BattleGroup wargaming scenarios for the Desert War">
<meta name="twitter:image" content="https://yoursite.com/cover.jpg">
```

---

## Backup Strategy

### Manual Backup

```bash
# Create timestamped backup
cd books
tar -czf ../backup-books-$(date +%Y%m%d).tar.gz .
```

### Git Tag Releases

```bash
# Tag stable releases
git tag -a v1.0 -m "Initial public release"
git push origin v1.0
```

### GitHub Releases

1. Go to **Releases** → **Create new release**
2. Tag version (e.g., `v1.0`)
3. Add release notes
4. Attach backup archive (optional)

---

## Maintenance Schedule

### Weekly
- [ ] Check for broken links
- [ ] Verify all book builds current
- [ ] Review analytics (if enabled)

### Monthly
- [ ] Update book content if needed
- [ ] Test on multiple browsers
- [ ] Review mobile experience

### Quarterly
- [ ] Update dependencies (MDBook version)
- [ ] Refresh historical research
- [ ] Add new features/books

---

## Support & Documentation

### Project Documentation
- README.md - Project overview
- CLAUDE.md - Development guidelines
- PROJECT_SCOPE.md - Complete vision
- PHASE_9B_SESSION_SUMMARY.md - Current status

### External Resources
- [GitHub Pages Docs](https://docs.github.com/en/pages)
- [MDBook Documentation](https://rust-lang.github.io/mdBook/)
- [BattleGroup Rules](https://www.plastic-soldier-company.co.uk/battlegroup)

---

**Last Updated**: November 11, 2025
**Deployment Status**: Ready for GitHub Pages
