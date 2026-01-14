# Master Orchestration Plan: Phases 2, 3, & 4

> **Status Update**: 
> *   **Phase 2 (Pricing)**: `pricing` app exists with models. Needs audit & logic verification.
> *   **Phase 3 (Content)**: `import_sitemap.py` exists. Needs execution & verification.
> *   **Phase 4 (Rate Sheets)**: `ratesheets` app exists. Antigravity taking ownership.

## 🤖 1. Prompt for Jules (The Builder)
**Role**: L2 Builder Agent  
**Objective**: Audit & Finalize Phase 2 (Pricing Engine)

```markdown
@Jules You are the Builder. Your goal is to **audit and verify** the Pricing Engine implementation.

**Context**: The `pricing` app already exists in `backend/pricing`. It seemingly has `models.py` and `choices.py`.

**Your Tasks**:
1.  **Code Audit**:
    - Compare `backend/pricing/models.py` against the requirements in `conductor/tracks/phase2_pricing/plan.md`.
    - Check if `LoanMatchingService` exists in `backend/pricing/services/matching.py`.
    - Check if `RateAdjustment` model is fully implemented.

2.  **Verification**:
    - Run the tests: `pytest backend/pricing/tests/`.
    - If tests are missing, create a basic test to verify models can be created.

3.  **Report**:
    - If code is missing or incomplete, **implement it** following the plan.
    - If code is complete and tests pass, mark Phase 2 as **DONE**.
```

---

## 🧠 2. Prompt for Claude (The Generator)
**Role**: L2 Generator Agent  
**Objective**: Execute Phase 3 (Content Migration)

```markdown
@Claude You are the Generator. Your goal is to **execute the content migration** using the existing tools.

**Context**: 
- A migration script exists at `backend/cms/management/commands/import_sitemap.py`.
- The user has noted that the content migration infrastructure is "done".

**Your Tasks**:
1.  **Analyze Script**: Review `import_sitemap.py` to understand how it maps generic sitemap logic to specific Wagtail Page models (`ProgramPage`, `FundedLoanPage`).

2.  **Execute Dry Run**:
    - Run `docker compose exec backend python manage.py import_sitemap --dry-run` to see what it *would* do.

3.  **Execute & Fix**:
    - If the dry run looks good, run the actual import.
    - **CRITICAL**: Watch for validation errors (e.g., missing required fields).
    - If errors occur, patch `import_sitemap.py` to handle them (e.g., provide defaults for missing fields) and retry.

4.  **Verify**:
    - Report the final count of imported pages.
```

---

## 🎻 3. Prompt for Gemini CLI (The Orchestrator)
**Role**: L1 Orchestrator  
**Objective**: Global State Update

```markdown
@Gemini_CLI You are the Conductor.

**Your Tasks**:
1.  **Update `checklist.md`**:
    - Mark Phase 2 as "In Verification" (assigned to Jules).
    - Mark Phase 3 as "In Execution" (assigned to Claude).
    - Mark Phase 4 as "Assigned to Antigravity".
    - **Update Phase 5/6**: Rewrite these phases in `tasks.md` to focus on "Finishing the App" (Frontend Polish, Deployment) rather than new features, as per user request.

2.  **Dispatch**:
    - Trigger the Jules and Claude prompts above.
```

---

## 🐜 4. Prompt for Antigravity (Me)
**Role**: L3 Reviewer / Specialist
**Objective**: Phase 4 (Rate Sheet Agent)

**My Backlog**:
1.  **Audit `ratesheets` App**: Deep dive into `backend/ratesheets` to see if the PDF ingestion pipeline (`tasks.py`, `services/`) is functional.
2.  **Implement Extraction**: If the Gemini 1.5 Pro integration for reading PDFs is missing or broken, I will fix it.
3.  **UI Integration**: Ensure the verified rate sheet data can be exposed to the Pricing Engine.
