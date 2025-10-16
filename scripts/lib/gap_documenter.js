/**
 * Gap Documenter - Tiered Extraction Support
 *
 * Handles gap documentation for Tier 2-4 extractions
 * - Tier 1 (75-100%): No gaps, production ready
 * - Tier 2 (60-74%): Minor gaps, generate GAPS_{unit}.md
 * - Tier 3 (50-59%): Partial data, generate NEEDS_RESEARCH_{unit}.md
 * - Tier 4 (<50%): Insufficient, generate RESEARCH_BRIEF_{unit}.md
 */

const fs = require('fs').promises;
const path = require('path');

class GapDocumenter {
  /**
   * Determine extraction tier based on confidence and field completeness
   *
   * @param {number} confidence - Overall confidence score (0-100)
   * @param {Array} requiredFieldsPresent - List of required fields found
   * @param {Array} requiredFieldsMissing - List of required fields missing
   * @param {Object} gapsDocumented - Detailed gap documentation
   * @returns {number} - Tier (1-4)
   */
  determineTier(confidence, requiredFieldsPresent, requiredFieldsMissing, gapsDocumented) {
    const totalRequired = requiredFieldsPresent.length + requiredFieldsMissing.length;
    const completeness = totalRequired > 0 ? (requiredFieldsPresent.length / totalRequired) * 100 : 0;

    // Tier 1: High confidence, all required fields present
    if (confidence >= 75 && requiredFieldsMissing.length === 0) {
      return 1;
    }

    // Tier 2: Good confidence, minor gaps OR well-documented gaps
    if (confidence >= 60 && confidence < 75) {
      // Well-documented gaps can still be Tier 2
      if (requiredFieldsMissing.length <= 2 && gapsDocumented && Object.keys(gapsDocumented).length > 0) {
        return 2;
      }
      // Only optional fields missing
      if (requiredFieldsMissing.length === 0) {
        return 2;
      }
    }

    // Tier 3: Moderate confidence, substantial data exists
    if (confidence >= 50 && confidence < 60 && completeness >= 50) {
      return 3;
    }

    // Tier 4: Low confidence or insufficient data
    return 4;
  }

  /**
   * Get status string for tier
   *
   * @param {number} tier - Tier (1-4)
   * @returns {string} - Status string
   */
  getStatusForTier(tier) {
    const statusMap = {
      1: 'production_ready',
      2: 'review_recommended',
      3: 'partial_needs_research',
      4: 'research_brief_created'
    };
    return statusMap[tier] || 'unknown';
  }

  /**
   * Generate GAPS file for Tier 2 extractions
   *
   * @param {Object} unit - Unit information
   * @param {Object} gapDocumentation - Detailed gap info from validation object
   * @param {Array} requiredFieldGaps - List of required fields with gaps
   * @param {number} confidence - Overall confidence score
   * @returns {string} - Markdown content for GAPS file
   */
  generateGapsReport(unit, gapDocumentation, requiredFieldGaps, confidence) {
    const { nation, quarter, unit_designation } = unit;

    let markdown = `# Data Gaps Report - ${unit_designation}\n\n`;
    markdown += `**Nation**: ${nation}\n`;
    markdown += `**Quarter**: ${quarter}\n`;
    markdown += `**Confidence**: ${confidence}% (Tier 2 - Review Recommended)\n`;
    markdown += `**Status**: Extraction completed with documented gaps\n\n`;
    markdown += `---\n\n`;

    markdown += `## Overview\n\n`;
    markdown += `This unit was extracted with **Tier 2** quality. The extraction is substantially complete, but has ${requiredFieldGaps.length} documented gap(s) in required fields. This is acceptable for review and use, with the understanding that some data points are documented as missing or estimated.\n\n`;

    markdown += `## Critical Field Gaps\n\n`;

    for (const fieldName of requiredFieldGaps) {
      const gap = gapDocumentation[fieldName];
      if (!gap) continue;

      markdown += `### ${fieldName}\n\n`;
      markdown += `- **Status**: ${gap.status}\n`;
      markdown += `- **Reason**: ${gap.reason}\n`;
      markdown += `- **Sources Checked**:\n`;
      for (const source of gap.sources_checked || []) {
        markdown += `  - ${source}\n`;
      }
      markdown += `- **Confidence Impact**: ${gap.confidence_impact}% penalty\n`;

      if (gap.mitigation) {
        markdown += `- **How to Resolve**: ${gap.mitigation}\n`;
      }

      if (gap.estimate_method) {
        markdown += `- **Estimation Method**: ${gap.estimate_method}\n`;
      }

      markdown += `\n`;
    }

    markdown += `## Recommendations\n\n`;
    markdown += `**For User Review**:\n`;
    markdown += `1. Review the documented gaps above\n`;
    markdown += `2. Decide if ${confidence}% confidence is acceptable for your use case\n`;
    markdown += `3. If gaps must be filled:\n`;
    markdown += `   - Follow the "How to Resolve" guidance for each gap\n`;
    markdown += `   - Update the unit JSON with new data\n`;
    markdown += `   - Re-run validation to upgrade to Tier 1\n\n`;

    markdown += `**Current Recommendation**: **${confidence >= 65 ? 'ACCEPTABLE' : 'NEEDS IMPROVEMENT'}** - `;
    markdown += confidence >= 65
      ? 'This Tier 2 extraction has reasonable confidence for use with documented limitations.'
      : 'Confidence is lower end of Tier 2 range. Consider filling gaps if data is critical.';

    markdown += `\n\n---\n\n`;
    markdown += `*Generated by: Gap Documenter v1.0*\n`;
    markdown += `*Schema: unified_toe_schema.json v3.1.0*\n`;

    return markdown;
  }

