# Automated Processing Modes - Quick Reference

**Last Updated**: 2025-10-23 (Commit 2587644)

---

## Mode Comparison

| Feature | Quick/Standard/Extended/Marathon | Continuous |
|---------|----------------------------------|------------|
| **Batch Count** | Fixed (1/3/5/10 batches) | ∞ (until queue empty) |
| **Token Monitoring** | ✅ YES (stops at 80%) | ❌ NO |
| **Compaction Safety** | ✅ YES | ❌ NO |
| **User Presence** | Monitored | Unattended (overnight) |
| **Use Case** | Daily work sessions | Overnight batch processing |
| **Recovery** | Manual resume if stopped | `npm run recover` in morning |

---

## Monitored Modes (Compaction Safety Enabled)

### npm run auto:quick
- **Batches**: 1 (3 units)
- **Time**: ~20-30 minutes
- **Token Safety**: Stops at 80% (160k/200k tokens)
- **Use**: Quick test runs, short sessions

### npm run auto:standard
- **Batches**: 3 (9 units)
- **Time**: ~60-90 minutes
- **Token Safety**: Stops at 80% (160k/200k tokens)
- **Use**: Recommended for daily sessions

### npm run auto:extended
- **Batches**: 5 (15 units)
- **Time**: ~100-150 minutes
- **Token Safety**: Stops at 80% (160k/200k tokens)
- **Use**: Long afternoon/evening sessions

### npm run auto:marathon
- **Batches**: 10 (30 units)
- **Time**: ~200-300 minutes
- **Token Safety**: Stops at 80% (160k/200k tokens)
- **Use**: Weekend sprints with monitoring

**Compaction Safety Behavior:**
```
Batch 1: Complete → session:end → Tokens: 95k (48%) → Continue ✅
Batch 2: Complete → session:end → Tokens: 110k (55%) → Continue ✅
Batch 3: Complete → session:end → Tokens: 125k (63%) → Continue ✅
Batch 4: Complete → session:end → Tokens: 140k (70%) → Continue ✅
Batch 5: Complete → session:end → Tokens: 165k (82%) → STOP! ⚠️

Claude tells you:
  ⚠️ Context usage: 165k/200k tokens (82%)
  ⚠️ Approaching compaction limit - stopping for safety

  All work has been saved via session:end.
  To continue: Open new thread and run same command.
```

---

## Unattended Mode (No Compaction Safety)

### npm run auto:continuous
- **Batches**: ∞ (until queue empty)
- **Time**: Hours (potentially overnight)
- **Token Safety**: ❌ NONE - runs until crash/compaction
- **Use**: Overnight batch processing without monitoring

**Behavior:**
```
Batch 1: Complete → session:end → Continue
Batch 2: Complete → session:end → Continue
Batch 3: Complete → session:end → Continue
...
Batch N: Complete → session:end → Continue
Batch N+1: Compaction occurs OR crash
```

**No stopping at 80% tokens** - designed to run unattended.

**Expected outcomes:**
- ✅ Best case: Processes entire queue overnight
- 🔄 Common case: Compaction occurs, some batches complete
- ⚠️ Worst case: Crash early, few batches complete

**Why this is safe:**
- session:end after EACH batch saves all work
- Max loss: 1-2 units from current batch when crash occurs
- `npm run recover` shows exactly what completed
- Can resume where it left off

---

## Overnight Workflow

### Before Bed:
```bash
# Check how many units remaining
cat WORK_QUEUE.md | grep "remaining"

# Start continuous mode
npm run auto:continuous

# Claude begins processing batches until queue empty or crash
```

### Morning Recovery:
```bash
# Step 1: Assess damage
npm run recover

# Shows:
# ✅ Complete units: 45/419 (10.7%)
# ⚠️ Partial units: 2 (current batch when crash occurred)
# ❌ Invalid units: 0

# Step 2: Clean up partial units
npm run recover -- --auto-cleanup

# Step 3: Resume if needed
npm run auto:continuous  # Continue where it left off
```

---

## Decision Matrix

