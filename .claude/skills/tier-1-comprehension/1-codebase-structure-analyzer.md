---
name: Codebase Structure Analyzer
tier: 1-Comprehension
category: Understanding
priority: Critical
---

# Codebase Structure Analyzer

## Purpose

Quickly map and understand any codebase structure provided by L1 Orchestrator. Creates a structured overview of directories, key files, architectural patterns, and entry points.

## When to Use (Trigger Conditions)

- Starting work on a new module or phase
- Analyzing unfamiliar codebase sections
- Understanding legacy code before porting
- Planning refactoring or architectural changes
- Identifying where generated code should fit

## Input Parameters

```
root_path: string
  The directory to analyze (e.g., "backend/", "frontend/src/")

depth: integer (default: 3)
  How many directory levels to map (3 = good overview, 5 = detailed)

file_types: list (default: all)
  Focus on specific extensions: ["*.py", "*.tsx", "*.ts"]

exclude_patterns: list
  What to ignore: ["node_modules", "__pycache__", ".git", "*.pyc"]

show_imports: boolean (default: false)
  Include top-level import analysis for each file

show_sizes: boolean (default: true)
  Include file size information
```

## Output Structure

```markdown
## CODEBASE STRUCTURE: [path]

### Directory Tree
- Clear hierarchical view
- File counts per directory
- Key modules identified

### Key Files & Purposes
- Entry points (main, index, __init__)
- Configuration files
- Important utilities

### Architecture Overview
- Identified patterns (MVC, Repository, Factory, etc.)
- Module relationships
- Dependency flow

### Important Observations
- Technology detected (Django, Next.js, etc.)
- Empty/template files
- Files needing attention

### Quick Reference
- File count summary
- Language distribution
- Total codebase size
```

## Example Output

```
## CODEBASE STRUCTURE: backend/

### Directory Tree

📁 backend/
├── 📂 config/ (Django settings & configuration)
│   ├── settings.py (main config, ~800 lines)
│   ├── urls.py (root router)
│   ├── wsgi.py (production entry)
│   └── settings/ (environment-specific)
│       ├── base.py
│       ├── development.py
│       └── production.py
│
├── 📂 api/ (REST API endpoints)
│   ├── models.py (empty, ~5 lines) [TEMPLATE]
│   ├── serializers.py (models → JSON)
│   ├── views.py (endpoint handlers)
│   ├── urls.py (routing)
│   ├── permissions.py (access control)
│   └── filters.py (query filtering)
│
├── 📂 pricing/ (Pricing engine - Phase 2)
│   ├── models.py (empty, waiting for cmtgdirect port)
│   ├── calculator.py (pricing logic)
│   ├── adjustments.py (rate adjustments)
│   └── tests/ (test cases)
│
├── 📂 cms/ (Wagtail CMS - Phase 3)
│   ├── models.py (empty, waiting for WordPress migration)
│   ├── blocks.py (StreamField blocks)
│   └── tests/
│
├── requirements.txt (Python dependencies)
├── Dockerfile (Python 3.12 slim image)
├── entrypoint.sh (migration runner)
└── manage.py (Django CLI)

### Key Files & Purposes

**Configuration:**
- config/settings.py - Django settings (DB, apps, middleware)
- config/urls.py - Root URL routing
- requirements.txt - Python dependencies

**API Layer:**
- api/views.py - REST endpoints (ViewSets, APIViews)
- api/serializers.py - Data validation & transformation
- api/models.py - Data models [WAITING FOR PORT]

**Business Logic:**
- pricing/calculator.py - Loan calculation engine
- pricing/adjustments.py - Rate adjustment grids

**Infrastructure:**
- Dockerfile - Container definition
- entrypoint.sh - Database setup, superuser creation
- manage.py - Django management interface

### Architecture Overview

This is a **Django + Wagtail Headless CMS** architecture:

```
Incoming Request
    ↓
[config/urls.py] - Route to appropriate app
    ↓
[api/views.py] - Handle request, call business logic
    ↓
[pricing/ or cms/] - Business logic or CMS models
    ↓
[PostgreSQL] - Data persistence
    ↓
