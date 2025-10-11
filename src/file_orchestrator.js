/**
 * File-Based Multi-Agent Orchestrator
 * Coordinates agents via file system - no API calls required
 * Each agent runs in separate Claude Code terminal session
 */

const fs = require('fs').promises;
const path = require('path');

class FileOrchestrator {
  constructor() {
    this.tasksDir = path.join(__dirname, '../tasks');
    this.outputsDir = path.join(__dirname, '../outputs');
    this.state = {
      currentPhase: 0,
      nation: null,
      quarter: null,
      completedTasks: [],
      failedTasks: []
    };

    console.log('🗂️  File-Based Orchestrator initialized');
  }

  async initialize(nation, quarter) {
    this.state.nation = nation;
    this.state.quarter = quarter;

    // Clear old tasks
    await this.clearDirectory(path.join(this.tasksDir, 'pending'));
    await this.clearDirectory(path.join(this.tasksDir, 'in_progress'));
    await this.clearDirectory(path.join(this.tasksDir, 'completed'));

    console.log(`\n${'='.repeat(60)}`);
    console.log(`  TO&E Build: ${nation} ${quarter}`);
    console.log(`  Mode: File-Based Multi-Agent (No API)`);
    console.log(`${'='.repeat(60)}\n`);
  }

  async clearDirectory(dir) {
    try {
      const files = await fs.readdir(dir);
      for (const file of files) {
        await fs.unlink(path.join(dir, file));
      }
    } catch (error) {
      // Directory might not exist or be empty
    }
  }

  async createTask(agentId, inputs, dependencies = []) {
    const taskId = `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    const task = {
      task_id: taskId,
      agent_id: agentId,
      inputs: inputs,
      dependencies: dependencies,
      created_at: new Date().toISOString(),
      status: 'pending'
    };

    const taskFile = path.join(this.tasksDir, 'pending', `${taskId}.json`);
    await fs.writeFile(taskFile, JSON.stringify(task, null, 2));

    console.log(`📝 Created task: ${agentId} (${taskId})`);
    return taskId;
  }

  async waitForTask(taskId, timeoutMs = 600000) {
    const startTime = Date.now();

    while (Date.now() - startTime < timeoutMs) {
      // Check if task is completed
      const completedFile = path.join(this.tasksDir, 'completed', `${taskId}.json`);
      const failedFile = path.join(this.tasksDir, 'failed', `${taskId}.json`);

      try {
        if (await this.fileExists(completedFile)) {
          const result = JSON.parse(await fs.readFile(completedFile, 'utf8'));
          console.log(`✓ Task completed: ${result.agent_id}`);
          this.state.completedTasks.push(taskId);

          // Read the output
          const outputFile = path.join(this.outputsDir, `${taskId}_output.json`);
          if (await this.fileExists(outputFile)) {
            return JSON.parse(await fs.readFile(outputFile, 'utf8'));
          }
          return result.output;
        }

        if (await this.fileExists(failedFile)) {
          const error = JSON.parse(await fs.readFile(failedFile, 'utf8'));
          console.error(`✗ Task failed: ${error.agent_id} - ${error.error}`);
          this.state.failedTasks.push(taskId);
          throw new Error(`Task ${taskId} failed: ${error.error}`);
        }
      } catch (error) {
        if (error.message.startsWith('Task')) throw error;
      }

      // Wait before checking again
      await this.sleep(2000);
    }

    throw new Error(`Task ${taskId} timed out after ${timeoutMs}ms`);
  }

  async fileExists(filePath) {
    try {
      await fs.access(filePath);
      return true;
    } catch {
      return false;
    }
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async executePhase1(sources) {
    console.log('\n📖 PHASE 1: Source Extraction\n');

    // Task 1: Document Parser
    const task1 = await this.createTask('document_parser', {
      sources: sources,
      documentType: 'military_handbook',
      nation: this.state.nation,
      quarter: this.state.quarter
    });

    const rawFacts = await this.waitForTask(task1);

    // Task 2: Historical Research
    const task2 = await this.createTask('historical_research', {
      rawFacts: rawFacts,
      additionalSources: sources
    }, [task1]);

    const verifiedFacts = await this.waitForTask(task2);

    console.log(`\n✓ Phase 1 complete: Facts extracted and verified\n`);
    return { rawFacts, verifiedFacts };
  }

  async executePhase2(verifiedFacts) {
    console.log('\n🏗️  PHASE 2: Organization Building\n');

    // Task 1: Build hierarchy
    const task1 = await this.createTask('org_hierarchy', {
      facts: verifiedFacts,
      nation: this.state.nation,
      quarter: this.state.quarter
    });

    const orgTree = await this.waitForTask(task1);

    // Tasks 2-5: Create templates (can run in parallel)
    console.log('  Creating unit templates...');
    const templateTasks = [];
    const unitTypes = ['squad', 'platoon', 'company', 'battalion'];

    for (const unitType of unitTypes) {
      const taskId = await this.createTask('toe_template', {
        nation: this.state.nation,
        quarter: this.state.quarter,
        unitType: unitType,
        doctrines: verifiedFacts?.doctrines || {}
      }, [task1]);
      templateTasks.push({ type: unitType, taskId });
    }

    // Wait for all templates
    const templates = {};
    for (const { type, taskId } of templateTasks) {
      templates[type] = await this.waitForTask(taskId);
    }

    // Task 6: Instantiate units
    console.log('\n  Creating unit instances...');
    const task6 = await this.createTask('unit_instantiation', {
      template: templates,
      orgTree: orgTree,
      nation: this.state.nation,
      quarter: this.state.quarter
    }, templateTasks.map(t => t.taskId));

    const allUnits = await this.waitForTask(task6);

    console.log(`\n✓ Phase 2 complete: Organization built\n`);
    return { orgTree, templates, allUnits };
  }

  async executeWorkflow(nation, quarter, sources) {
    await this.initialize(nation, quarter);

    try {
      // Phase 1: Source Extraction
      const phase1 = await this.executePhase1(sources);

      // Phase 2: Organization Building
      const phase2 = await this.executePhase2(phase1.verifiedFacts);

      // Phases 3-6 would continue here...
      console.log('\n⚠️  Phases 3-6 not yet implemented in file-based mode');

      console.log(`\n${'='.repeat(60)}`);
      console.log(`✓ File-based workflow complete!`);
      console.log(`  Completed tasks: ${this.state.completedTasks.length}`);
      console.log(`  Failed tasks: ${this.state.failedTasks.length}`);
      console.log(`${'='.repeat(60)}\n`);

      return {
        status: 'success',
        completed: this.state.completedTasks.length,
        failed: this.state.failedTasks.length
      };

    } catch (error) {
      console.error(`\n✗ Workflow failed: ${error.message}\n`);
      return {
        status: 'error',
        error: error.message,
        completed: this.state.completedTasks.length,
        failed: this.state.failedTasks.length
      };
    }
  }
}

// CLI usage
if (require.main === module) {
  const orchestrator = new FileOrchestrator();

  orchestrator.executeWorkflow(
    'italian',
    '1940-Q2',
    ['TM E 30-420.pdf', 'italian_10th_army_records.pdf']
  ).then(result => {
    console.log('\n📊 Final Result:');
    console.log(JSON.stringify(result, null, 2));
    process.exit(result.status === 'success' ? 0 : 1);
  }).catch(error => {
    console.error('\n💥 Fatal error:', error.message);
    process.exit(1);
  });
}

module.exports = { FileOrchestrator };
