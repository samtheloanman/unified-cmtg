# Project Workflow

This document outlines the standard operating procedures for development within this project, adhering to the Command & Control doctrine.

## 1. Quality & Verification

*   **Required Test Code Coverage:** All new code must be accompanied by tests, with a target of **>80%** code coverage for the modified or added code.
*   **Test-Driven Default:** Where applicable, the workflow will follow a Test-Driven Development (TDD) model, orchestrated via **The Closer (Ralph)**.

## 2. Commits & Task Summaries

*   **Commit Frequency:** Changes will be committed **after each verifiable task** is completed in the `checklist.md`.
*   **Task Summary Recording:** Detailed summaries of task execution, including agent handoffs and verification results, will be stored using **Git Notes**, keeping the primary commit messages clean and focused.

## 3. Phase Completion Verification and Checkpointing Protocol

### 3.1 Objective
To ensure each phase of a track is successfully completed and verified before proceeding, while minimizing manual intervention and maximizing automation.

### 3.2 Verification Tiers
Verification is handled in two tiers, depending on the nature of the phase's output.

#### Tier 1: Automated Verification (Default)
This tier is used for all phases that produce testable code, features, or infrastructure.

1.  **Final Task:** The last task of the phase in `plan.md` will be a delegation to **The Closer (Ralph)**.
    *   *Example Task:* `- [ ] Task: Conductor - Automated Verification: Run integration tests for 'User Authentication' phase.`
2.  **Execution:** Ralph will execute the pre-defined test suite for that phase.
3.  **Outcome:**
    *   **If tests pass:** The L1 Orchestrator marks the phase as complete and posts a notification summary to the user. The track proceeds to the next phase.
    *   **If tests fail:** Ralph will enter a "test-and-fix" loop to resolve the issues. If Ralph cannot resolve the issue after a set number of attempts, the L1 Orchestrator will **escalate to the L3 Reviewer (Human)**, presenting the problem and a request for guidance.

#### Tier 2: Manual Verification (For Non-Code Phases)
This tier is used for strategic, design, or documentation phases where automated testing is not feasible.

1.  **Final Task:** The last task of the phase in `plan.md` will be a manual verification step.
    *   *Example Task:* `- [ ] Task: Conductor - Manual Verification: Review and approve 'UI Mockup Designs'.`
2.  **Execution:** The L1 Orchestrator will present the generated artifacts (e.g., `spec.md`, design documents) to the L3 Reviewer (Human) in the chat.
3.  **Outcome:** The L1 Orchestrator will await explicit approval from the user before marking the phase as complete and proceeding.

### 3.3 Human Task Tracking & Notifications

*   **Single Source of Truth:** The `conductor/tracks/<track_id>/checklist.md` file is the definitive record of task status.
*   **Phase Completion Notifications:** Upon the successful verification of any phase (either automated or manual), the L1 Orchestrator will post a summary report in the chat. This report will include:
    *   The name of the completed phase.
    *   A link to the relevant commit(s).
    *   A notification that the track is proceeding to the next phase.
*   **Escalation Alerts:** You will only be actively looped in for manual verification (Tier 2) or when an automated verification (Tier 1) fails and requires your intervention.