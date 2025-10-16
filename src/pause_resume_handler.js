/**
 * Pause/Resume Handler for Exhaustive Search Protocol v3.2.0
 *
 * Handles human-in-the-loop collaboration by:
 * 1. Detecting when agent has paused (awaiting_user_guidance)
 * 2. Presenting findings to user
 * 3. Awaiting user's direct instruction
 * 4. Resuming extraction based on user guidance
 *
 * Part of Agent Catalog v3.2.0 - Exhaustive Search + Human-in-Loop
 */

const fs = require('fs').promises;
const path = require('path');

class PauseResumeHandler {
  constructor() {
    this.pausedUnitsPath = path.join(__dirname, '../data/paused_units.json');
  }

  /**
   * Check if agent response contains pause signal
   * @param {Object} agentResponse - Response from historical_research agent
   * @returns {Boolean} True if agent is awaiting user guidance
   */
  isPaused(agentResponse) {
    return (
      agentResponse &&
      agentResponse.awaiting_user_guidance &&
      agentResponse.awaiting_user_guidance.status === 'PAUSED'
    );
  }

  /**
   * Extract pause information from agent response
   * @param {Object} agentResponse - Response from historical_research agent
   * @param {Object} unitInfo - Unit being processed
   * @returns {Object} Pause information for user
   */
  extractPauseInfo(agentResponse, unitInfo) {
    const awaitingGuidance = agentResponse.awaiting_user_guidance || {};
    const exhaustiveSearch = agentResponse.exhaustive_search_report || {};

    return {
      unit: unitInfo,
      paused_at: new Date().toISOString(),
      reason: awaitingGuidance.reason || 'Exhaustive search complete, awaiting user guidance',

      // Exhaustive search results
      sources_checked: {
        tier1: exhaustiveSearch.tier1_sources_checked || [],
        tier2: exhaustiveSearch.tier2_sources_checked || [],
        tier3: exhaustiveSearch.tier3_sources_checked || []
      },

      // Critical gaps identified
      gaps: exhaustiveSearch.critical_gaps_identified || [],

      // Data summary
      data_summary: exhaustiveSearch.data_summary || {},

      // Question and options for user
      question: awaitingGuidance.question_for_user || 'How would you like to proceed?',
      context: awaitingGuidance.user_options_context || 'Provide direct instruction',

      // Research results (for context)
      research_results: agentResponse.research_results || {}
    };
  }

  /**
   * Save paused unit to disk for later resume
   * @param {Object} pauseInfo - Pause information
   */
  async savePausedUnit(pauseInfo) {
    try {
      // Load existing paused units
      let pausedUnits = [];
      try {
        const data = await fs.readFile(this.pausedUnitsPath, 'utf-8');
        pausedUnits = JSON.parse(data);
      } catch (error) {
        // File doesn't exist yet, start fresh
        pausedUnits = [];
      }

      // Add new paused unit
      pausedUnits.push(pauseInfo);

      // Save back to disk
      await fs.writeFile(this.pausedUnitsPath, JSON.stringify(pausedUnits, null, 2));

      console.log(`\n⏸️  Unit paused and saved: ${pauseInfo.unit.nation} ${pauseInfo.unit.unit_designation} ${pauseInfo.unit.quarter}`);
    } catch (error) {
      console.error(`❌ Failed to save paused unit: ${error.message}`);
    }
  }