  /**
   * Generate NEEDS_RESEARCH file for Tier 3 extractions
   *
   * @param {Object} unit - Unit information
   * @param {Object} availableData - Data that WAS successfully extracted
   * @param {Object} gap Documentation - Detailed gap info
   * @param {Array} requiredFieldGaps - List of required fields missing
   * @param {number} confidence - Overall confidence score
   * @returns {string} - Markdown content for NEEDS_RESEARCH file
   */
  generateNeedsResearchReport(unit, availableData, gapDocumentation, requiredFieldGaps, confidence) {
    const { nation, quarter, unit_designation } = unit;

    let markdown = `# Research Needed - ${unit_designation}\n\n`;
    markdown += `**Nation**: ${nation}\n`;
    markdown += `**Quarter**: ${quarter}\n`;
    markdown += `**Confidence**: ${confidence}% (Tier 3 - Partial Extraction)\n`;
    markdown += `**Status**: Substantial data available, but critical gaps exist\n\n`;
    markdown += `---\n\n`;

    markdown += `## Status Summary\n\n`;
    markdown += `This unit was extracted with **Tier 3** quality. Significant data has been found and preserved, but ${requiredFieldGaps.length} required field(s) are missing or have very low confidence. Additional research is needed to upgrade this to Tier 2 or Tier 1.\n\n`;

    markdown += `### What We Have ✅\n\n`;
    const availableFields = Object.keys(availableData || {}).filter(key =>
      availableData[key] !== null && availableData[key] !== undefined
    );
    markdown += `- **${availableFields.length}** fields successfully extracted\n`;
    markdown += `- **${confidence}%** overall confidence in available data\n`;
    markdown += `- Unit existence and basic structure confirmed\n\n`;

    markdown += `### What We Need ❌\n\n`;
    markdown += `**${requiredFieldGaps.length} Required Field Gaps**:\n\n`;

    for (const fieldName of requiredFieldGaps) {
      const gap = gapDocumentation[fieldName];
      markdown += `#### ${fieldName}\n\n`;

      if (gap) {
        markdown += `- **Reason Missing**: ${gap.reason}\n`;
        markdown += `- **Sources Already Checked**:\n`;
        for (const source of gap.sources_checked || []) {
          markdown += `  - ❌ ${source}\n`;
        }
        if (gap.mitigation) {
          markdown += `- **🔍 Recommended Next Sources**: ${gap.mitigation}\n`;
        }
      } else {
        markdown += `- **Status**: Not found in available sources\n`;
        markdown += `- **Research Required**: Identify authoritative source for this field\n`;
      }

      markdown += `\n`;
    }

    markdown += `## Research Action Plan\n\n`;
    markdown += `**Priority Order** (tackle in this sequence):\n\n`;

    requiredFieldGaps.forEach((fieldName, index) => {
      const gap = gapDocumentation[fieldName];
      markdown += `${index + 1}. **${fieldName}**\n`;
      if (gap && gap.mitigation) {
        markdown += `   - Try: ${gap.mitigation}\n`;
      } else {
        markdown += `   - Consult Tier 1 sources for ${nation} ${quarter} units\n`;
      }
    });

    markdown += `\n## How to Upgrade to Tier 2\n\n`;
    markdown += `1. Address at least ${Math.ceil(requiredFieldGaps.length * 0.7)} of the ${requiredFieldGaps.length} gaps above\n`;
    markdown += `2. Document remaining gaps with clear reasoning\n`;
    markdown += `3. Ensure overall confidence reaches 60%+\n`;
    markdown += `4. Update unit JSON with new findings\n`;
    markdown += `5. Re-run extraction to recalculate tier\n\n`;

    markdown += `## How to Upgrade to Tier 1\n\n`;
    markdown += `1. Fill ALL required field gaps\n`;
    markdown += `2. Achieve 75%+ confidence\n`;
    markdown += `3. Cross-verify all data with 2+ sources\n`;
    markdown += `4. Update unit JSON and regenerate MDBook chapter\n\n`;

    markdown += `---\n\n`;
    markdown += `*Generated by: Gap Documenter v1.0*\n`;
    markdown += `*Schema: unified_toe_schema.json v3.1.0*\n`;

    return markdown;
  }

