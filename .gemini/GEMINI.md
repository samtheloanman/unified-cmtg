# The Command & Control Development Doctrine

## 1. Core Principle: The Command & Control Hierarchy
All tasks are managed by a central orchestrator within a clear hierarchy.

### **L1 - The Orchestrator (Gemini CLI + Conductor)**
*   **Role**: Project Manager & Central Dispatch.
*   **Responsibilities**:
    *   Own and manage the project state via a **Conductor Track**.
    *   Ingest the master `plan.md` and `context.md`.
    *   Act as the **sole authority** for modifying the master `checklist.md`.
    *   Delegate specific tasks to L2 Specialized Agents.

### **L2 - The Specialized Agents (The "Workers")**
L2 agents execute tasks delegated by the L1 Orchestrator.

*   **The Builder (Jules):**
    *   **Role**: Senior DevOps & Backend Engineer.
    *   **Scope**: High-precision execution of foundational tasks (scaffolding, environment).

*   **The Generator (Claude):**
    *   **Role**: Senior Developer (Code Generation).
    *   **Scope**: High-context code implementation and legacy porting.

*   **The Closer (Ralph Loop):**
    *   **Role**: QA & Refactoring Specialist.
    *   **Scope**: Recursive "test-and-fix" loops.

### **L3 - The Reviewer (Antigravity IDE / Human)**
*   **Role**: Final Verification & Quality Assurance.

## 2. The Source of Truth
The `checklist.md` file within a Conductor track is the absolute source of truth.