  /**
   * Present pause information to user
   * @param {Object} pauseInfo - Pause information
   */
  presentToUser(pauseInfo) {
    console.log('\n' + '='.repeat(80));
    console.log('⏸️  AGENT PAUSED - AWAITING USER GUIDANCE');
    console.log('='.repeat(80));

    console.log(`\n📋 Unit: ${pauseInfo.unit.nation} ${pauseInfo.unit.unit_designation} (${pauseInfo.unit.quarter})`);
    console.log(`\n❓ Reason: ${pauseInfo.reason}`);

    // Show exhaustive search summary
    console.log('\n🔍 EXHAUSTIVE SEARCH COMPLETED:');
    console.log(`   • Tier 1 sources checked: ${pauseInfo.sources_checked.tier1.length}`);
    console.log(`   • Tier 2 sources checked: ${pauseInfo.sources_checked.tier2.length}`);
    console.log(`   • Tier 3 sources checked: ${pauseInfo.sources_checked.tier3.length}`);

    // Show data summary
    const summary = pauseInfo.data_summary;
    if (summary.fields_verified || summary.fields_estimated || summary.fields_unknown) {
      console.log('\n📊 DATA SUMMARY:');
      if (summary.fields_verified) {
        console.log(`   ✅ Verified: ${summary.fields_verified.join(', ')}`);
      }
      if (summary.fields_estimated) {
        console.log(`   📐 Estimated: ${summary.fields_estimated.join(', ')}`);
      }
      if (summary.fields_unknown) {
        console.log(`   ❌ Unknown: ${summary.fields_unknown.join(', ')}`);
      }
      if (summary.overall_confidence) {
        console.log(`   🎯 Overall confidence: ${summary.overall_confidence}%`);
      }
    }

    // Show critical gaps
    if (pauseInfo.gaps && pauseInfo.gaps.length > 0) {
      console.log('\n⚠️  CRITICAL GAPS IDENTIFIED:');
      for (const gap of pauseInfo.gaps) {
        console.log(`\n   Field: ${gap.field}`);
        console.log(`   Status: ${gap.status}`);
        console.log(`   Sources tried: ${gap.sources_tried}`);
        console.log(`   Reason: ${gap.reason}`);

        if (gap.potential_next_steps && gap.potential_next_steps.length > 0) {
          console.log(`   \n   💡 Potential next steps:`);
          gap.potential_next_steps.forEach((step, i) => {
            console.log(`      ${i + 1}. ${step}`);
          });
        }
      }
    }

    // Show question to user
    console.log('\n' + '-'.repeat(80));
    console.log('❓ QUESTION FOR USER:');
    console.log('-'.repeat(80));
    console.log(pauseInfo.question);

    // Show context
    console.log('\n' + '-'.repeat(80));
    console.log('💬 CONTEXT:');
    console.log('-'.repeat(80));
    console.log(pauseInfo.context);

    console.log('\n' + '='.repeat(80));
    console.log('⏳ Unit saved to: data/paused_units.json');
    console.log('📝 You can provide guidance by:');
    console.log('   1. Running: npm run resume -- [unit_id]');
    console.log('   2. Providing direct instruction when prompted');
    console.log('='.repeat(80) + '\n');
  }

  /**
   * Get all paused units
   * @returns {Array} List of paused units
   */
  async getPausedUnits() {
    try {
      const data = await fs.readFile(this.pausedUnitsPath, 'utf-8');
      return JSON.parse(data);
    } catch (error) {
      return [];
    }
  }

  /**
   * Resume a paused unit with user guidance
   * @param {String} unitId - Unit identifier
   * @param {String} userGuidance - User's direct instruction
   * @returns {Object} Updated pause info with user guidance
   */
  async resume(unitId, userGuidance) {
    const pausedUnits = await this.getPausedUnits();

    // Find the paused unit
    const unitIndex = pausedUnits.findIndex(u => {
      const id = `${u.unit.nation}_${u.unit.quarter}_${u.unit.unit_designation}`;
      return id === unitId;
    });

    if (unitIndex === -1) {
      throw new Error(`Paused unit not found: ${unitId}`);
    }

    const pausedUnit = pausedUnits[unitIndex];

    // Add user guidance
    pausedUnit.user_guidance = {
      instruction: userGuidance,
      provided_at: new Date().toISOString()
    };

    // Remove from paused list
    pausedUnits.splice(unitIndex, 1);
    await fs.writeFile(this.pausedUnitsPath, JSON.stringify(pausedUnits, null, 2));

    console.log(`\n▶️  Resuming unit with user guidance: ${pausedUnit.unit.nation} ${pausedUnit.unit.unit_designation}`);
    console.log(`   User instruction: ${userGuidance}\n`);

    return pausedUnit;
  }

  /**
   * List all paused units (for CLI command)
   */
  async listPausedUnits() {
    const pausedUnits = await this.getPausedUnits();

    if (pausedUnits.length === 0) {
      console.log('\n✅ No paused units\n');
      return;
    }

    console.log('\n' + '='.repeat(80));
    console.log(`⏸️  PAUSED UNITS (${pausedUnits.length})`);
    console.log('='.repeat(80) + '\n');

    for (const [index, unit] of pausedUnits.entries()) {
      console.log(`${index + 1}. ${unit.unit.nation} ${unit.unit.unit_designation} (${unit.unit.quarter})`);
      console.log(`   Paused: ${unit.paused_at}`);
      console.log(`   Reason: ${unit.reason}`);

      if (unit.gaps && unit.gaps.length > 0) {
        console.log(`   Gaps: ${unit.gaps.map(g => g.field).join(', ')}`);
      }

      console.log();
    }

    console.log('='.repeat(80));
    console.log('To resume a unit: npm run resume -- [unit_id]');
    console.log('='.repeat(80) + '\n');
  }
}

module.exports = PauseResumeHandler;
