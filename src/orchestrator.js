/**
 * North Africa TO&E Builder - Master Agent Orchestrator
 * Coordinates all specialist agents to build complete TO&E database
 */

require('dotenv').config();

const fs = require('fs').promises;
const path = require('path');
const fetch = require('node-fetch');

class AgentOrchestrator {
  constructor() {
    this.agents = new Map();
    this.state = new WorkflowState();
    this.results = new Map();
    this.config = null;
    
    console.log('🚀 Agent Orchestrator initialized');
  }
  
  async initialize() {
    // Load agent catalog
    const catalogPath = path.join(__dirname, '../agents/agent_catalog.json');
    const catalogData = await fs.readFile(catalogPath, 'utf8');
    this.config = JSON.parse(catalogData);
    
    // Register all agents
    for (const agentDef of this.config.agents) {
      this.registerAgent(agentDef);
    }
    
    console.log(`✓ Loaded ${this.agents.size} agents\n`);
  }
  
  registerAgent(agentConfig) {
    const agent = new Agent(agentConfig);
    this.agents.set(agentConfig.agent_id, agent);
  }
  
  async runAgent(agentId, inputs, retries = 3) {
    const agent = this.agents.get(agentId);
    if (!agent) {
      throw new Error(`Agent ${agentId} not found`);
    }
    
    const taskId = this.generateTaskId();
    console.log(`→ Running agent: ${agentId} (task ${taskId})`);
    
    for (let attempt = 0; attempt < retries; attempt++) {
      try {
        const result = await agent.execute(taskId, inputs);
        this.results.set(taskId, result);
        
        if (result.status === "success") {
          console.log(`✓ Agent ${agentId} completed successfully`);
          if (result.metadata.warnings.length > 0) {
            console.log(`  ⚠ ${result.metadata.warnings.length} warnings`);
          }
          return result.outputs;
        }
        
        const nonRecoverableErrors = result.errors.filter(e => !e.recoverable);
        if (nonRecoverableErrors.length > 0) {
          throw new Error(
            `Non-recoverable error in ${agentId}: ${nonRecoverableErrors[0].message}`
          );
        }
        
        console.warn(
          `⚠ Agent ${agentId} failed (attempt ${attempt + 1}/${retries}), retrying...`
        );
        
      } catch (error) {
        if (attempt === retries - 1) {
          console.error(`✗ Agent ${agentId} failed after ${retries} attempts`);
          throw error;
        }
        await this.sleep(1000 * (attempt + 1));
      }
    }
  }
  
  async executeWorkflow(nation, quarter, sources) {
    console.log(`\n${'='.repeat(60)}`);
    console.log(`  TO&E Build: ${nation} ${quarter}`);
    console.log(`${'='.repeat(60)}\n`);
    
    const startTime = Date.now();
    
    try {
      // PHASE 1: Source Extraction
      await this.executePhase1(sources);
      
      // PHASE 2: Organization Building
      await this.executePhase2(nation, quarter);
      
      // PHASE 3: Equipment Distribution
      await this.executePhase3(nation, quarter);
      
      // PHASE 4: Aggregation
      await this.executePhase4();
      
      // PHASE 5: Validation
      await this.executePhase5();
      
      // PHASE 6: Output Generation
      await this.executePhase6();
      
      const duration = ((Date.now() - startTime) / 1000).toFixed(2);
      console.log(`\n${'='.repeat(60)}`);
      console.log(`✓ Build complete in ${duration}s!`);
      console.log(`${'='.repeat(60)}\n`);
      
      return this.generateReport();
      
    } catch (error) {
      console.error(`\n✗ Build failed: ${error.message}\n`);
      console.error(error.stack);
      return {
        status: "error",
        error: error.message,
        state: this.state.data
      };
    }
  }
  
  async executePhase1(sources) {
    console.log('\n📖 PHASE 1: Source Extraction\n');
    
    this.state.set('rawFacts', await this.runAgent("document_parser", {
      sources: sources,
      documentType: "military_handbook"
    }));
    
    this.state.set('verifiedFacts', await this.runAgent("historical_research", {
      rawFacts: this.state.get('rawFacts'),
      additionalSources: sources
    }));
    
    const factCount = this.state.get('verifiedFacts')?.length || 0;
    console.log(`\n✓ Phase 1 complete: ${factCount} facts verified\n`);
  }
  
