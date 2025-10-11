#!/usr/bin/env node

/**
 * Single-Session Orchestrator
 *
 * Designed to run ENTIRELY within Claude Code chat session.
 * - No API calls
 * - No manual JSON entry
 * - No separate terminals
 * - Uses Claude Code subscription tokens only
 *
 * This script prepares all prompts and saves them to files.
 * Then you paste them one by one into this Claude Code chat,
 * and Claude processes them automatically.
 */

const fs = require('fs').promises;
const path = require('path');
const { SourceWaterfall } = require('./source_waterfall');

class SingleSessionOrchestrator {
  constructor(projectPath) {
    this.projectPath = projectPath;
    this.project = null;
    this.agents = new Map();
    this.sessionDir = path.join(__dirname, '../data/output/session_' + Date.now());
  }

  async initialize() {
    console.log('\n' + '='.repeat(80));
    console.log('  🎯 SINGLE-SESSION ORCHESTRATOR');
    console.log('  Fully automated within Claude Code - No API calls!');
    console.log('='.repeat(80) + '\n');

    // Load project
    const projectData = await fs.readFile(this.projectPath, 'utf-8');
    this.project = JSON.parse(projectData);

    console.log(`Project: ${this.project.project_name}`);
    console.log(`Units: ${this.project.seed_units.length}`);

    // Load agents
    const catalogPath = path.join(__dirname, '../agents/agent_catalog.json');
    const catalog = JSON.parse(await fs.readFile(catalogPath, 'utf-8'));

    for (const agent of catalog.agents) {
      this.agents.set(agent.agent_id, agent);
    }

    console.log(`Agents: ${this.agents.size} loaded\n`);

    // Create session directory
    await fs.mkdir(this.sessionDir, { recursive: true });
    await fs.mkdir(path.join(this.sessionDir, 'prompts'), { recursive: true });
    await fs.mkdir(path.join(this.sessionDir, 'responses'), { recursive: true });

    console.log(`Session directory: ${this.sessionDir}\n`);
  }

  /**
   * Generate all prompts for all units
   */
  async generateAllPrompts() {
    console.log('📝 GENERATING ALL PROMPTS\n');
    console.log('This will create prompt files for every unit.');
    console.log('You can then process them in Claude Code at your own pace.\n');

    const promptIndex = [];

    for (let i = 0; i < this.project.seed_units.length; i++) {
      const unit = this.project.seed_units[i];

      console.log(`[${i + 1}/${this.project.seed_units.length}] ${unit.nation} ${unit.unit_designation} (${unit.quarter})`);

      try {
        // PHASE 1: Prepare source
        console.log('  - Searching for sources...');
        const sourceResult = await this.prepareSource(unit);

        // PHASE 2: Generate document_parser prompt
        console.log('  - Generating document_parser prompt...');
        const promptFile = await this.generatePrompt('document_parser', {
          source_content: sourceResult.content,
          document_type: sourceResult.source_name,
          nation: unit.nation,
          quarter: unit.quarter,
          unit_designation: unit.unit_designation
        }, `${i + 1}_parse_${unit.nation}_${this.sanitize(unit.unit_designation)}`);

        promptIndex.push({
          number: i + 1,
          unit: `${unit.nation} ${unit.unit_designation} (${unit.quarter})`,
          phase: 'document_parser',
          promptFile: promptFile,
          responseFile: promptFile.replace('/prompts/', '/responses/').replace('_prompt.txt', '_response.json')
        });

        console.log(`  ✓ Prompt saved\n`);

      } catch (error) {
        console.log(`  ✗ Failed: ${error.message}\n`);
        continue;
      }
    }

    // Save index
    const indexPath = path.join(this.sessionDir, 'PROMPT_INDEX.json');
    await fs.writeFile(indexPath, JSON.stringify(promptIndex, null, 2));

    console.log('\n' + '='.repeat(80));
    console.log(`✅ ALL PROMPTS GENERATED`);
    console.log('='.repeat(80));
    console.log(`\nTotal prompts: ${promptIndex.length}`);
    console.log(`Location: ${this.sessionDir}/prompts/\n`);

    console.log('📋 INDEX FILE: ' + indexPath);
    console.log('\nNext steps:');
    console.log('1. Open PROMPT_INDEX.json to see all prompts');
    console.log('2. Copy each prompt file content');
    console.log('3. Paste it into this Claude Code chat');
    console.log('4. Save Claude\'s JSON response to the corresponding responseFile');
    console.log('5. Continue to next prompt\n');

    // Create a guide file
    await this.createProcessingGuide(promptIndex);

    return promptIndex;
  }

  /**
   * Create interactive processing guide
   */
  async createProcessingGuide(promptIndex) {
    const guidePath = path.join(this.sessionDir, 'PROCESSING_GUIDE.md');

    let guide = `# Processing Guide - Single Session Orchestrator

## Total Prompts: ${promptIndex.length}

## How to Process

For each prompt below:

1. **Read the prompt file** (full path provided)
2. **Copy the entire prompt**
3. **Paste it into Claude Code chat** (this session)
4. **Wait for Claude's JSON response**
5. **Copy Claude's JSON response**
6. **Save it to the response file** (path provided)
7. **Move to next prompt**

---

`;

    for (const item of promptIndex) {
      guide += `
## ${item.number}. ${item.unit}

**Phase:** ${item.phase}

**Prompt File:**
\`\`\`
${item.promptFile}
\`\`\`

**Response File (save Claude's JSON here):**
\`\`\`
${item.responseFile}
\`\`\`

**Quick Commands:**

Read prompt:
\`\`\`bash
cat "${item.promptFile}"
\`\`\`

Save response (paste JSON after <<'EOF'):
\`\`\`bash
cat > "${item.responseFile}" <<'EOF'
[paste Claude's JSON response here]
EOF
\`\`\`

---

`;
    }

    guide += `
## Verification

After processing all prompts, verify responses exist:

\`\`\`bash
ls -lh ${path.join(this.sessionDir, 'responses')}/*.json | wc -l
\`\`\`

Expected: ${promptIndex.length} files

## Next Phase

Once all document_parser responses are saved, run:

\`\`\`bash
node src/single_session_orchestrator.js ${this.projectPath} --phase2
\`\`\`

This will generate the next set of prompts for historical_research agent.
`;

    await fs.writeFile(guidePath, guide);

    console.log('📖 GUIDE: ' + guidePath);
    console.log('   Open this file for step-by-step instructions\n');
  }