  /**
   * Generate RESEARCH_BRIEF for Tier 4 (insufficient data)
   *
   * @param {Object} unit - Unit information
   * @param {Object} findings - What was discovered during research
   * @param {Array} sourcesChecked - All sources consulted
   * @param {string} recommendation - What to do next
   * @returns {string} - Markdown content for RESEARCH_BRIEF file
   */
  generateResearchBrief(unit, findings, sourcesChecked, recommendation) {
    const { nation, quarter, unit_designation } = unit;

    let markdown = `# Research Brief - ${unit_designation}\n\n`;
    markdown += `**Nation**: ${nation}\n`;
    markdown += `**Quarter**: ${quarter}\n`;
    markdown += `**Status**: Tier 4 - Insufficient Data for Extraction\n\n`;
    markdown += `---\n\n`;

    markdown += `## Executive Summary\n\n`;
    markdown += `Autonomous extraction attempted for "${unit_designation}" but insufficient data was found to create a valid TO&E JSON file. This research brief documents what WAS discovered and recommends next steps.\n\n`;

    markdown += `## Key Findings\n\n`;
    if (findings.unit_exists === false) {
      markdown += `### ⚠️ Unit May Not Exist in This Quarter\n\n`;
      markdown += `**Evidence**:\n`;
      markdown += `${findings.existence_evidence || 'No evidence found that this unit existed in ' + quarter}\n\n`;
      if (findings.alternate_period) {
        markdown += `**Alternate Period**: This unit may have existed in ${findings.alternate_period} instead\n\n`;
      }
    } else {
      markdown += `### Unit Existence: ${findings.unit_exists ? '✅ Confirmed' : '❓ Uncertain'}\n\n`;
      if (findings.evidence) {
        markdown += `**Evidence**:\n${findings.evidence}\n\n`;
      }
    }

    if (findings.data_found && findings.data_found.length > 0) {
      markdown += `### Data Successfully Found\n\n`;
      for (const data of findings.data_found) {
        markdown += `- ✅ ${data}\n`;
      }
      markdown += `\n`;
    }

    if (findings.critical_gaps && findings.critical_gaps.length > 0) {
      markdown += `### Critical Data Gaps\n\n`;
      for (const gap of findings.critical_gaps) {
        markdown += `- ❌ ${gap}\n`;
      }
      markdown += `\n`;
    }

    markdown += `## Sources Consulted\n\n`;
    for (const source of sourcesChecked || []) {
      markdown += `- ${source.status === 'checked' ? '✓' : '✗'} ${source.name}\n`;
      if (source.result) {
        markdown += `  - ${source.result}\n`;
      }
    }
    markdown += `\n`;

    markdown += `## Recommendation\n\n`;
    markdown += `${recommendation}\n\n`;

    markdown += `## Suggested Next Steps\n\n`;
    if (findings.unit_exists === false) {
      markdown += `1. **Verify quarter**: Check if unit existed in different quarter\n`;
      markdown += `2. **Check designation**: Verify exact unit name/designation\n`;
      markdown += `3. **Remove from seed**: If confirmed non-existent, remove from project scope\n`;
    } else {
      markdown += `1. **Consult additional Tier 1 sources** (archives, unit war diaries)\n`;
      markdown += `2. **Contact subject matter experts** for this nation/period\n`;
      markdown += `3. **Check regimental histories** for parent/subordinate unit references\n`;
      markdown += `4. **Review battle accounts** mentioning this unit\n`;
    }

    markdown += `\n---\n\n`;
    markdown += `*Generated by: Gap Documenter v1.0*\n`;
    markdown += `*Schema: unified_toe_schema.json v3.1.0*\n`;

    return markdown;
  }