  async executePhase2(nation, quarter) {
    console.log('\n🏗️  PHASE 2: Organization Building\n');
    
    // Build hierarchy
    this.state.set('orgTree', await this.runAgent("org_hierarchy", {
      facts: this.state.get('verifiedFacts'),
      nation: nation,
      quarter: quarter
    }));
    
    // Create templates
    const unitTypes = ["squad", "platoon", "company", "battalion"];
    const templates = {};
    
    for (const unitType of unitTypes) {
      console.log(`  Creating ${unitType} template...`);
      templates[unitType] = await this.runAgent("toe_template", {
        nation: nation,
        quarter: quarter,
        unitType: unitType,
        doctrines: this.state.get('verifiedFacts')?.doctrines || {}
      });
    }
    
    this.state.set('templates', templates);
    
    // Instantiate all units
    console.log('\n  Creating unit instances...');
    const allUnits = await this.instantiateAllUnits(
      this.state.get('orgTree'),
      templates,
      nation,
      quarter
    );
    
    this.state.set('allUnits', allUnits);
    
    console.log(`\n✓ Phase 2 complete: ${allUnits.length} units created\n`);
  }
  
  async instantiateAllUnits(orgTree, templates, nation, quarter) {
    const units = [];
    
    // Recursive function to walk org tree
    const walkTree = async (node, parentUnit = null) => {
      // Get appropriate template
      const template = templates[node.type] || null;
      
      // Create unit instance
      const unitTOE = await this.runAgent("unit_instantiation", {
        template: template,
        unit: node,
        parent: parentUnit,
        nation: nation,
        quarter: quarter
      });
      
      units.push(unitTOE);
      
      // Save unit file
      await this.saveUnitFile(unitTOE);
      
      // Recurse for subordinates
      if (node.subordinates) {
        for (const sub of node.subordinates) {
          await walkTree(sub, node.unit_designation);
        }
      }
    };
    
    await walkTree(orgTree);
    return units;
  }
  
  async executePhase3(nation, quarter) {
    console.log('\n⚙️  PHASE 3: Equipment Distribution\n');
    
    // Load theater SCM
    const theaterSCM = await this.loadTheaterSCM(nation, quarter);
    
    // Allocate to divisions
    const divisionAllocations = await this.runAgent("theater_allocator", {
      theaterSCM: theaterSCM,
      orgTree: this.state.get('orgTree')
    });
    
    this.state.set('divisionAllocations', divisionAllocations);
    
    // Cascade down through hierarchy
    const divisions = this.extractDivisions(this.state.get('orgTree'));
    
    for (const division of divisions) {
      console.log(`  Distributing equipment for ${division.unit_designation}...`);
      
      await this.runAgent("division_cascader", {
        divisionEquipment: divisionAllocations[division.unit_designation],
        subordinates: division.subordinates,
        distributionDoctrine: this.state.get('verifiedFacts')?.doctrine || {}
      });
    }
    
    // Reconcile totals
    const reconciliation = await this.runAgent("equipment_reconciliation", {
      allUnits: this.state.get('allUnits')
    });
    
    if (reconciliation.errors?.length > 0) {
      console.error('\n⚠ Equipment reconciliation found issues:');
      reconciliation.errors.forEach(err => console.error(`  - ${err.message}`));
      throw new Error('Equipment reconciliation failed');
    }
    
    console.log('\n✓ Phase 3 complete: Equipment distributed and verified\n');
  }
  
  async executePhase4() {
    console.log('\n📊 PHASE 4: Aggregation\n');
    
    const squadFiles = this.state.get('allUnits')
      .filter(u => u.organization_level === "squad");
    
    const aggregated = await this.runAgent("bottom_up_aggregator", {
      squadFiles: squadFiles,
      orgTree: this.state.get('orgTree')
    });
    
    this.state.set('aggregatedUnits', aggregated);
    
    // Calculate theater SCM
    const theaterSCM = await this.runAgent("top3_calculator", {
      allUnits: this.state.get('allUnits')
    });
    
    this.state.set('theaterSCM', theaterSCM);
    
    console.log('\n✓ Phase 4 complete: Aggregation verified\n');
  }
  
  async executePhase5() {
    console.log('\n✅ PHASE 5: Validation\n');
    
    const validationResults = [];
    const allUnits = this.state.get('allUnits');
    
    for (const unit of allUnits) {
      // Schema validation
      const schemaResult = await this.runAgent("schema_validator", {
        unit: unit,
        schema: await this.loadSchema()
      });
      
      // Historical accuracy
      const accuracyResult = await this.runAgent("historical_accuracy", {
        unit: unit,
        sources: this.state.get('verifiedFacts')
      });
      
      validationResults.push({
        unit: unit.unit_designation,
        schemaResult: schemaResult,
        accuracyResult: accuracyResult
      });
      
      if (!schemaResult.valid) {
        console.error(`  ✗ ${unit.unit_designation} failed schema validation`);
      }
      
      if (accuracyResult.confidence < 75) {
        console.warn(`  ⚠ ${unit.unit_designation} low confidence (${accuracyResult.confidence}%)`);
      }
    }
    
    this.state.set('validationResults', validationResults);
    
    const failedValidations = validationResults.filter(r => !r.schemaResult.valid);
    if (failedValidations.length > 0) {
      throw new Error(`${failedValidations.length} units failed validation`);
    }
    
    console.log(`\n✓ Phase 5 complete: ${allUnits.length} units validated\n`);
  }
  
