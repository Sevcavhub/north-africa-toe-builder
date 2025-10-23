#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, 'session_start.js');
let content = fs.readFileSync(filePath, 'utf-8');

// Fix Issue 2 & 3: Clarify checkpoint vs session:end
const oldWorkflow = `**After all 3 agents complete:**
- Run checkpoint: Bash('npm run checkpoint')
- Session end when done: Bash('npm run session:end')`;

const newWorkflow = `**After EACH batch of 3 units completes:**
- Run checkpoint: Bash('npm run checkpoint')
  - Validates units (JSON + chapter + schema compliance)
  - Updates WORKFLOW_STATE.json with new count
  - Commits to git with auto-generated message
  - Regenerates WORK_QUEUE.md

**After ALL batches complete (end of session):**
- Run session end: Bash('npm run session:end')
  - Runs final checkpoint
  - **Updates MCP Memory** with session patterns, statistics, and unit observations
  - Creates SESSION_SUMMARY.md with session report
  - Removes SESSION_ACTIVE.txt marker
  - Prepares for next session

⚠️ **CRITICAL**: You MUST run session:end when finished for the day - it stores knowledge in MCP memory for future sessions!`;

// Fix Issue 4: Enhanced MCP memory instructions
const oldAgentInstructions = `- Store findings in Memory MCP using mcp__memory__create_entities`;

const newAgentInstructions = `- **Store findings in MCP Memory** using mcp__memory__create_entities:
  - Create entity for the unit with observations about: organization structure, equipment patterns, command chain, tactical doctrine, supply challenges, unique characteristics
  - Store 5-10 observations per unit (not just 1!)
  - Link related units using mcp__memory__create_relations (e.g., brigade → division parent)
  - Example: {name: "1re_BFL_1942q1", entityType: "unit", observations: ["Multi-national force...", "Mixed French/British equipment...", "Defended Bir Hakeim..."]}`;

const oldReportLine = `- Report: confidence score, sources used, MCP tool usage log`;
const newReportLine = `- Report: confidence score, sources used, MCP tool usage log (should show 5-10 memory calls, not 1!)`;

content = content.replace(oldWorkflow, newWorkflow);
content = content.replace(oldAgentInstructions, newAgentInstructions);
content = content.replace(oldReportLine, newReportLine);

fs.writeFileSync(filePath, content, 'utf-8');

console.log('✅ Updated session_start.js:');
console.log('   - Issue 2: Added session:end workflow clarity');
console.log('   - Issue 3: Clarified checkpoint (per batch) vs session:end (end of all work)');
console.log('   - Issue 4: Enhanced MCP memory instructions (5-10 observations per unit)');
