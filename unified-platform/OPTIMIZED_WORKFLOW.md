# Optimized Autonomous Workflow: The "Finisher" Protocol

## 1. The Truth (Current State Analysis)
*   **Codebase**: Next.js 16 (App Router) + Django 5/Wagtail 6.
    *   *Status*: Foundation is solid. Key models (`ProgramPage`) are built.
*   **Documentation**: `GEMINI.md` and `PRD.md` describe a complex, multi-agent "Command & Control" system hosted on "Dell Brain."
*   **Reality Gap**: The "Conductor" tracks (`phase3_content`, etc.) imply a manual, step-by-step handoff process that is too slow for the "Almost Done" phase. The intermediate JSON export steps (F.2) are redundant.

## 2. Red Team Findings (Bottlenecks)
*   **Over-Engineering**: Creating separate JSON exports (`wp_extractor.py`) then importing them (`import_wordpress.py`) doubles the I/O and schema maintenance work.
*   **Rigid Tracks**: The `conductor/tracks/` folder structure encourages linear blocking. We can parallelize Frontend implementation with Backend ingestion.
*   **Manual Orchestration**: "Jules" waiting for "Claude" to write content is inefficient. We should use code generation to build the *generators*, not just the content.

## 3. The New Way: Autonomous Swarm Workflow

### 🚀 Principle: "Code It Once, Run It Forever"
Instead of agents manually performing tasks (extracting, writing), agents write **Management Commands** that perform the tasks autonomously.

### 🔄 The Workflow Loop
1.  **Define**: User sets high-level goal (e.g., "Migrate Content").
2.  **Build**: Agent writes a robust Django Management Command (e.g., `sync_wordpress`).
3.  **Execute**: Run the command. It handles auth, pagination, error retries, and saving.
4.  **Verify**: Agent checks the DB count vs. Source count.

```mermaid
graph TD
    User[User Goal: Finish App] --> Agent[Jules (Builder)]
    Agent --> Code[Write Self-Healing Scripts]
    Code --> Task1[Sync WP Content]
    Code --> Task2[Generate SEO Pages]
    Code --> Task3[Ingest Rate Sheets]
    Task1 & Task2 & Task3 --> DB[(PostgreSQL)]
    DB --> API[GraphQL / API v2]
    API --> Frontend[Next.js Headless]
```

## 4. The Finisher Plan (Strategic Pivot)

We will condense the remaining 5 phases into 3 streamlined tracks.

### Track A: Content Synchronization (Previously F.2, F.3)
*   **Old Plan**: Python Script -> JSON Files -> Django Command.
*   **New Plan**: **Direct Ingestion Command** (`manage.py sync_wordpress`).
    *   Fetches from WP API.
    *   Maps ACF fields in-memory.
    *   Upserts to Wagtail `ProgramPage`.
    *   *Why*: Removes intermediate state, easier to re-run daily.

### Track B: Programmatic SEO Engine (Previously F.4, F.5)
*   **Old Plan**: Complex URL router hacks + CSV imports.
*   **New Plan**: **Generator Command** (`manage.py generate_geo_pages`).
    *   Inputs: `ProgramPage` + `City` list.
    *   Logic: Generates `LocalProgramPage` children under the Program.
    *   URL: Standard Wagtail routing `/{program}/{city}-{state}/` (Cleaner, no hacks).

### Track C: Testing & Deployment (Phase F.X)
*   **Action**: Implement the `TESTING_STRATEGY.md` immediately.
*   **Focus**: E2E "Get a Quote" flow and CMS "Page Load" verification.

## 5. Implementation Roadmap (Next 24 Hours)

1.  **Build `sync_wordpress` Command**:
    *   Hit `https://custommortgageinc.com/wp-json/wp/v2/programs?acf_format=standard`.
    *   Map JSON -> `ProgramPage` model.
    *   Run and Verify.

2.  **Build `generate_geo_pages` Command**:
    *   Create `City` model.
    *   Script: For each Program + Top 100 Cities -> Create Page.

3.  **Frontend Integration**:
    *   Update `frontend/src/app/[...slug]/page.tsx` to render these new pages via API.

---
*Approved for Immediate Execution by System Administrator*