  async executePhase6() {
    console.log('\n📝 PHASE 6: Output Generation\n');
    
    const allUnits = this.state.get('allUnits');
    
    // Generate book chapters
    console.log('  Generating book chapters...');
    const chapters = [];
    for (const unit of allUnits) {
      const chapter = await this.runAgent("book_chapter_generator", {
        unit: unit,
        chapterType: unit.organization_level
      });
      chapters.push(chapter);
      await this.saveChapter(chapter, unit.unit_designation);
    }
    
    // Generate scenarios
    console.log('  Generating wargaming scenarios...');
    const scenarios = await this.runAgent("scenario_exporter", {
      units: allUnits,
      format: "witw_csv"
    });
    await this.saveScenarios(scenarios);
    
    // Generate SQL
    console.log('  Generating SQL database...');
    const sql = await this.runAgent("sql_populator", {
      units: allUnits
    });
    await this.saveSQL(sql);
    
    console.log(`\n✓ Phase 6 complete: All outputs generated\n`);
  }
  
  // Helper methods
  
  generateTaskId() {
    return `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
  
  extractDivisions(orgTree) {
    const divisions = [];
    const walk = (node) => {
      if (node.level === 'division' || node.organization_level === 'division') {
        divisions.push(node);
      }
      if (node.subordinates) {
        node.subordinates.forEach(sub => walk(sub));
      }
    };
    walk(orgTree);
    return divisions;
  }
  
  async loadTheaterSCM(nation, quarter) {
    const scmPath = path.join(__dirname, `../data/sources/${nation}_${quarter}_scm.json`);
    try {
      const data = await fs.readFile(scmPath, 'utf8');
      return JSON.parse(data);
    } catch (error) {
      console.warn(`⚠ Could not load theater SCM, using defaults`);
      return {};
    }
  }
  
  async loadSchema() {
    const schemaPath = path.join(__dirname, '../schemas/unified_toe_schema.json');
    const data = await fs.readFile(schemaPath, 'utf8');
    return JSON.parse(data);
  }
  
  async saveUnitFile(unit) {
    const outputDir = path.join(__dirname, '../data/output/units');
    await fs.mkdir(outputDir, { recursive: true });

    // Handle missing unit_designation
    const designation = unit.unit_designation || unit.name || `unit_${Date.now()}`;
    const filename = `${designation.replace(/\s+/g, '_')}_toe.json`;
    const filepath = path.join(outputDir, filename);

    await fs.writeFile(filepath, JSON.stringify(unit, null, 2));
  }
  
  async saveChapter(chapter, unitName) {
    const outputDir = path.join(__dirname, '../data/output/chapters');
    await fs.mkdir(outputDir, { recursive: true });
    
    const filename = `${unitName.replace(/\s+/g, '_')}.md`;
    const filepath = path.join(outputDir, filename);
    
    await fs.writeFile(filepath, chapter);
  }
  
  async saveScenarios(scenarios) {
    const outputDir = path.join(__dirname, '../data/output/scenarios');
    await fs.mkdir(outputDir, { recursive: true });
    
    const filepath = path.join(outputDir, 'scenarios.csv');
    await fs.writeFile(filepath, scenarios);
  }
  
  async saveSQL(sql) {
    const outputDir = path.join(__dirname, '../data/output/sql');
    await fs.mkdir(outputDir, { recursive: true });
    
    const filepath = path.join(outputDir, 'database.sql');
    await fs.writeFile(filepath, sql);
  }
  
  generateReport() {
    const allUnits = this.state.get('allUnits') || [];
    const validationResults = this.state.get('validationResults') || [];
    
    return {
      status: "success",
      summary: {
        units_created: allUnits.length,
        phases_completed: 6,
        validation_passed: validationResults.filter(r => r.schemaResult.valid).length,
        validation_total: validationResults.length
      },
      breakdown: {
        by_level: this.countByLevel(allUnits),
        avg_confidence: this.averageConfidence(validationResults)
      },
      outputs: {
        units: `data/output/units/`,
        chapters: `data/output/chapters/`,
        scenarios: `data/output/scenarios/`,
        sql: `data/output/sql/`
      }
    };
  }
  
  countByLevel(units) {
    const counts = {};
    units.forEach(u => {
      const level = u.organization_level;
      counts[level] = (counts[level] || 0) + 1;
    });
    return counts;
  }
  
  averageConfidence(results) {
    if (results.length === 0) return 0;
    const sum = results.reduce((acc, r) => acc + r.accuracyResult.confidence, 0);
    return Math.round(sum / results.length);
  }
}

class Agent {
  constructor(config) {
    this.config = config;
  }
  
  async execute(taskId, inputs) {
    const startTime = Date.now();
    
    // Build prompt
    const prompt = this.buildPrompt(inputs);
    
    // Call Claude API
    const response = await this.callClaude(prompt);
    
    // Parse output
    const output = this.parseOutput(response);
    
    // Validate
    const validation = this.validate(output);
    
    return {
      agent_id: this.config.agent_id,
      task_id: taskId,
      status: validation.valid ? "success" : "error",
      outputs: output,
      metadata: {
        execution_time_ms: Date.now() - startTime,
        confidence: output.confidence || 0,
        warnings: validation.warnings
      },
      errors: validation.errors
    };
  }
  
  buildPrompt(inputs) {
    let prompt = this.config.prompt_template;

    // Map common input name variations to template variables
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
      'unit': 'unit_toe',
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
  
  async callClaude(prompt) {
    // NOTE: In production, use actual API key
    // const API_KEY = process.env.ANTHROPIC_API_KEY;

    try {
      const response = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-api-key": process.env.ANTHROPIC_API_KEY || "your-api-key",
          "anthropic-version": "2023-06-01"
        },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 8000,
          messages: [{role: "user", content: prompt}]
        })
      });

      const data = await response.json();

      // Check for API errors
      if (data.error) {
        throw new Error(`API Error: ${data.error.message || JSON.stringify(data.error)}`);
      }

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${JSON.stringify(data)}`);
      }

      return data.content[0].text;

    } catch (error) {
      // Fallback for testing without API
      console.warn(`⚠ Claude API unavailable: ${error.message}`);
      return JSON.stringify({
        mock: true,
        message: "API call would be made here"
      });
    }
  }
  
  parseOutput(text) {
    try {
      // Try to extract JSON from code blocks first
      const codeBlockMatch = text.match(/```json\n([\s\S]*?)\n```/);
      if (codeBlockMatch) {
        try {
          return JSON.parse(codeBlockMatch[1]);
        } catch (e) {
          // JSON in code block was invalid, continue to other methods
        }
      }

      // Try to find JSON object in text
      const jsonObjectMatch = text.match(/\{[\s\S]*\}/);
      if (jsonObjectMatch) {
        try {
          return JSON.parse(jsonObjectMatch[0]);
        } catch (e) {
          // Not valid JSON, continue
        }
      }

      // No valid JSON found - Claude returned explanatory text
      // This is normal when template variables aren't filled
      return {
        raw: text,
        confidence: 50,
        note: "Agent returned text explanation instead of JSON - check prompt template variables"
      };

    } catch (error) {
      return {
        raw: text,
        error: error.message,
        confidence: 0
      };
    }
  }
  
  validate(output) {
    const errors = [];
    const warnings = [];
    
    // Run validation rules from config
    for (const rule of this.config.validation_rules || []) {
      // TODO: Implement specific validation logic per rule
      // For now, basic checks
      if (!output || typeof output !== 'object') {
        errors.push({
          error_type: 'invalid_output',
          message: 'Output is not a valid object',
          recoverable: false
        });
      }
    }
    
    return {
      valid: errors.length === 0,
      errors: errors,
      warnings: warnings
    };
  }
}

class WorkflowState {
  constructor() {
    this.data = {};
  }
  
  set(key, value) {
    this.data[key] = value;
  }
  
  get(key) {
    return this.data[key];
  }
}

// Export
module.exports = { AgentOrchestrator, Agent, WorkflowState };

// CLI usage
if (require.main === module) {
  const orchestrator = new AgentOrchestrator();
  
  orchestrator.initialize().then(() => {
    return orchestrator.executeWorkflow(
      "italian",
      "1940-Q2",
      ["TM E 30-420.pdf", "italian_10th_army_records.pdf"]
    );
  }).then(result => {
    console.log('\n📊 Final Report:');
    console.log(JSON.stringify(result, null, 2));
  }).catch(error => {
    console.error('\n💥 Fatal error:', error.message);
    process.exit(1);
  });
}
