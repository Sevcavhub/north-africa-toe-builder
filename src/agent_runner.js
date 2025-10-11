/**
 * Agent Runner - Runs in separate Claude Code terminal
 * Watches for tasks and displays prompts for Claude Code to execute
 */

const fs = require('fs').promises;
const path = require('path');
const readline = require('readline');

class AgentRunner {
  constructor(agentId) {
    this.agentId = agentId;
    this.tasksDir = path.join(__dirname, '../tasks');
    this.outputsDir = path.join(__dirname, '../outputs');
    this.catalogPath = path.join(__dirname, '../agents/agent_catalog.json');
    this.agentConfig = null;
    this.running = true;

    console.log(`🤖 Agent Runner: ${agentId}`);
    console.log(`   Watching for tasks...`);
    console.log(`   Press Ctrl+C to stop\n`);
  }

  async initialize() {
    // Load agent configuration
    const catalog = JSON.parse(await fs.readFile(this.catalogPath, 'utf8'));
    this.agentConfig = catalog.agents.find(a => a.agent_id === this.agentId);

    if (!this.agentConfig) {
      throw new Error(`Agent ${this.agentId} not found in catalog`);
    }

    console.log(`✓ Loaded configuration for ${this.agentId}`);
    console.log(`  Role: ${this.agentConfig.role}`);
    console.log(`  Category: ${this.agentConfig.category}\n`);
  }

  async watchForTasks() {
    while (this.running) {
      try {
        // Check pending directory for tasks assigned to this agent
        const pendingDir = path.join(this.tasksDir, 'pending');
        const files = await fs.readdir(pendingDir);

        for (const file of files) {
          const taskPath = path.join(pendingDir, file);
          const task = JSON.parse(await fs.readFile(taskPath, 'utf8'));

          if (task.agent_id === this.agentId) {
            await this.processTask(task, file);
          }
        }
      } catch (error) {
        // Directory might not exist or be empty
      }

      // Wait before checking again
      await this.sleep(2000);
    }
  }

  async processTask(task, filename) {
    console.log(`\n${'='.repeat(60)}`);
    console.log(`📋 NEW TASK: ${task.task_id}`);
    console.log(`${'='.repeat(60)}\n`);

    try {
      // Move to in_progress
      const pendingPath = path.join(this.tasksDir, 'pending', filename);
      const inProgressPath = path.join(this.tasksDir, 'in_progress', filename);
      await fs.rename(pendingPath, inProgressPath);

      // Build the prompt
      const prompt = this.buildPrompt(task.inputs);

      console.log('AGENT PROMPT:');
      console.log('─'.repeat(60));
      console.log(prompt);
      console.log('─'.repeat(60));
      console.log('\n📝 Please provide the agent response as JSON:');
      console.log('   (Paste the complete JSON output below)\n');

      // Wait for user to provide response
      const response = await this.getUserInput();

      // Parse and validate response
      let output;
      try {
        output = JSON.parse(response);
      } catch (e) {
        // Try to extract JSON from code blocks
        const jsonMatch = response.match(/```json\n([\s\S]*?)\n```/);
        if (jsonMatch) {
          output = JSON.parse(jsonMatch[1]);
        } else {
          output = { raw: response };
        }
      }

      // Save output
      const outputPath = path.join(this.outputsDir, `${task.task_id}_output.json`);
      await fs.writeFile(outputPath, JSON.stringify(output, null, 2));

      // Move to completed
      const completedPath = path.join(this.tasksDir, 'completed', filename);
      task.completed_at = new Date().toISOString();
      task.output = output;
      await fs.writeFile(completedPath, JSON.stringify(task, null, 2));
      await fs.unlink(inProgressPath);

      console.log(`\n✓ Task completed successfully!\n`);
      console.log('Watching for next task...\n');

    } catch (error) {
      console.error(`\n✗ Task failed: ${error.message}\n`);

      // Move to failed
      const failedPath = path.join(this.tasksDir, 'failed', filename);
      task.failed_at = new Date().toISOString();
      task.error = error.message;
      await fs.writeFile(failedPath, JSON.stringify(task, null, 2));

      try {
        const inProgressPath = path.join(this.tasksDir, 'in_progress', filename);
        await fs.unlink(inProgressPath);
      } catch {}
    }
  }

  buildPrompt(inputs) {
    let prompt = this.agentConfig.prompt_template;

    // Map common input name variations
    const inputMappings = {
      'sources': 'source_content',
      'documentType': 'document_type',
      'rawFacts': 'raw_facts',
      'additionalSources': 'source_list',
      'facts': 'verified_facts',
      'unitType': 'unit_type',
      'doctrines': 'doctrine_sources',
      'unit': 'unit_designation',
      'parent': 'parent_unit',
      'modifications': 'modifications',
      'theaterSCM': 'theater_scm',
      'orgTree': 'division_list',
      'divisionEquipment': 'division_equipment',
      'subordinates': 'org_structure',
      'distributionDoctrine': 'doctrine',
      'allUnits': 'unit_files',
      'squadFiles': 'squad_files',
      'chapterType': 'chapter_type',
      'format': 'format'
    };

    for (const [key, value] of Object.entries(inputs)) {
      const replacement = typeof value === 'object'
        ? JSON.stringify(value, null, 2)
        : String(value);

      // Try original key name
      prompt = prompt.replace(new RegExp(`\\{${key}\\}`, 'g'), replacement);

      // Try mapped name
      if (inputMappings[key]) {
        prompt = prompt.replace(new RegExp(`\\{${inputMappings[key]}\\}`, 'g'), replacement);
      }
    }

    return prompt;
  }

  async getUserInput() {
    return new Promise((resolve) => {
      const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
      });

      let input = '';
      let collecting = false;

      console.log('Enter response (type END_JSON on a new line when done):');

      rl.on('line', (line) => {
        if (line.trim() === 'END_JSON') {
          rl.close();
          resolve(input);
        } else {
          if (!collecting && (line.trim().startsWith('{') || line.trim().startsWith('```'))) {
            collecting = true;
          }
          input += line + '\n';
        }
      });
    });
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  stop() {
    this.running = false;
    console.log('\n🛑 Agent runner stopped\n');
  }
}

// CLI usage
if (require.main === module) {
  const agentId = process.argv[2];

  if (!agentId) {
    console.error('Usage: node agent_runner.js <agent_id>');
    console.error('\nExample: node agent_runner.js document_parser');
    console.error('\nAvailable agents:');
    console.error('  - document_parser');
    console.error('  - historical_research');
    console.error('  - org_hierarchy');
    console.error('  - toe_template');
    console.error('  - unit_instantiation');
    process.exit(1);
  }

  const runner = new AgentRunner(agentId);

  // Handle Ctrl+C
  process.on('SIGINT', () => {
    runner.stop();
    process.exit(0);
  });

  runner.initialize().then(() => {
    return runner.watchForTasks();
  }).catch(error => {
    console.error('Fatal error:', error.message);
    process.exit(1);
  });
}

module.exports = { AgentRunner };
