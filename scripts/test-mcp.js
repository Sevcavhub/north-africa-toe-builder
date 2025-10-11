#!/usr/bin/env node

/**
 * MCP Testing Script
 *
 * Generates test prompts to verify MCPs are working in Claude Code.
 * Run: node scripts/test-mcp.js
 */

console.log('\n🧪 MCP Testing Script\n');
console.log('This script generates test prompts for you to paste into Claude Code.\n');
console.log('═'.repeat(80) + '\n');

console.log('📋 INSTRUCTIONS:\n');
console.log('1. Ensure Claude Code is running');
console.log('2. Copy each test prompt below');
console.log('3. Paste it into Claude Code chat');
console.log('4. Verify the response indicates success\n');
console.log('═'.repeat(80) + '\n');

// Test 1: Check available MCPs
console.log('TEST 1: Check Available MCPs');
console.log('─'.repeat(80));
console.log('PROMPT TO PASTE:');
console.log('─'.repeat(80));
console.log(`
List all available MCP servers and their capabilities.
For each MCP, show:
- Server name
- Status (available/unavailable)
- Brief description of what it does
`);
console.log('─'.repeat(80));
console.log('EXPECTED RESULT: Should list sqlite, puppeteer, memory, git\n');
console.log('═'.repeat(80) + '\n');

// Test 2: SQLite
console.log('TEST 2: SQLite Database MCP');
console.log('─'.repeat(80));
console.log('PROMPT TO PASTE:');
console.log('─'.repeat(80));
console.log(`
Use the sqlite MCP to:
1. Create a test table called 'mcp_test' with columns: id INTEGER PRIMARY KEY, test_name TEXT, timestamp TEXT
2. Insert a test record: id=1, test_name='SQLite MCP Test', timestamp='${new Date().toISOString()}'
3. Query the table to verify the record exists
4. Show me the results
`);
console.log('─'.repeat(80));
console.log('EXPECTED RESULT: Table created, record inserted, query shows the data\n');
console.log('═'.repeat(80) + '\n');

// Test 3: Puppeteer
console.log('TEST 3: Puppeteer Web Scraping MCP');
console.log('─'.repeat(80));
console.log('PROMPT TO PASTE:');
console.log('─'.repeat(80));
console.log(`
Use the puppeteer MCP to:
1. Fetch the HTML content from http://example.com
2. Extract and show me:
   - The page title
   - The first paragraph of text
   - The first 500 characters of HTML
`);
console.log('─'.repeat(80));
console.log('EXPECTED RESULT: HTML content fetched, title and text extracted\n');
console.log('═'.repeat(80) + '\n');

// Test 4: Memory
console.log('TEST 4: Memory Persistent Storage MCP');
console.log('─'.repeat(80));
console.log('PROMPT TO PASTE:');
console.log('─'.repeat(80));
console.log(`
Use the memory MCP to:
1. Store a key-value pair:
   key='test_memory_${Date.now()}'
   value='MCP Memory Test - ${new Date().toISOString()}'
2. Retrieve it back immediately
3. Confirm the value matches what was stored
`);
console.log('─'.repeat(80));
console.log('EXPECTED RESULT: Value stored and retrieved successfully\n');
console.log('═'.repeat(80) + '\n');

// Test 5: Git
console.log('TEST 5: Git Version Control MCP');
console.log('─'.repeat(80));
console.log('PROMPT TO PASTE:');
console.log('─'.repeat(80));
console.log(`
Use the git MCP to:
1. Show the current git status
2. List the current branch name
3. Show the last commit message
4. List any uncommitted changes
`);
console.log('─'.repeat(80));
console.log('EXPECTED RESULT: Git information displayed (or message if not a git repo)\n');
console.log('═'.repeat(80) + '\n');

// Summary
console.log('📊 VERIFICATION CHECKLIST:\n');
console.log('[ ] Test 1: Available MCPs listed');
console.log('[ ] Test 2: SQLite database operations worked');
console.log('[ ] Test 3: Puppeteer fetched web content');
console.log('[ ] Test 4: Memory stored and retrieved data');
console.log('[ ] Test 5: Git operations completed\n');

console.log('═'.repeat(80));
console.log('✅ If all 5 tests pass, your MCPs are configured correctly!\n');
console.log('Next step: Run autonomous orchestrator');
console.log('   npm run start:autonomous\n');
console.log('═'.repeat(80) + '\n');

// Advanced test
console.log('🚀 ADVANCED: Integrated Test');
console.log('─'.repeat(80));
console.log('After completing the above tests, run this integrated test:');
console.log('─'.repeat(80));
console.log(`
Use all available MCPs together to:

1. Memory MCP: Store "test_start_time" = "${new Date().toISOString()}"
2. Puppeteer MCP: Fetch http://feldgrau.com (just the HTML title)
3. SQLite MCP: Create table 'integration_test' with columns (id, url, title, timestamp)
4. SQLite MCP: Insert the fetched title into the table
5. Git MCP: Show git status
6. Memory MCP: Retrieve "test_start_time" and calculate elapsed time

Show me the results from each step.
`);
console.log('─'.repeat(80));
console.log('EXPECTED RESULT: All MCPs work together seamlessly\n');
console.log('═'.repeat(80) + '\n');

console.log('💡 TIP: If any MCP fails, check:\n');
console.log('   1. Claude Code was restarted after config changes');
console.log('   2. JSON config is valid (no syntax errors)');
console.log('   3. File paths use proper escaping (double backslashes on Windows)');
console.log('   4. Node.js and npm are installed (check: node --version)\n');
console.log('📖 See MCP_SETUP_GUIDE.md for troubleshooting\n');