  /**
   * Prepare source using waterfall
   */
  async prepareSource(unit) {
    const waterfall = new SourceWaterfall(
      this.project.source_strategy,
      this.project.resource_documents_path || 'Resource Documents'
    );

    return await waterfall.prepare_source(unit);
  }

  /**
   * Generate a prompt file
   */
  async generatePrompt(agentId, inputs, filename) {
    const agent = this.agents.get(agentId);
    if (!agent) throw new Error(`Agent ${agentId} not found`);

    // Build prompt from template
    let prompt = agent.prompt_template;

    // Replace all variables
    for (const [key, value] of Object.entries(inputs)) {
      const replacement = typeof value === 'object'
        ? JSON.stringify(value, null, 2)
        : String(value);

      // Try multiple variable name formats
      const variations = [
        key,
        key.replace(/([A-Z])/g, '_$1').toLowerCase(), // camelCase to snake_case
        key.toLowerCase()
      ];

      for (const variant of variations) {
        prompt = prompt.replace(new RegExp(`\\{${variant}\\}`, 'g'), replacement);
      }
    }

    // Add response instructions
    prompt += `\n\n---

RESPONSE FORMAT:

Provide your response as a JSON object or array following the schema described above.

Your JSON response will be saved automatically.

Do NOT include explanatory text before or after the JSON - provide ONLY valid JSON.

If you need to include notes, add them in a "notes" field within the JSON.
`;

    // Save to file
    const promptPath = path.join(this.sessionDir, 'prompts', `${filename}_prompt.txt`);
    await fs.writeFile(promptPath, prompt);

    return promptPath;
  }

  /**
   * Sanitize unit designation for filename
   */
  sanitize(str) {
    return str.replace(/[^a-z0-9]/gi, '_').replace(/_+/g, '_').toLowerCase();
  }

  /**
   * Display a prompt for immediate processing
   */
  async displayPrompt(promptPath) {
    const prompt = await fs.readFile(promptPath, 'utf-8');

    console.log('\n' + '█'.repeat(80));
    console.log('PROMPT READY FOR CLAUDE CODE');
    console.log('█'.repeat(80));
    console.log('\n' + prompt + '\n');
    console.log('█'.repeat(80));
    console.log('Waiting for Claude Code to respond...');
    console.log('█'.repeat(80) + '\n');
  }

  /**
   * Process interactively - display one prompt at a time
   */
  async processInteractive() {
    const indexPath = path.join(this.sessionDir, 'PROMPT_INDEX.json');
    const promptIndex = JSON.parse(await fs.readFile(indexPath, 'utf-8'));

    console.log('\n' + '='.repeat(80));
    console.log('  🎮 INTERACTIVE MODE');
    console.log('='.repeat(80) + '\n');

    console.log(`Processing ${promptIndex.length} prompts interactively.\n`);
    console.log('Instructions:');
    console.log('1. Read each prompt below');
    console.log('2. Claude Code (AI) will process it in this chat');
    console.log('3. Save Claude\'s response to the indicated file');
    console.log('4. Continue to next prompt\n');

    for (const item of promptIndex) {
      console.log(`\n[${ item.number}/${promptIndex.length}] ${item.unit} - ${item.phase}\n`);

      await this.displayPrompt(item.promptFile);

      console.log(`\nResponse should be saved to:\n${item.responseFile}\n`);

      console.log('Press Enter when ready for next prompt...');
      await this.waitForEnter();
    }

    console.log('\n✅ All prompts displayed!\n');
  }

  async waitForEnter() {
    return new Promise(resolve => {
      process.stdin.once('data', () => resolve());
    });
  }
}

// CLI
async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log(`
Usage:
  node src/single_session_orchestrator.js <project.json> [options]

Options:
  --generate      Generate all prompts (default)
  --interactive   Display prompts one by one for processing
  --phase2        Generate Phase 2 prompts (historical_research)

Examples:
  # Generate all Phase 1 prompts
  node src/single_session_orchestrator.js projects/north_africa_campaign.json

  # Process interactively
  node src/single_session_orchestrator.js projects/north_africa_campaign.json --interactive

  # Generate Phase 2 prompts
  node src/single_session_orchestrator.js projects/north_africa_campaign.json --phase2
`);
    process.exit(0);
  }

  const projectPath = args[0];
  const orchestrator = new SingleSessionOrchestrator(projectPath);

  await orchestrator.initialize();

  if (args.includes('--interactive')) {
    await orchestrator.processInteractive();
  } else if (args.includes('--phase2')) {
    console.log('Phase 2 generation not yet implemented\n');
  } else {
    await orchestrator.generateAllPrompts();
  }
}

if (require.main === module) {
  main().catch(error => {
    console.error('\n❌ Error:', error.message);
    console.error(error.stack);
    process.exit(1);
  });
}

module.exports = { SingleSessionOrchestrator };