Response (JSON or CMS content)
```

**Design Patterns Detected:**
- ViewSet pattern (DRF) for CRUD operations
- Manager pattern (Django ORM) for complex queries
- Signal pattern for model lifecycle hooks
- Migration pattern for schema versioning

### Important Observations

**Current State:**
✓ Foundation layers (config, API routing) complete
✓ Database configured (PostgreSQL + Redis)
✓ Docker setup complete
⚠️ pricing/ models empty - waiting for cmtgdirect port
⚠️ cms/ models empty - waiting for WordPress migration

**Ready to Generate:**
✓ LoanProgram model
✓ RateAdjustment model
✓ API serializers & views

**Dependencies:**
- Wagtail 6.0 for CMS (already configured)
- DRF 3.14 for REST (already configured)
- Celery 5.3 for async tasks (configured in settings)

### Quick Reference

**File Count:**
- Total Python files: 34
- Models: 0 (templates only)
- Serializers: 2
- Views: 3
- Tests: 8
- Configuration: 5

**Language Distribution:**
- Python: 95%
- YAML/JSON: 5% (Docker, requirements)

**Codebase Size:**
- Total: ~4.2 MB (mostly dependencies)
- Source code: ~150 KB
- Test code: ~85 KB
```

## Use Cases

### Use Case 1: Starting New Phase
**Scenario:** Phase 2 (Pricing Engine porting) begins
**Process:**
1. Analyze `backend/pricing/` directory
2. Identify empty model templates
3. Understand existing pricing patterns
4. Generate models based on cmtgdirect code

### Use Case 2: Understanding Legacy Code Before Porting
**Scenario:** Need to understand `legacy/cmtgdirect/` structure
**Process:**
1. Map the legacy directory structure
2. Identify key files (models, views, utilities)
3. Note entry points and main logic
4. Create mapping guide for translation

### Use Case 3: Planning Refactor
**Scenario:** Codebase has grown, refactoring needed
**Process:**
1. Analyze full structure
2. Identify tightly-coupled modules
3. Map dependencies
4. Plan split into smaller, focused modules

## How I Use This Skill

**Step 1: Receive Task**
```
Task: "Generate pricing models for Phase 2.
       Reference existing cmtgdirect code."
```

**Step 2: Analyze Structure**
```
/claude map-codebase backend/
  → Shows existing patterns
  → Identifies where models go
  → Reveals what already exists
```

**Step 3: Understand Pattern**
```
Observations:
- LoanProgram (Wagtail Page) is parent pattern
- Uses custom Manager for queries
- Includes business logic methods
- Properly documented with docstrings
```

**Step 4: Generate with Confidence**
```
I now generate RateAdjustment model following:
- Same file structure as LoanProgram
- Same docstring style
- Same validation patterns
- Same manager query methods
```

## Technical Details

### Algorithm
1. Recursively traverse directory (respecting max depth)
2. Count files by type
3. Identify key files (entry points, configs)
4. Detect technology stack
5. Note empty/template files
6. Summarize architecture

### Performance
- Fast: Typical backend analyzed in < 2 seconds
- Scales: Can handle large codebases (1.9GB legacy code)
- Safe: Read-only operation, no side effects

### Limitations
- Binary files not analyzed (images, compiled code)
- Does not execute code (static analysis only)
- Does not infer business logic (shows structure only)

## Integration with Other Skills

**After Codebase Structure Analyzer:**
→ Use **Pattern Recognition Engine** to understand design patterns
→ Use **Dependency Graph Mapper** to understand impact of changes
→ Use **File Type Classifier** to understand proper file organization

**When to Combine:**
1. New Phase: Structure → Patterns → File Classification
2. Refactor: Structure → Dependencies → Code Splitter
3. Porting: Structure → Legacy Mapping → Modernizer

## Quality Checklist

When I generate output from this skill, I verify:
- [ ] Directory tree is clear and properly indented
- [ ] All key files identified and described
- [ ] Technology stack clearly stated
- [ ] Architecture diagram shows data flow
- [ ] Observations note empty/template files
- [ ] Quick reference has accurate file counts
- [ ] Performance information included (if analyzed)

---

**Example Run:**

```bash
/claude map-codebase backend/ --depth 3 --show-imports true
```

Output: Clear structure analysis with observations about what's ready for generation.
