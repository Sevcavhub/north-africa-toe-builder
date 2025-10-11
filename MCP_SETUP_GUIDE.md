# MCP Setup Guide for Beginners

## What Are MCPs?

**MCP = Model Context Protocol**

Think of MCPs as "superpowers" you can add to Claude Code. They give Claude access to:
- 🗄️ Databases (PostgreSQL, SQLite)
- 🌐 Web browsing (fetch websites automatically)
- 📁 Git operations (commit, push, pull)
- 🧠 Persistent memory (remember things across sessions)
- 📊 And much more!

**Without MCPs:** Claude can only read/write files you tell it to
**With MCPs:** Claude can interact with databases, browse web, use git, etc. autonomously

## How MCPs Work

```
You → Claude Code → MCP Server → External Tool (Database, Browser, etc.)
                         ↓
                    Results back to Claude
```

MCPs are small Node.js servers that run on your machine and give Claude controlled access to tools.

---

## Part 1: Finding Your MCP Configuration File

Claude Code stores MCP settings in a JSON configuration file. Location depends on your OS:

### Windows (Your System)
```
%APPDATA%\Claude\claude_desktop_config.json
```

Full path example:
```
C:\Users\YourUsername\AppData\Roaming\Claude\claude_desktop_config.json
```

### macOS
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

### Linux
```
~/.config/Claude/claude_desktop_config.json
```

---

## Part 2: Accessing the Configuration File

### Method 1: Using File Explorer (Windows - Easiest)

1. Press `Win + R` to open Run dialog
2. Type: `%APPDATA%\Claude`
3. Press Enter
4. Look for `claude_desktop_config.json`
5. If it doesn't exist, create it (see next section)

### Method 2: Using Command Line

```bash
# Navigate to config directory
cd %APPDATA%\Claude

# Open in VS Code (if you have code command)
code claude_desktop_config.json

# Or open in Notepad
notepad claude_desktop_config.json
```

### Method 3: Direct Path

Just open this path in your editor:
```
C:\Users\[YourUsername]\AppData\Roaming\Claude\claude_desktop_config.json
```
Replace `[YourUsername]` with your actual Windows username.

---

## Part 3: Creating the Configuration File

If the file doesn't exist yet:

### Step 1: Create the directory (if needed)
```bash
mkdir %APPDATA%\Claude
```

### Step 2: Create the file
```bash
cd %APPDATA%\Claude
echo {} > claude_desktop_config.json
```

### Step 3: Verify it exists
```bash
dir claude_desktop_config.json
```

---

## Part 4: Installing MCPs for Your TO&E Project

### Overview of What We'll Install

| MCP | Purpose | Priority |
|-----|---------|----------|
| **PostgreSQL** | Store TO&E data in queryable database | 🥇 High |
| **Puppeteer** | Scrape Feldgrau, Niehorster websites | 🥈 Medium |
| **Memory** | Remember source resolutions across sessions | 🥉 Medium |
| **Git** | Version control for generated data | 📦 Optional |

Let's install them one by one!

---

## Installing PostgreSQL MCP (Database Access)

### Prerequisites

You need PostgreSQL installed on your system.

**Option A: Install PostgreSQL (Recommended)**

1. Download from: https://www.postgresql.org/download/windows/
2. Run installer (accept defaults)
3. Remember the password you set for `postgres` user
4. Default port: 5432

**Option B: Use SQLite Instead (Simpler)**

SQLite doesn't require installation - it's just a file!

### Configuration

Open `%APPDATA%\Claude\claude_desktop_config.json` and add:

**For PostgreSQL:**
```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "postgresql://postgres:yourpassword@localhost:5432/toe_database"
      }
    }
  }
}
```

**For SQLite (easier for beginners):**
```json
{
  "mcpServers": {
    "sqlite": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sqlite"],
      "env": {
        "SQLITE_DB_PATH": "D:\\north-africa-toe-builder\\data\\toe_database.db"
      }
    }
  }
}
```

