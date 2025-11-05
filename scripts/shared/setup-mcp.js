#!/usr/bin/env node

/**
 * MCP Setup Helper
 *
 * Automatically configures Claude Code to use MCPs for this project.
 * Run: node scripts/setup-mcp.js
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

console.log('\n🔧 MCP Setup Helper\n');
console.log('This script will configure MCPs for your TO&E project.\n');
console.log('Supports both:');
console.log('  - Claude Code (VS Code extension) → .mcp.json in project root');
console.log('  - Claude Desktop (standalone app) → AppData config\n');

// Determine Claude config path based on OS
function getClaudeConfigPath() {
  const platform = os.platform();
  const homeDir = os.homedir();

  if (platform === 'win32') {
    return path.join(process.env.APPDATA || path.join(homeDir, 'AppData', 'Roaming'), 'Claude', 'claude_desktop_config.json');
  } else if (platform === 'darwin') {
    return path.join(homeDir, 'Library', 'Application Support', 'Claude', 'claude_desktop_config.json');
  } else {
    return path.join(homeDir, '.config', 'Claude', 'claude_desktop_config.json');
  }
}

// Get current project path with proper escaping
function getProjectPath() {
  const projectPath = process.cwd();

  // On Windows, escape backslashes for JSON
  if (os.platform() === 'win32') {
    return projectPath.replace(/\\/g, '\\\\');
  }

  return projectPath;
}

// Create Claude Code .mcp.json in project root
function setupClaudeCodeMCP() {
  const mcpJsonPath = path.join(process.cwd(), '.mcp.json');

  const config = {
    mcpServers: {
      sqlite: {
        command: 'npx',
        args: ['-y', 'mcp-server-sqlite-npx'],
        env: {
          SQLITE_DB_PATH: '${workspaceFolder}/data/toe_database.db'
        }
      },
      git: {
        command: 'npx',
        args: ['-y', '@cyanheads/git-mcp-server'],
        env: {
          GIT_REPO_PATH: '${workspaceFolder}'
        }
      },
      puppeteer: {
        command: 'npx',
        args: ['-y', '@modelcontextprotocol/server-puppeteer']
      },
      memory: {
        command: 'npx',
        args: ['-y', '@modelcontextprotocol/server-memory']
      }
    }
  };

  fs.writeFileSync(mcpJsonPath, JSON.stringify(config, null, 2), 'utf8');

  return mcpJsonPath;
}

async function setupMCP() {
  console.log('🎯 Setting up MCPs for BOTH Claude Code and Claude Desktop...\n');

  // Setup 1: Claude Code (.mcp.json in project root)
  console.log('1️⃣  CLAUDE CODE (VS Code Extension)');
  console.log('   Creating .mcp.json in project root...');
  try {
    const claudeCodePath = setupClaudeCodeMCP();
    console.log(`   ✅ Created: ${claudeCodePath}\n`);
  } catch (error) {
    console.error(`   ❌ Failed: ${error.message}\n`);
  }

  // Setup 2: Claude Desktop (AppData config)
  console.log('2️⃣  CLAUDE DESKTOP (Standalone App)');
  const configPath = getClaudeConfigPath();
  const projectPath = getProjectPath();

  console.log(`   Config location: ${configPath}`);
  console.log(`   Project path: ${projectPath}`);

  // Check if Claude config directory exists
  const configDir = path.dirname(configPath);
  if (!fs.existsSync(configDir)) {
    console.log(`📁 Creating directory: ${configDir}`);
    fs.mkdirSync(configDir, { recursive: true });
  }

  // Build MCP configuration
  const mcpConfig = {
    mcpServers: {
      sqlite: {
        command: 'npx',
        args: ['-y', 'mcp-server-sqlite-npx'],
        env: {
          SQLITE_DB_PATH: path.join(projectPath, 'data', 'toe_database.db').replace(/\\/g, '\\\\')
        }
      },
      puppeteer: {
        command: 'npx',
        args: ['-y', '@modelcontextprotocol/server-puppeteer']
      },
      memory: {
        command: 'npx',
        args: ['-y', '@modelcontextprotocol/server-memory']
      },
      git: {
        command: 'npx',
        args: ['-y', '@cyanheads/git-mcp-server'],
        env: {
          GIT_REPO_PATH: projectPath
        }
      }
    }
  };

  // Check if config already exists
  let existingConfig = {};
  if (fs.existsSync(configPath)) {
    console.log('⚠️  Existing Claude config found.');

    try {
      existingConfig = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      console.log('✓ Existing config loaded.\n');

      // Merge with existing MCPs
      if (existingConfig.mcpServers) {
        console.log('📝 Merging with existing MCP servers...');
        mcpConfig.mcpServers = {
          ...existingConfig.mcpServers,
          ...mcpConfig.mcpServers
        };
      }
    } catch (error) {
      console.error('❌ Error reading existing config:', error.message);
      console.log('💾 Will create backup and write new config.\n');

      // Backup existing config
      const backupPath = configPath + '.backup.' + Date.now();
      fs.copyFileSync(configPath, backupPath);
      console.log(`✓ Backup saved to: ${backupPath}\n`);
    }
  }

  // Write configuration
  try {
    const finalConfig = {
      ...existingConfig,
      ...mcpConfig
    };

    fs.writeFileSync(configPath, JSON.stringify(finalConfig, null, 2), 'utf8');

    console.log('   ✅ Claude Desktop config written successfully!\n');

    console.log('═'.repeat(80));
    console.log('  ✅ MCP SETUP COMPLETE');
    console.log('═'.repeat(80));

    console.log('\n📋 Configured MCPs (both applications):');
    console.log('   ✓ SQLite - Database access');
    console.log('   ✓ Puppeteer - Web scraping');
    console.log('   ✓ Memory - Persistent knowledge');
    console.log('   ✓ Git - Version control\n');

    console.log('📍 Configuration Locations:');
    console.log(`   • Claude Code: ${path.join(process.cwd(), '.mcp.json')}`);
    console.log(`   • Claude Desktop: ${configPath}\n`);

    console.log('🔄 Next Steps (Choose based on what you\'re using):\n');

    console.log('   IF USING CLAUDE CODE (VS Code extension):');
    console.log('   1. Restart VS Code (completely close and reopen)');
    console.log('   2. In Claude Code chat, verify: "What MCP servers are available?"');
    console.log('   3. Test with: npm run mcp:test');
    console.log('   4. Run: npm run start:autonomous\n');

    console.log('   IF USING CLAUDE DESKTOP (standalone app):');
    console.log('   1. Restart Claude Desktop app');
    console.log('   2. Open this project folder');
    console.log('   3. Verify MCPs are loaded\n');

    console.log('📖 For more information, see MCP_SETUP_GUIDE.md\n');

  } catch (error) {
    console.error('❌ Error writing config:', error.message);
    console.error('\nManual setup required. See MCP_SETUP_GUIDE.md for instructions.\n');
    process.exit(1);
  }
}

// Check prerequisites
function checkPrerequisites() {
  console.log('🔍 Checking prerequisites...\n');

  // Check Node.js
  const nodeVersion = process.version;
  console.log(`✓ Node.js: ${nodeVersion}`);

  // Check if in project directory
  if (!fs.existsSync('package.json')) {
    console.error('❌ Error: Not in project directory');
    console.error('   Run this script from the north-africa-toe-builder directory\n');
    process.exit(1);
  }

  console.log('✓ Project directory confirmed');

  // Check if data directory exists
  if (!fs.existsSync('data')) {
    console.log('📁 Creating data directory...');
    fs.mkdirSync('data', { recursive: true });
  }

  console.log('✓ Data directory ready\n');
}

// Main execution
(async () => {
  try {
    checkPrerequisites();
    await setupMCP();
  } catch (error) {
    console.error('❌ Fatal error:', error.message);
    console.error(error.stack);
    process.exit(1);
  }
})();
