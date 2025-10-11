# Automated Git Commit & Push Guide

**Never forget to commit your work again!**

---

## 🎯 Quick Commands

### After Extracting Units:
```bash
npm run git:commit "Italian batch 3"
```

This automatically:
1. ✅ Checks for changed files
2. ✅ Stages all changes (git add .)
3. ✅ Creates descriptive commit message
4. ✅ Commits locally
5. ✅ Pushes to GitHub

**That's it!** One command does everything.

---

## 📋 Available Commands

### Commit Only (No Push)
```bash
npm run git:commit
```
- Commits locally but doesn't push to GitHub
- Safe if you want to review before pushing

### Commit + Push (Recommended)
```bash
npm run git:commit "batch name"
```
- Commits AND pushes to GitHub in one step
- Backs up your work immediately

### Dry Run (Test Mode)
```bash
node scripts/git_auto_commit.js --dry-run
```
- Shows what WOULD be committed without actually committing
- Good for checking before committing

---

## 🔄 Integration with Orchestration

### Option 1: Manual After Each Batch
After running autonomous extraction:
```bash
npm run start:autonomous
# Wait for batch to complete
npm run git:commit "British batch 1"
```

### Option 2: Add to Your Workflow
Update your workflow to include git commit after every 10 units:

1. Extract 10 units
2. Run QA validation
3. **Auto-commit:** `npm run git:commit`
4. Continue to next batch

### Option 3: Add to Handoff Prompt
Include in your session handoff instructions:
```
After completing each batch:
1. Validate units
2. Run: npm run git:commit "batch description"
3. Confirm push succeeded
```

---

## 📝 Commit Message Format

**Auto-generated commits look like this:**

```
feat: Add Italian batch 3 extraction

- 5 unit JSON files
- 5 MDBook chapters

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Smart detection:**
- Counts unit files
- Counts chapter files
- Detects agent changes
- Detects schema updates
- Detects documentation changes

---

## ⚙️ Configuration

### Enable/Disable Auto-Push

**Enable (default):**
```bash
# Automatically pushes to GitHub
npm run git:commit
```

**Disable:**
```bash
# Commit locally only, no push
GIT_AUTO_PUSH=false npm run git:commit
```

Or set in `.env`:
```
GIT_AUTO_PUSH=true
```

---

## 🚨 Error Handling

### If Push Fails:
The script will:
1. ✅ Still create the local commit
2. ⚠️  Show error message
3. 💡 Tell you to push manually: `git push`

Your work is ALWAYS saved locally even if GitHub is unreachable.

### If Nothing to Commit:
```
✅ Working tree clean - nothing to commit
```
No action needed - everything already committed!

---

## 📊 What Gets Committed?

**YES:**
- ✅ Unit JSON files (`units/*.json`)
- ✅ MDBook chapters (`north_africa_book/src/*.md`)
- ✅ Agent configurations (`agents/`)
- ✅ Schema updates (`schemas/`)
- ✅ Documentation (`docs/`)
- ✅ Scripts and source code (`src/`, `scripts/`)

**NO (excluded by .gitignore):**
- ❌ Resource Documents/ (large PDFs)
- ❌ data/iterations/ (Windows path issues)
- ❌ .venv/, .vscode/, .claude-code/
- ❌ Test/temp files

---

## 🎯 Best Practices

### Commit Frequency

**After Every 10 Units:**
```bash
npm run git:commit "British batch 1 (10 units)"
```

**After Major Changes:**
```bash
npm run git:commit "Updated QA Auditor agent"
```

**End of Session:**
```bash
npm run git:commit "Session complete - 35 units extracted"
```

### Batch Naming Convention

Use descriptive names:
- ✅ `"Italian batch 3"`
- ✅ `"British Commonwealth units"`
- ✅ `"American 1942-1943 quarter"`
- ❌ `"stuff"` (not descriptive)
- ❌ `"units"` (too vague)

---

## 🔗 Alternative: Git MCP Server

**Claude Code supports Git MCP for direct git operations!**

To use Git MCP instead:
1. Install Git MCP server: https://github.com/modelcontextprotocol/servers/tree/main/src/git
2. Configure in `.claude/mcp.json`
3. Claude Code can then commit/push directly without scripts

**Script vs MCP:**
- **Script:** Simple, works now, one command
- **MCP:** More integrated, requires setup

---

## 📚 Examples

### Example 1: After Italian Extraction
```bash
# Extract Italian units
npm run start:autonomous

# Validate
npm run validate

# Commit and push
npm run git:commit "Italian divisions 1940-1942"
```

### Example 2: Dry Run First
```bash
# Check what would be committed
node scripts/git_auto_commit.js --dry-run

# If looks good, commit for real
npm run git:commit "German Panzer divisions"
```

### Example 3: Commit Without Push
```bash
# Commit locally only
GIT_AUTO_PUSH=false npm run git:commit "Work in progress"

# Review, then push manually later
git push
```

---

## 🆘 Troubleshooting

### "Failed to push to GitHub"
**Solution:** Check internet connection, then:
```bash
git push
```
Your commit is safe locally!

### "Nothing to commit"
**Solution:** You're all caught up! No action needed.

### "Authentication failed"
**Solution:** GitHub credentials not configured. Run:
```bash
git config --global credential.helper wincred
git push
# Enter credentials when prompted
```

---

## ✨ Summary

**One command to remember:**
```bash
npm run git:commit "description"
```

**That's it!** Your work is automatically committed and pushed to GitHub.

**Never lose work again!** 🎉