### Create the Database

**For PostgreSQL:**
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE toe_database;

# Exit
\q
```

**For SQLite:**
Nothing needed! The file will be created automatically.

### Test It

Restart Claude Code, then in chat:
```
Check if sqlite MCP is available. If so, create a test table.
```

---

## Installing Puppeteer MCP (Web Scraping)

### What It Does
Allows Claude to automatically fetch content from websites like Feldgrau.com, Niehorster.org, etc.

### Prerequisites
None! Puppeteer installs everything it needs via npx.

### Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sqlite": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sqlite"],
      "env": {
        "SQLITE_DB_PATH": "D:\\north-africa-toe-builder\\data\\toe_database.db"
      }
    },
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    }
  }
}
```

**Note:** Each MCP is separated by a comma.

### Test It

Restart Claude Code, then:
```
Use puppeteer MCP to fetch the HTML from http://feldgrau.com and show me the first 500 characters
```

---

## Installing Memory MCP (Persistent Knowledge)

### What It Does
Allows Claude to remember things across sessions - like source conflict resolutions, preferred data sources, etc.

### Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sqlite": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sqlite"],
      "env": {
        "SQLITE_DB_PATH": "D:\\north-africa-toe-builder\\data\\toe_database.db"
      }
    },
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
```

### Test It

```
Use memory MCP to store: "preferred_source_for_german_units: Tessin Wehrmacht Encyclopedia"
Then retrieve it back to confirm it worked.
```

---

## Installing Git MCP (Version Control)

### What It Does
Allows Claude to commit, push, pull, and manage git operations automatically.

### Prerequisites
Git must be installed: https://git-scm.com/download/win

### Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sqlite": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sqlite"],
      "env": {
        "SQLITE_DB_PATH": "D:\\north-africa-toe-builder\\data\\toe_database.db"
      }
    },
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "git": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-git"],
      "env": {
        "GIT_REPO_PATH": "D:\\north-africa-toe-builder"
      }
    }
  }
}
```

### Test It

```
Use git MCP to show me the current git status of the project
```

---

## Complete Configuration Example

Here's what your full `claude_desktop_config.json` should look like with all 4 MCPs:

```json
{
  "mcpServers": {
    "sqlite": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sqlite"],
      "env": {
        "SQLITE_DB_PATH": "D:\\north-africa-toe-builder\\data\\toe_database.db"
      }
    },
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "git": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-git"],
      "env": {
        "GIT_REPO_PATH": "D:\\north-africa-toe-builder"
      }
    }
  }
}
```

**Important:**
- Replace `D:\\north-africa-toe-builder` with your actual project path
- Use double backslashes `\\` on Windows
- Ensure proper JSON formatting (commas between items, but not after last item)

---

## Part 5: Verifying MCPs Are Working

### Step 1: Restart Claude Code
After editing the config, **completely restart** Claude Code (close and reopen).

### Step 2: Check Available MCPs

In Claude Code chat, send:
```
What MCP servers are currently available? List them all.
```

You should see:
```
Available MCP servers:
- sqlite
- puppeteer
- memory
- git
```

### Step 3: Test Each One

**Test SQLite:**
```
Use sqlite MCP to create a test table called 'test_units' with columns: id, name, nation
```

**Test Puppeteer:**
```
Use puppeteer MCP to fetch http://example.com and show me the HTML title
```

**Test Memory:**
```
Use memory MCP to store test_key = "test_value", then retrieve it
```

**Test Git:**
```
Use git MCP to show the current branch name
```

---

## Troubleshooting

### "MCP not found" or "MCP server failed to start"

**Problem:** `npx` can't find the MCP server

**Solution:**
1. Ensure Node.js and npm are installed:
   ```bash
   node --version
   npm --version
   ```
2. If not installed, download from: https://nodejs.org/
3. Restart Claude Code after installing Node.js

