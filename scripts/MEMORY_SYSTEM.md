# Memory System Documentation

## Overview

The memory system provides cross-session knowledge retention for the North Africa TO&E project. It stores patterns, decisions, and quality issues discovered during work sessions, enabling continuity across multiple autonomous runs.

## Architecture

### Storage Strategy
- **Primary**: Memory MCP (when available) for persistent knowledge graph
- **Fallback**: Local JSON files in `.memory_cache/` directory

### Data Types Stored

1. **Patterns** - Quality trends and systematic observations
   - Example: "80% of units have estimated battalion TO&E"
   - Example: "100% missing WITW IDs (one-time batch fix needed)"

2. **Decisions** - Workflow choices and threshold settings
   - Example: "Use 2-3 agents max for stability (4-6 caused crashes)"
   - Example: "75%+ confidence threshold for division-level units"

3. **Quality Issues** - Validation failures and data conflicts
   - Example: "Schema validation failed for germany_1941q2_15_panzer_division"
   - Example: "Personnel total mismatch: expected 16000, got 15750"

4. **Session Statistics** - Completion metrics and performance data
   - Units completed per session
   - Session duration
   - Patterns/issues/decisions discovered

## Usage

### Integration with Session Scripts

The memory system is automatically integrated with session management:

**Session Start** (`npm run session:start`):
- Queries project knowledge (patterns, decisions, quality issues)
- Displays most recent 10 items of each type
- Uses defaults if no cached knowledge available

**Session End** (`npm run session:end`):
- Stores session statistics
- Stores patterns discovered during session
- Stores quality issues found
- Stores decisions made

### Manual Operations

**View Memory Statistics**:
```bash
npm run memory:stats
```

Shows:
- Total patterns, decisions, issues
- Breakdown by category
- Recent items of each type
- Severity distribution for quality issues

**Export Memory Cache**:
```bash
npm run memory:export [filepath]
```

Creates backup of all memory data to JSON file. Default: `memory_export.json`

**Import Memory Cache**:
```bash
node scripts/memory_mcp_helpers.js import <filepath>
```

Restores memory from backup file.

**Clear Memory Cache**:
```bash
npm run memory:clear
```

Deletes `.memory_cache/` directory. Use for testing or reset.

### Programmatic Usage

```javascript
const {
    storePattern,
    storeDecision,
    storeQualityIssue,
    storeSessionStats,
    queryProjectKnowledge
} = require('./memory_mcp_helpers');

// Store a pattern
await storePattern(
    '93% have estimated supply status',
    { session_id: 'session_123', confidence: 0.93 }
);

// Store a decision
await storeDecision(
    '3-3-3 rule: 3 units/batch, 3 batches/session',
    'Proven stable in production',
    { session_id: 'session_123' }
);

// Store a quality issue
await storeQualityIssue(
    'Personnel total mismatch',
    'warning',
    { unit_id: 'germany_1941q2_15_panzer', expected: 16000, actual: 15750 }
);

// Query all knowledge
const knowledge = await queryProjectKnowledge();
console.log('Patterns:', knowledge.patterns);
console.log('Decisions:', knowledge.decisions);
console.log('Issues:', knowledge.issues);
```

## Storage Locations

### Memory MCP (when available)
- Stored in Memory MCP knowledge graph
- Queryable across sessions
- Persists indefinitely

### Local Fallback
```
.memory_cache/
├── patterns.json           # Pattern observations
├── decisions.json          # Workflow decisions
├── quality_issues.json     # Validation failures
└── session_stats.json      # Session metrics
```

**Note**: `.memory_cache/` is gitignored to avoid cluttering repository.

## Data Schema

### Pattern Entry
```json
{
  "pattern": "80% of units have estimated battalion TO&E",
  "timestamp": "2025-10-11T12:34:56.789Z",
  "session_id": "session_abc123",
  "units_affected": 170,
  "confidence": 0.8
}
```

### Decision Entry
```json
{
  "decision": "Use 2-3 agents max for stability",
  "rationale": "4-6 agents caused crashes",
  "timestamp": "2025-10-11T12:34:56.789Z",
  "session_id": "session_abc123",
  "agents": 3
}
```

### Quality Issue Entry
```json
{
  "issue": "Personnel total mismatch",
  "severity": "warning",
  "timestamp": "2025-10-11T12:34:56.789Z",
  "session_id": "session_abc123",
  "unit_id": "germany_1941q2_15_panzer",
  "field": "total_personnel",
  "expected": 16000,
  "actual": 15750
}
```

### Session Stats Entry
```json
{
  "completed_count": 3,
  "duration": 180,
  "session_id": "session_abc123",
  "timestamp": "2025-10-11T15:34:56.789Z",
  "patterns": ["pattern1", "pattern2"],
  "issues": [{...}],
  "decisions": [{...}]
}
```

## Integration with Autonomous Orchestrator

The autonomous orchestrator automatically:

1. **On Start**: Queries memory to inform decision-making
   - Uses known patterns to set expectations
   - Applies established decisions to workflow
   - Avoids repeating known issues

2. **During Execution**: Collects data for storage
   - Tracks patterns as they emerge
   - Documents decisions made
   - Records quality issues encountered

3. **On Checkpoint**: Stores accumulated knowledge
   - After every 3-unit batch
   - Session end
   - Manual checkpoint creation

## Benefits

1. **Cross-Session Continuity**: Knowledge persists across autonomous runs
2. **Informed Decision-Making**: New sessions start with full context
3. **Pattern Recognition**: Systematic issues become visible over time
4. **Quality Improvement**: Repeated issues can be addressed systematically
5. **Workflow Optimization**: Successful approaches are documented and reused

## Fallback Behavior

When Memory MCP is unavailable:
- All functions gracefully degrade to local file storage
- No functionality is lost
- Performance is identical
- Data persists across restarts

When Memory MCP becomes available:
- TODO: Implement migration of local cache to MCP
- TODO: Implement bidirectional sync

## Future Enhancements

### Phase 1 (Implemented)
- ✅ Local file-based storage
- ✅ Core storage/query functions
- ✅ Session script integration
- ✅ CLI interface
- ✅ Export/import functionality

### Phase 2 (Planned)
- ⏳ Memory MCP integration
- ⏳ Automatic cache migration
- ⏳ Bidirectional sync
- ⏳ Advanced query capabilities
- ⏳ Pattern analysis and trend detection

### Phase 3 (Future)
- 📋 Cross-project knowledge sharing
- 📋 AI-assisted pattern recognition
- 📋 Automated quality improvement suggestions
- 📋 Decision recommendation engine

## Troubleshooting

### Memory not persisting between sessions
- Check that `.memory_cache/` directory exists and is writable
- Verify session scripts are using `npm run session:start` and `npm run session:end`
- Run `npm run memory:stats` to verify data is being stored

### Memory MCP not available
- This is expected behavior - system automatically uses local fallback
- No action needed unless you specifically want MCP integration
- To check availability: `node scripts/memory_mcp_helpers.js test-query`

### Want to reset memory
- Use `npm run memory:clear` to delete all cached data
- Backup first with `npm run memory:export` if desired

### Want to share memory between machines
- Export on machine A: `npm run memory:export shared_memory.json`
- Import on machine B: `node scripts/memory_mcp_helpers.js import shared_memory.json`

---

**Last Updated**: 2025-10-11
**Version**: 1.0
**Author**: Checkpoint System Implementation