**Choose auto:quick when:**
- Testing new features
- Limited time available (20-30 min)
- Want to verify workflow works

**Choose auto:standard when:**
- Daily work session (1-1.5 hours)
- Regular extraction work
- Monitoring progress

**Choose auto:extended when:**
- Long work session (2-2.5 hours)
- Making significant progress
- Available to monitor

**Choose auto:marathon when:**
- Weekend sprint (3-5 hours)
- Dedicated extraction day
- Can monitor for token usage

**Choose auto:continuous when:**
- Going to bed / leaving computer
- Want maximum progress without monitoring
- Comfortable with potential crashes
- Will run `npm run recover` in morning

---

## Recovery Command

After any crash or compaction:

```bash
# Analyze what completed
npm run recover

# If partial units found, clean them up
npm run recover -- --auto-cleanup

# Resume work
npm run session:start  # Manual mode
# or
npm run auto:standard  # Continue automated
```

---

## Safety Features

### All Modes:
- ✅ session:end after each batch (updates MCP memory)
- ✅ Documentation synced (START_HERE, PROJECT_SCOPE)
- ✅ Git commit after each batch
- ✅ Work queue regenerated
- ✅ Max 1-2 units lost per crash (current batch only)

### Monitored Modes Only:
- ✅ Token usage monitoring
- ✅ Automatic stop at 80% tokens
- ✅ Clear instructions to resume in new thread

### Continuous Mode:
- ❌ No token monitoring (by design)
- ❌ No automatic stop (runs until queue empty or crash)
- ✅ Designed for unattended overnight runs
- ✅ Recover command assesses damage in morning

---

## Example Session Logs

### Monitored Mode (auto:standard):
```
🎯 Automated Queue Processing

📋 Mode: preset
📊 Batches to process: 3
📦 Units per batch: 3
📈 Total units: 9

============================================================
⚠️  AUTOMATED MODE - NO USER CONFIRMATIONS REQUIRED
============================================================

🤖 INSTRUCTIONS FOR CLAUDE:
You are in AUTOMATED MODE. You MUST process ALL 3 batches.

After each batch completes:
1. Run session:end
2. **CHECK TOKEN USAGE**
   - If > 160,000 tokens (80%): STOP and warn user
3. If tokens OK: Move to next batch IMMEDIATELY

⚠️  COMPACTION SAFETY: Will pause at 80% token usage if needed
```

### Continuous Mode (auto:continuous):
```
🎯 Automated Queue Processing

📋 Mode: continuous
📊 Batches to process: Continuous (until queue empty)
📦 Units per batch: 3
📈 Total units: Until queue empty

============================================================
⚠️  AUTOMATED MODE - NO USER CONFIRMATIONS REQUIRED
============================================================

🤖 INSTRUCTIONS FOR CLAUDE:
You are in CONTINUOUS MODE. Process batches until queue is empty.

After each batch completes:
1. Run session:end
2. **NO TOKEN MONITORING** - Runs until queue empty
   - Compaction/crashes expected on long runs (overnight)
   - session:end saves work after each batch
   - User will run "npm run recover" in morning

⚠️  CONTINUOUS MODE: Designed for overnight unattended runs
⚠️  NO COMPACTION SAFETY: Will run until queue empty or crash
⚠️  If crash/compaction occurs: Use "npm run recover"
⚠️  session:end after each batch = max 1-2 units lost per crash
```

---

## Tips

1. **For daily work**: Start with `auto:standard` (9 units, ~1 hour)
2. **For overnight**: Use `auto:continuous` before bed
3. **After crashes**: Always run `npm run recover` first
4. **If unsure**: Use smaller batch size (quick/standard) with monitoring
5. **Token usage**: Check system warnings in Claude output (shows current/200k)

---

**Status**: ✅ All modes implemented and tested
**Commits**:
- 2587644 - Continuous mode (no compaction safety)
- 0ecc89b - Direct execution detection
- 0501b04 - Crash recovery (single command)
- 9e2721b - Compaction safety (monitored modes)
- 3da13c2 - Mode-specific messaging
- 16cb311 - Non-interactive automation