  /**
   * Save gap documentation to appropriate file
   *
   * @param {number} tier - Extraction tier (2, 3, or 4)
   * @param {string} nation - Nation code
   * @param {string} quarter - Quarter string
   * @param {string} unit_designation - Unit designation (normalized)
   * @param {string} content - Markdown content
   * @param {string} outputDir - Output directory path
   * @returns {Promise<string>} - Path to saved file
   */
  async saveGapDocumentation(tier, nation, quarter, unit_designation, content, outputDir = 'data/output') {
    const normalizedUnit = unit_designation.toLowerCase().replace(/[^a-z0-9]+/g, '_');
    const normalizedQuarter = quarter.toLowerCase().replace(/-/g, '');

    let filename;
    if (tier === 2) {
      filename = `GAPS_${nation}_${normalizedQuarter}_${normalizedUnit}.md`;
    } else if (tier === 3) {
      filename = `NEEDS_RESEARCH_${nation}_${normalizedQuarter}_${normalizedUnit}.md`;
    } else if (tier === 4) {
      filename = `RESEARCH_BRIEF_${nation}_${normalizedQuarter}_${normalizedUnit}.md`;
    } else {
      throw new Error(`Invalid tier ${tier} for gap documentation (only 2, 3, 4 supported)`);
    }

    const gapsDir = path.join(outputDir, 'gaps');
    await fs.mkdir(gapsDir, { recursive: true });

    const filePath = path.join(gapsDir, filename);
    await fs.writeFile(filePath, content, 'utf-8');

    return filePath;
  }

  /**
   * Process extraction result and generate appropriate gap documentation
   *
   * @param {Object} extractionResult - Result from agent extraction
   * @param {string} outputDir - Output directory
   * @returns {Promise<Object>} - Gap documentation result
   */
  async processExtraction(extractionResult, outputDir = 'data/output') {
    const {
      unit,
      confidence,
      requiredFieldsPresent = [],
      requiredFieldsMissing = [],
      gapDocumentation = {},
      availableData = {},
      findings = {},
      sourcesChecked = [],
      recommendation = ''
    } = extractionResult;

    const tier = this.determineTier(
      confidence,
      requiredFieldsPresent,
      requiredFieldsMissing,
      gapDocumentation
    );

    const status = this.getStatusForTier(tier);

    let gapFilePath = null;
    let gapContent = null;

    if (tier === 2) {
      gapContent = this.generateGapsReport(
        unit,
        gapDocumentation,
        requiredFieldsMissing,
        confidence
      );
      gapFilePath = await this.saveGapDocumentation(
        tier,
        unit.nation,
        unit.quarter,
        unit.unit_designation,
        gapContent,
        outputDir
      );
    } else if (tier === 3) {
      gapContent = this.generateNeedsResearchReport(
        unit,
        availableData,
        gapDocumentation,
        requiredFieldsMissing,
        confidence
      );
      gapFilePath = await this.saveGapDocumentation(
        tier,
        unit.nation,
        unit.quarter,
        unit.unit_designation,
        gapContent,
        outputDir
      );
    } else if (tier === 4) {
      gapContent = this.generateResearchBrief(
        unit,
        findings,
        sourcesChecked,
        recommendation
      );
      gapFilePath = await this.saveGapDocumentation(
        tier,
        unit.nation,
        unit.quarter,
        unit.unit_designation,
        gapContent,
        outputDir
      );
    }

    return {
      tier,
      status,
      gapFilePath,
      gapContent,
      message: this.getTierMessage(tier, confidence)
    };
  }

  /**
   * Get user-friendly message for tier
   *
   * @param {number} tier - Tier (1-4)
   * @param {number} confidence - Confidence score
   * @returns {string} - Message
   */
  getTierMessage(tier, confidence) {
    const messages = {
      1: `Tier 1: Production ready with ${confidence}% confidence. No gaps, ready for use.`,
      2: `Tier 2: Review recommended with ${confidence}% confidence. Minor documented gaps, acceptable for most uses.`,
      3: `Tier 3: Partial extraction with ${confidence}% confidence. Substantial data preserved, additional research needed.`,
      4: `Tier 4: Insufficient data (${confidence}% confidence). Research brief created, extraction not attempted.`
    };
    return messages[tier] || 'Unknown tier';
  }
}

module.exports = GapDocumenter;
