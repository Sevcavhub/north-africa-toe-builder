# North Africa TO&E Builder

Multi-agent orchestration system for building detailed Table of Organization & Equipment (TO&E) data from historical military sources.

## Overview

This project uses specialized AI agents to:
- Extract data from historical documents
- Build organizational hierarchies (Theater → Corps → Division → Regiment → Battalion → Company → Platoon → Squad)
- Distribute equipment across all levels
- Validate data consistency
- Generate multiple output formats (MDBook, wargaming scenarios, SQL database)

## Quick Start

```bash
# Install dependencies
npm install

# Run the orchestrator
npm start

# Run tests
npm test
```

## Project Structure

```
north-africa-toe-builder/
├── src/                    # Core orchestration code
├── agents/                 # Agent definitions and prompts
├── schemas/                # JSON schemas for data validation
├── templates/              # Unit templates (squad, platoon, etc.)
├── data/
│   ├── sources/           # Historical source documents
│   └── output/            # Generated outputs
├── test/                   # Test files
└── docs/                   # Documentation
```

## Documentation

See `docs/PROJECT_CONTEXT.md` for complete project context and architecture.

## Current Status

- ✅ Architecture designed
- ✅ Agent catalog defined
- ⏸️ Implementation in progress

## Example Data

- Italian 10th Army (1940-Q2): 200,000 personnel, 170 tanks
- British Western Desert Force (1940-Q2): 36,000 personnel, 228 tanks