### "Permission denied" errors

**Problem:** MCP can't access files/directories

**Solution:**
- Check file paths use double backslashes on Windows: `D:\\path\\to\\file`
- Ensure directories exist
- Run Claude Code as administrator (right-click → Run as administrator)

### MCPs work but then stop working

**Problem:** MCP servers crash or disconnect

**Solution:**
- Check Claude Code logs: Help → Show Logs
- Look for MCP-related errors
- Restart Claude Code
- Check if antivirus is blocking npx

### "Invalid JSON" error

**Problem:** Syntax error in config file

**Solution:**
- Validate JSON at: https://jsonlint.com/
- Common errors:
  - Missing comma between items
  - Comma after last item (not allowed)
  - Unclosed quotes or brackets
  - Single backslash (use `\\` on Windows)

### Can't find claude_desktop_config.json

**Problem:** File doesn't exist yet

**Solution:**
```bash
# Create the directory
mkdir %APPDATA%\Claude

# Create empty config
echo {"mcpServers": {}} > %APPDATA%\Claude\claude_desktop_config.json
```

---

## Part 6: Using MCPs in Your TO&E Project

Once MCPs are installed, your autonomous orchestrator will automatically use them!

### Example Workflow with MCPs:

**Phase 1: Source Extraction**
```
WITHOUT MCPs:
- Only reads local Tessin files
- Can't access web sources

WITH MCPs:
✓ Reads local Tessin files
✓ Scrapes Feldgrau.com via Puppeteer MCP
✓ Fetches Niehorster data via Puppeteer MCP
✓ Checks Memory MCP for past resolutions
```

**Phase 2-5: Processing**
```
WITHOUT MCPs:
- Saves to JSON files only

WITH MCPs:
✓ Saves to SQLite database (queryable!)
✓ Stores resolutions in Memory MCP
✓ Commits to Git after each phase
```

**Phase 6: Outputs**
```
WITHOUT MCPs:
- Generates separate report files

WITH MCPs:
✓ Queries SQLite for aggregated reports
✓ Shows validation results from database
✓ Final commit with detailed message
```

---

## Quick Start Summary

1. **Create config file:**
   - Path: `%APPDATA%\Claude\claude_desktop_config.json`
   - Content: See "Complete Configuration Example" above

2. **Install Git** (if not already):
   - https://git-scm.com/download/win

3. **Restart Claude Code**

4. **Verify in chat:**
   ```
   What MCP servers are available?
   ```

5. **Run autonomous orchestrator:**
   ```bash
   npm run start:autonomous
   ```

6. **Watch Claude use MCPs automatically!**

---

## Next Steps

After setting up MCPs:

1. ✅ Test each MCP individually (use test commands above)
2. ✅ Run: `npm run start:autonomous`
3. ✅ Paste the orchestration message into Claude Code
4. ✅ Watch Claude autonomously process your project using MCPs!

The autonomous orchestrator will automatically detect and use available MCPs - no code changes needed!

---

## Getting Help

If you encounter issues:

1. **Check Claude Code logs:**
   - Help → Show Logs
   - Look for MCP-related errors

2. **Validate your JSON config:**
   - https://jsonlint.com/

3. **Ask in this chat:**
   ```
   I'm having trouble with [MCP name]. Here's the error: [paste error]
   ```

4. **MCP Documentation:**
   - https://github.com/modelcontextprotocol/servers

---

## Advanced: Creating Custom MCPs

Want to create your own MCP for specialized tasks? Check out:
- MCP SDK: https://github.com/modelcontextprotocol/sdk
- Example servers: https://github.com/modelcontextprotocol/servers

For this project, you could create:
- Custom MCP for parsing Tessin format specifically
- MCP for WITW wargaming scenario generation
- MCP for MDBook chapter formatting

---

**Ready to install your first MCP?** Start with SQLite - it's the easiest and most useful for your project!
