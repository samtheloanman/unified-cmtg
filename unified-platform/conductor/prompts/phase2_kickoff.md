# Phase 2 Kickoff: Pricing Engine Porting Prompts

> **Context**: We are moving from Phase 1 (Foundation) to Phase 2 (Core Pricing Engine). We need to port legacy Django models and logic from `cmtgdirect` to `unified-platform`.

## 🤖 1. Prompt for Jules (The Builder)
**Role**: L2 Builder Agent  
**Objective**: Port Core Models & Initial Setup (Task 2.1)

```markdown
@Jules You are the Builder Agent. Your goal is to establish the database foundation for the Pricing Engine by porting legacy models.

**Context**: 
- Source: `cmtgdirect` (Legacy Django)
- Destination: `unified-platform/backend/pricing` (New Django app)

**Your Checklist**:
1.  **Copy Model Files**:
    - Copy `loans/models/programs.py` from legacy to `backend/pricing/models/programs.py`.
    - Copy `loans/models/program_types.py` from legacy to `backend/pricing/models/program_types.py`.
    - Copy `loans/choices.py` from legacy to `backend/pricing/choices.py`.

2.  **Refactor Code**:
    - Open each new file.
    - Change imports from `loans.choices` to `pricing.choices`.
    - Ensure `TimestampedModel` import points to `common.models`.
    - If `ChoiceArrayField` is used, ensure it imports from `common.fields`.

3.  **Setup App**:
    - Create `backend/pricing/models/__init__.py` exposing: `Lender`, `LoanProgram`, `BaseLoan`, `ProgramType`, `LenderProgramOffering`.
    - Ensure `pricing` is in `INSTALLED_APPS` (it should be already).

4.  **Database Sync**:
    - Run `python manage.py makemigrations pricing`.
    - Run `python manage.py migrate`.
    - **Verify**: Run `python manage.py showmigrations pricing` and confirm `0001_initial` is applied.

5.  **Fixture Extraction (Bonus)**:
    - If accessible, run `dumpdata` on legacy container and `loaddata` on new container for `Lender` model to prove compatibility.

**Definition of Done**:
- Migration file `0001_initial.py` exists.
- `python manage.py check` passes with zero errors.
```

---

## 🧠 2. Prompt for Claude (The Generator)
**Role**: L2 Generator Agent  
**Objective**: Port Matching Logic & Service Layer (Task 2.2)

```markdown
@Claude You are the Senior Developer (Generator). Your goal is to port the complex loan matching logic from the legacy system into a clean, testable Service Layer.

**Context**:
- Legacy Logic: `cmtgdirect/loans/queries.py` (specifically `get_matched_loan_programs_for_qual`)
- New Destination: `backend/pricing/services/matching.py`

**Your Checklist**:
1.  **Analyze Legacy Logic**:
    - Read `cmtgdirect/loans/queries.py`.
    - Understand the filtering dictionary (property_types, entity_types, loan limits, FICO/LTV cutoffs).

2.  **Implement Service Class**:
    - Create `backend/pricing/services/matching.py`.
    - Define class `LoanMatchingService`.
    - Implement `__init__(self, scenario)` where scenario is a data class or dict of borrower info.
    - Implement `get_matches()` returning a QuerySet of `LenderProgramOffering`.
    - **CRITICAL**: The filtering logic must be IDENTICAL to legacy. Do not "improve" the business logic yet, only the code structure.

3.  **Create Unit Test**:
    - Create `backend/pricing/tests/test_matching.py`.
    - Write a test case that creates a `LenderProgramOffering` with specific constraints (e.g., Min FICO 700).
    - Assert that a borrower with FICO 680 is excluded.
    - Assert that a borrower with FICO 720 is included.

**Definition of Done**:
- `LoanMatchingService` class is fully implemented with type hints.
- `pytest backend/pricing/tests/test_matching.py` passes.
```

---

## 🎻 3. Prompt for Gemini CLI (The Orchestrator)
**Role**: L1 Orchestrator  
**Objective**: Project State Management & Validation

```markdown
@Gemini_CLI You are the Conductor. Your job is to enforce the workflow state and ensure Phase 1 is solidly complete before Phase 2 code merges.

**Your Checklist**:
1.  **Phase 1 Final Check**:
    - Verify Frontend/Backend connectivity: `curl -v http://localhost:3001/test` (Expect 200 OK or "API ok").
    - If failing, STOP Phase 2 work and order a fix for the frontend client.

2.  **Environment Prep**:
    - Ensure `pricing` app exists in Django: `ls backend/pricing`.
    - Check git status: Ensure checking out a new branch `feat/pricing-engine-v1` from `main`.

3.  **Task Delegation**:
    - Create artifacts/tickets for Jules (Task 2.1) and Claude (Task 2.2).
    - Update `conductor/current.md` moving Phase 2 items to "In Progress".

4.  **Verification Loop**:
    - Watch for the new migration file `0001_initial.py`.
    - Once created, run the test suite: `pytest`.

**Command**: Initialize Phase 2 now.
```

---

## 🐜 4. Tasks for Antigravity (Me)
**Role**: L3 Reviewer & Support

- [ ] **Monitor Frontend Connectivity**: Analyze the `curl` output from Step 258 to confirm if Phase 1 is truly done.
- [ ] **Scaffold Files**: If Jules/Claude are not available immediately, I will create the empty file structures for `pricing/models/*.py` and `pricing/services/matching.py` to unblock them.
- [ ] **Run Validation**: I will execute the `makemigrations` dry-run to ensure the ported code doesn't crash Django before we commit.
- [ ] **Update Documentation**: I will update `conductor/tasks.md` to reflect the exact state of these sub-tasks.
