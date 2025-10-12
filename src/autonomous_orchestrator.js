/**
 * Autonomous Orchestrator - October 2025
 *
 * Leverages Claude Sonnet 4.5's full capabilities:
 * - Task tool for true autonomous sub-agents
 * - Extended thinking for complex analysis
 * - Direct file access via Read/Write tools
 * - Parallel processing
 * - Background tasks
 * - MCP integrations
 *
 * Usage from terminal:
 *   node src/autonomous_orchestrator.js
 *
 * Then in Claude Code chat, send message:
 *   "Start autonomous orchestration for North Africa project"
 *
 * The orchestrator will:
 * 1. Load project configuration
 * 2. Launch specialized agents for each phase
 * 3. Process all units autonomously
 * 4. Track progress with TodoWrite
 * 5. Save all outputs
 * 6. Generate final report
 *
 * All work happens in this Claude Code session using your subscription!
 */

const fs = require('fs').promises;
const path = require('path');

/**
 * Autonomous Orchestrator Manager
 *
 * This is a lightweight wrapper that helps coordinate between:
 * - Node.js file system operations
 * - Claude Code's autonomous agent capabilities
 *
 * The actual orchestration happens through Claude Code's Task tool.
 */
class AutonomousOrchestrator {
  constructor() {
    this.projectPath = 'projects/north_africa_campaign.json';
    this.project = null;
    this.outputDir = path.join(__dirname, '../data/output/autonomous_' + Date.now());
  }

  /**
   * Initialize orchestrator
   * Loads project config and prepares directories
   */
  async initialize() {
    console.log('\n' + '='.repeat(80));
    console.log('  🤖 AUTONOMOUS ORCHESTRATOR - October 2025');
    console.log('  Leveraging Sonnet 4.5\'s full capabilities');
    console.log('='.repeat(80) + '\n');

    // Load project configuration
    try {
      const projectData = await fs.readFile(this.projectPath, 'utf-8');
      this.project = JSON.parse(projectData);
    } catch (error) {
      console.error(`❌ Failed to load project: ${error.message}`);
      console.error(`   Looking for: ${this.projectPath}\n`);
      process.exit(1);
    }

    // Load seed units from separate file
    try {
      const seedUnitsPath = path.join(path.dirname(this.projectPath), 'north_africa_seed_units.json');
      const seedData = await fs.readFile(seedUnitsPath, 'utf-8');
      const seedUnits = JSON.parse(seedData);

      // Convert seed units to flat list
      this.project.seed_units = [];
      const nations = ['german_units', 'italian_units', 'british_units', 'usa_units', 'french_units'];
      const nationMap = {
        'german_units': 'Germany',
        'italian_units': 'Italy',
        'british_units': 'Britain',
        'usa_units': 'USA',
        'french_units': 'France'
      };

      for (const key of nations) {
        if (seedUnits[key]) {
          for (const unit of seedUnits[key]) {
            for (const quarter of unit.quarters) {
              this.project.seed_units.push({
                nation: nationMap[key],
                unit_designation: unit.designation,
                quarter: quarter
              });
            }
          }
        }
      }
    } catch (error) {
      console.error(`❌ Failed to load seed units: ${error.message}`);
      console.error(`   Looking for: north_africa_seed_units.json\n`);
      process.exit(1);
    }

    console.log(`📋 Project: ${this.project.project_name}`);
    console.log(`📍 Campaign: ${this.project.scope.theater}`);
    console.log(`🎯 Units: ${this.project.seed_units.length} unit-quarters\n`);

    // Create output directory
    await fs.mkdir(this.outputDir, { recursive: true });
    await fs.mkdir(path.join(this.outputDir, 'units'), { recursive: true });
    await fs.mkdir(path.join(this.outputDir, 'reports'), { recursive: true });

    console.log(`📁 Output directory: ${this.outputDir}\n`);

    // Save orchestration metadata
    const metadata = {
      started_at: new Date().toISOString(),
      project: this.project.project_name,
      total_units: this.project.seed_units.length,
      output_dir: this.outputDir,
      orchestrator_version: 'October 2025',
      capabilities_used: [
        'Task tool for sub-agents',
        'Extended thinking',
        'Direct file access',
        'Parallel processing',
        'MCP integrations'
      ]
    };

    await fs.writeFile(
      path.join(this.outputDir, 'orchestration_metadata.json'),
      JSON.stringify(metadata, null, 2)
    );

    return metadata;
  }

