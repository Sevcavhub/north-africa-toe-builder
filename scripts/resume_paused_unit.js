#!/usr/bin/env node

/**
 * Resume Paused Unit - CLI Interface
 *
 * Allows user to:
 * 1. List all paused units
 * 2. Select a paused unit to resume
 * 3. Provide direct instruction to agent
 * 4. Resume extraction with user guidance
 *
 * Usage:
 *   npm run resume:list            # List all paused units
 *   npm run resume -- [unit_id]    # Resume specific unit (interactive)
 *
 * Part of Agent Catalog v3.2.0 - Exhaustive Search + Human-in-Loop
 */

const PauseResumeHandler = require('../src/pause_resume_handler');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

/**
 * Prompt user for input
 * @param {String} question - Question to ask
 * @returns {Promise<String>} User's answer
 */
function prompt(question) {
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      resolve(answer);
    });
  });
}

/**
 * Main function
 */
async function main() {
  const handler = new PauseResumeHandler();
  const command = process.argv[2];

  console.log('\n' + '='.repeat(80));
  console.log('⏸️  RESUME PAUSED UNIT - Human-in-the-Loop Interface');
  console.log('='.repeat(80) + '\n');

  if (command === 'list' || !command) {
    // List all paused units
    await handler.listPausedUnits();

    const pausedUnits = await handler.getPausedUnits();
    if (pausedUnits.length === 0) {
      rl.close();
      return;
    }

    // Ask if user wants to resume one
    const answer = await prompt('Would you like to resume a unit? (y/n): ');
    if (answer.toLowerCase() !== 'y') {
      console.log('\n👋 Exiting\n');
      rl.close();
      return;
    }

    const unitNumber = await prompt(`Enter unit number (1-${pausedUnits.length}): `);
    const index = parseInt(unitNumber) - 1;

    if (isNaN(index) || index < 0 || index >= pausedUnits.length) {
      console.error('\n❌ Invalid unit number\n');
      rl.close();
      return;
    }

    const selectedUnit = pausedUnits[index];

    // Show detailed pause information
    console.log('\n' + '-'.repeat(80));
    console.log('📋 SELECTED UNIT:');
    console.log('-'.repeat(80));
    console.log(`Unit: ${selectedUnit.unit.nation} ${selectedUnit.unit.unit_designation} (${selectedUnit.unit.quarter})`);
    console.log(`Paused: ${selectedUnit.paused_at}`);
    console.log(`Reason: ${selectedUnit.reason}\n`);

    // Show exhaustive search summary
    console.log('🔍 EXHAUSTIVE SEARCH COMPLETED:');
    console.log(`   • Tier 1 sources checked: ${selectedUnit.sources_checked.tier1.length}`);
    console.log(`   • Tier 2 sources checked: ${selectedUnit.sources_checked.tier2.length}`);
    console.log(`   • Tier 3 sources checked: ${selectedUnit.sources_checked.tier3.length}\n`);

    // Show critical gaps
    if (selectedUnit.gaps && selectedUnit.gaps.length > 0) {
      console.log('⚠️  CRITICAL GAPS:');
      for (const gap of selectedUnit.gaps) {
        console.log(`\n   Field: ${gap.field}`);
        console.log(`   Status: ${gap.status}`);
        console.log(`   Sources tried: ${gap.sources_tried}`);

        if (gap.potential_next_steps && gap.potential_next_steps.length > 0) {
          console.log(`   \n   💡 Potential next steps:`);
          gap.potential_next_steps.forEach((step, i) => {
            console.log(`      ${i + 1}. ${step}`);
          });
        }
      }
      console.log();
    }

    // Show question
    console.log('-'.repeat(80));
    console.log('❓ QUESTION:');
    console.log('-'.repeat(80));
    console.log(selectedUnit.question);
    console.log();

    // Show context
    console.log('-'.repeat(80));
    console.log('💬 CONTEXT:');
    console.log('-'.repeat(80));
    console.log(selectedUnit.context);
    console.log();

    // Get user guidance
    console.log('-'.repeat(80));
    console.log('📝 PROVIDE YOUR GUIDANCE:');
    console.log('-'.repeat(80));
    console.log('Examples:');
    console.log('  • "Check British Intelligence WO 208 for commander information"');
    console.log('  • "Accept extraction with commander = null and document the gap"');
    console.log('  • "Mark for future research when Italian archive access available"');
    console.log('  • "Use Generale di Corpo d\'Armata Lorenzo Dalmazzo as commander"\n');

    const userGuidance = await prompt('Your instruction: ');

    if (!userGuidance || userGuidance.trim().length === 0) {
      console.error('\n❌ No instruction provided. Exiting.\n');
      rl.close();
      return;
    }

    // Resume unit with guidance
    const unitId = `${selectedUnit.unit.nation}_${selectedUnit.unit.quarter}_${selectedUnit.unit.unit_designation}`;

    try {
      await handler.resume(unitId, userGuidance);

      console.log('\n' + '='.repeat(80));
      console.log('✅ UNIT RESUMED');
      console.log('='.repeat(80));
      console.log(`\n📝 Your guidance: ${userGuidance}`);
      console.log('\n⚠️  NOTE: Agent will now process your instruction.');
      console.log('   Run the orchestrator again to continue extraction with your guidance.');
      console.log('\n='.repeat(80) + '\n');
    } catch (error) {
      console.error(`\n❌ Failed to resume unit: ${error.message}\n`);
    }

    rl.close();
  } else {
    // Resume specific unit by ID
    const unitId = command;

    try {
      const pausedUnits = await handler.getPausedUnits();
      const selectedUnit = pausedUnits.find(u => {
        const id = `${u.unit.nation}_${u.unit.quarter}_${u.unit.unit_designation}`;
        return id === unitId;
      });

      if (!selectedUnit) {
        console.error(`\n❌ Paused unit not found: ${unitId}\n`);
        console.log('💡 Run "npm run resume:list" to see all paused units\n');
        rl.close();
        return;
      }

      // Show detailed pause information (same as above)
      console.log('\n' + '-'.repeat(80));
      console.log('📋 UNIT:');
      console.log('-'.repeat(80));
      console.log(`Unit: ${selectedUnit.unit.nation} ${selectedUnit.unit.unit_designation} (${selectedUnit.unit.quarter})`);
      console.log(`Paused: ${selectedUnit.paused_at}\n`);

      console.log('-'.repeat(80));
      console.log('❓ QUESTION:');
      console.log('-'.repeat(80));
      console.log(selectedUnit.question);
      console.log();

      // Get user guidance
      const userGuidance = await prompt('Your instruction: ');

      if (!userGuidance || userGuidance.trim().length === 0) {
        console.error('\n❌ No instruction provided. Exiting.\n');
        rl.close();
        return;
      }

      await handler.resume(unitId, userGuidance);

      console.log('\n✅ Unit resumed with your guidance\n');
    } catch (error) {
      console.error(`\n❌ Error: ${error.message}\n`);
    }

    rl.close();
  }
}

main().catch(error => {
  console.error(`\n❌ Fatal error: ${error.message}\n`);
  rl.close();
  process.exit(1);
});
