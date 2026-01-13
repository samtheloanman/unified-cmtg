# Claude Code Configuration

This directory contains the complete skill architecture, command definitions, and plugin ecosystem for Claude Code operating as **L2 Agent - The Generator** within the unified-cmtg project.

## Directory Structure

```
.claude/
├── CLAUDE.md                    # Main configuration & operational doctrine
├── README.md                    # This file
├── settings.local.json          # Claude Code settings
│
├── skills/                      # 5 Tiers of Skills (27 total)
│   ├── tier-1-comprehension/    # Understand codebases & patterns (5 skills)
│   ├── tier-2-generation/       # Generate production code (8+ skills)
│   ├── tier-3-refactoring/      # Improve & adapt code (5 skills)
│   ├── tier-4-verification/     # Ensure quality & document (5 skills)
│   └── tier-5-workflow/         # Maintain doctrine compliance (4 skills)
│
├── commands/                    # Reusable command definitions
│   ├── analysis/                # Codebase analysis commands
│   ├── generation/              # Code generation commands
│   ├── refactoring/             # Code improvement commands
│   ├── verification/            # Quality checking commands
│   ├── workflow/                # Task & handoff management
│   └── design-os/               # Design system commands (existing)
│
└── plugins/                     # Extensible plugin ecosystem
    ├── parsers/                 # File format & code parsers
    ├── reference/               # Pattern library & conventions
    ├── integrations/            # Helper tools
    └── formatters/              # Output formatting
```

## Quick Start for L1 Orchestrator

### Delegating a Task to Claude

1. **Create the task** in a Conductor track's `checklist.md`:
   ```markdown
   - [ ] **Code Generation:** Generate LoanProgram Django model from schema
         (Owner: Claude) (Priority: High) (Phase: 2)
   ```

2. **Provide full context:**
   ```
   - Legacy model to port: [code provided]
   - Target schema: schema.json
   - Reference pattern: LoanLender model
   - Expected methods: get_rate_for_fico(), is_active()
   ```

3. **Claude executes:** Receives task, parses requirements, generates code, validates quality, prepares handoff

4. **Verification:**
   - Claude provides: Handoff report with specific verification steps
   - You verify: Use proposed steps to check quality
   - Mark complete: Update checklist.md when verified

5. **Next step:** Delegate to Ralph for testing with clear test specifications

### Working with Claude Commands

Commands are invoked via `/claude <command> [args]`:

```bash
/claude parse-task "Generate a RateAdjustment model..."
/claude map-codebase backend/pricing/
/claude detect-patterns backend/api/models.py
/claude check-quality generated_code.py
/claude create-handoff-report task_name completed_files
```

## Skill Tier Overview

### Tier 1: Comprehension (Understanding)
- Codebase Structure Analyzer
- Pattern Recognition Engine
- Legacy Code Mapping Translator
- Dependency Graph Mapper
- File Type & Role Classifier

**Use when:** Starting work, understanding new modules, or planning refactors

### Tier 2: Generation (Creating)
- Django Model Generator
- DRF Serializer Generator
- Django REST API Endpoint Generator
- React/Next.js Component Generator
- TypeScript Type Definition Generator
- API Client Generator
- Celery Task Generator
- Test Suite Generator

**Use when:** Generating new code, porting legacy code, or creating components

### Tier 3: Refactoring (Improving)
- Large File Splitter
- Function Extractor
- Code Modernizer
- Django to Next.js Translator
- Architecture Normalizer

**Use when:** Improving existing code or adapting code across contexts

### Tier 4: Verification (Quality)
- Code Quality Analyzer
- Test Case Validator
- Documentation Generator
- Handoff Report Generator
- Change Summary Documenter

**Use before:** Handing off to Ralph or L1 review

### Tier 5: Workflow (Compliance)
- Task Specification Parser
- Context Receiver & Organizer
- Verification Checkpoint Creator
- Handoff Preparation

**Use always:** To maintain Command & Control doctrine alignment

## Plugin System

### Parser Plugins
- `legacy-code-parser` - Understand Django 2.x, PHP, older patterns
- `json-schema-to-types` - Convert JSON Schema to Python/TypeScript types
- `openapi-parser` - Parse OpenAPI specifications
- `wordpress-acf-parser` - Understand WordPress ACF exports

### Reference Plugins
- `pattern-library` - Architectural patterns used in project
- `style-guide-enforcer` - Naming, formatting, structure rules
- `example-extractor` - Pull working examples from codebase
- `convention-validator` - Check against project rules

### Integration Plugins
- `api-spec-viewer` - Display API specs
- `type-validator` - Validate TypeScript/Python types
- `import-organizer` - Organize imports consistently
- `model-relationship-mapper` - Visualize Django relationships
- `migration-analyzer` - Check migration safety

### Formatter Plugins
- `code-formatter` - Ensure consistent formatting
- `docstring-formatter` - Format documentation
- `changelog-generator` - Create clear changelogs
- `test-report-formatter` - Format test results
- `specification-documenter` - Create clear specs

## Configuration

See `CLAUDE.md` for:
- Operational doctrine and principles
- Complete skill descriptions
- Command definitions
- Plugin architecture
- Escalation procedures
- Success metrics

## Project Context

**Unified CMTG Platform** - Mortgage/real estate website restructuring with:
- ~310 city-specific landing pages using local SEO strategy
- Ported cmtgdirect pricing engine (Django)
- Migrated custommortgage content (Wagtail CMS)
- Rate sheet PDF extraction pipeline
- Floify lead capture integration

**Technology:**
- Frontend: Next.js 14, React 19, TypeScript 5, Tailwind CSS 4
- Backend: Django 5.0, Wagtail 6.0, DRF 3.14, Celery 5.3
- Data: PostgreSQL 15, Redis 7
- External: Floify, Gemini 1.5 Pro, OpenAI, Zillow APIs

## Workflow Hierarchy

```
L1 ORCHESTRATOR (Gemini + Conductor)
  ├─ Owns master plan & checklist.md
  ├─ Delegates tasks to L2 agents
  └─ Verifies completion
      │
      ├─> L2 CLAUDE (Generator)
      │     └─ High-context code generation
      │
      ├─> L2 JULES (Builder)
      │     └─ Infrastructure & setup
      │
      └─> L2 RALPH (Closer)
            └─ Testing & verification

L3 REVIEWER (Human)
  └─ Final sign-off on major milestones
```

## Getting Help

For detailed skill descriptions, see individual files in `skills/` tiers.
For command usage, see `commands/` directory.
For plugin details, see `plugins/` directory.
For operational guidelines, see `CLAUDE.md`.

---

**Last Updated:** 2026-01-12
**Version:** 1.0
**Status:** Active for unified-cmtg project