  /**
   * Display instructions for Claude Code
   */
  displayInstructions() {
    console.log('═'.repeat(80));
    console.log('  READY FOR AUTONOMOUS ORCHESTRATION');
    console.log('═'.repeat(80));
    console.log('\n📢 INSTRUCTIONS:\n');
    console.log('1. Copy the following message');
    console.log('2. Paste it into Claude Code chat');
    console.log('3. Claude will autonomously orchestrate the entire build\n');
    console.log('─'.repeat(80));
    console.log('MESSAGE TO SEND TO CLAUDE CODE:');
    console.log('─'.repeat(80));
    console.log(`
Start autonomous orchestration for the North Africa TO&E project.

Project file: ${this.projectPath}
Output directory: ${this.outputDir}
Units to process: ${this.project.seed_units.length}

**MCP CAPABILITIES:**
Check which MCPs are available and use them:
- SQLite MCP → Store TO&E data in queryable database (table: units, equipment, personnel)
- Puppeteer MCP → Automatically scrape Feldgrau.com, Niehorster.org for Tier 2 sources
- Memory MCP → Remember source conflict resolutions across sessions
- Git MCP → Auto-commit after each phase with detailed messages

If MCPs are NOT available, gracefully degrade to file-based operations.

Use the following approach:

**PHASE 1: Setup & Planning**
1. Check available MCPs and log which ones we can use
2. Use TodoWrite to create task list for all ${this.project.seed_units.length} units
3. Read project configuration from ${this.projectPath}
4. Load agent definitions from agents/agent_catalog.json
5. If SQLite MCP available: Initialize database schema
6. If Git MCP available: Create initial commit for this orchestration run

**PHASE 2: Document Extraction (Parallel Processing)**
For each unit in projects/north_africa_seed_units.json:
- Launch document_parser agent using Task tool
- Each agent should:
  * TIER 1: Use Glob to find relevant source documents in Resource Documents/
  * TIER 1: Use Read to load source content (Tessin, Army Lists, Field Manuals)
  * TIER 2 (if Puppeteer MCP available): Scrape Feldgrau, Niehorster for additional data
  * TIER 3 (if needed): Check Memory MCP for past similar units' resolutions
  * Use extended thinking for complex document analysis when sources conflict
  * Extract structured data following unified TO&E schema (schemas/unified_toe_schema.json)
  * Return JSON with facts, citations, confidence scores, and source tier used
  * If SQLite MCP available: INSERT extracted data into database immediately
- Process units in parallel (batches of 3 maximum)
- Update progress with TodoWrite after each unit
- **CHECKPOINT: After every 3-unit batch, run: Bash('npm run checkpoint')**
- This creates a git commit and updates WORKFLOW_STATE.json for crash recovery

**PHASE 3: Cross-Reference Validation**
- Launch historical_research agents to:
  * Cross-reference extracted data against multiple sources
  * Identify conflicts and resolve them
  * If Memory MCP available: Store resolutions for future use
  * Update confidence scores based on source agreement
  * If SQLite MCP available: UPDATE confidence scores in database
  * Flag items needing human review (confidence < 75%)

**PHASE 4: TO&E Generation**
- Generate complete TO&E JSON files for each unit
- Validate against schemas/unified_toe_schema.json
- Use MCP ide__getDiagnostics for schema validation
- Save to ${this.outputDir}/units/
- If SQLite MCP available: Ensure database and JSON files are in sync
- If Git MCP available: Commit completed phase with summary

**PHASE 5: Output Generation**
- Generate MDBook chapters for each unit
- Export wargaming scenarios (WITW format)
- If SQLite MCP available: Generate reports via SQL queries:
  * Units by nation and quarter
  * Average confidence scores by source tier
  * Equipment totals and distributions
  * Source usage statistics
- Create validation summary report
- Generate final orchestration summary
- If Git MCP available: Final commit with complete summary

**FINAL DELIVERABLES:**
- ${this.project.seed_units.length} TO&E JSON files (${this.outputDir}/units/)
- SQLite database (if MCP available): ${this.outputDir.replace(/\\/g, '/')}/../toe_database.db
- Validation reports
- Progress logs
- Git history (if MCP available)

**AUTONOMOUS EXECUTION:**
Use your autonomous capabilities to complete this entire workflow:
- Launch Task agents in parallel (batches of 3 units maximum - wait for batch to complete before starting next batch)
- Use extended thinking when analyzing conflicting sources
- Leverage all available MCPs to enhance functionality
- Gracefully degrade if MCPs not available
- Update progress regularly using TodoWrite
- Save all outputs directly using Write tool
- Handle errors and retry when appropriate

Begin orchestration now!
`);
    console.log('─'.repeat(80));
    console.log('\n4. Watch Claude work autonomously!');
    console.log('5. Check progress in real-time via TodoWrite updates');
    console.log('6. Review outputs in: ' + this.outputDir);
    console.log('\n═'.repeat(80) + '\n');
  }

  /**
   * Generate progress dashboard
   */
  async generateProgressDashboard() {
    const dashboardPath = path.join(this.outputDir, 'PROGRESS_DASHBOARD.md');

    const dashboard = `# Autonomous Orchestration Progress Dashboard

## Project: ${this.project.project_name}

## Status: 🚀 Running

Started: ${new Date().toISOString()}

## Total Units: ${this.project.seed_units.length}

## Progress Tracking

Claude Code will update this dashboard automatically as it processes units.

Check the todo list in Claude Code chat for real-time progress.

## Outputs

All generated files will appear in:
\`\`\`
${this.outputDir}/
├── units/                    # Generated TO&E JSON files
├── reports/                  # Validation and summary reports
└── orchestration_metadata.json
\`\`\`

## Real-Time Progress

To see real-time progress:
1. Watch the Claude Code chat for TodoWrite updates
2. Check ${this.outputDir}/units/ for new files
3. Monitor completion messages in chat

## Units Being Processed

${this.project.seed_units.map((unit, i) =>
  `${i + 1}. ${unit.nation} ${unit.unit_designation} (${unit.quarter})`
).join('\n')}

---

This dashboard is auto-generated by the Autonomous Orchestrator.
October 2025 - Leveraging Sonnet 4.5 full capabilities.
`;

    await fs.writeFile(dashboardPath, dashboard);
    console.log(`📊 Progress dashboard: ${dashboardPath}\n`);
  }
}

/**
 * Main execution
 */
async function main() {
  const orchestrator = new AutonomousOrchestrator();

  try {
    await orchestrator.initialize();
    await orchestrator.generateProgressDashboard();
    orchestrator.displayInstructions();
  } catch (error) {
    console.error('\n❌ Error:', error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { AutonomousOrchestrator };
