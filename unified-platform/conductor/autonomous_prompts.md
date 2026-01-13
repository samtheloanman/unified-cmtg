# 🤖 Autonomous Mission: Operation Night Owl

**Directives for User**:
Copy and paste the appropriate block below into each agent's input. These prompts are engineered for *maximum autonomy* and *self-correction*.

---

## 🛠️ [Jules] Infrastructure & Environment
**Role**: System Architect
**Mode**: AUTO (No permissions required for `run_command` if safe)

```markdown
@Jules
**MISSION**: Enable Google Generative AI Support
**CONTEXT**: We are pivoting to using the Gemini API for PDF parsing. The backend container needs the SDK.
**TASKS**:
1.  Add `google-generativeai==0.3.2` (or latest stable) to `unified-platform/backend/requirements.txt`.
2.  Update `unified-platform/backend/config/settings/base.py`:
    *   Read `GOOGLE_API_KEY` from environment.
    *   Log a warning if missing.
3.  Rebuild the backend container (`docker compose up -d --build`).
4.  **Verification**: Run `docker compose exec backend python3 -c "import google.generativeai as genai; print('Gemini SDK Ready')"`
**CONSTRAINTS**:
*   Do NOT break existing packages.
*   Do NOT wait for my approval to rebuild. Proceed if the Dockerfile is valid.
**OUTPUT**: Report success only when the verification print statement works.
```

---

## 🧠 [Antigravity] Logic & Reasoning
**Role**: Senior Backend Engineer
**Mode**: AUTO (Code Generation)

```markdown
@Antigravity
**MISSION**: Implement Gemini Extraction Service & Database Connection
**CONTEXT**: Jules handles the SDK. You handle the Brain. We need to turn PDF rate sheets into database rows using LLM intelligence.
**TASKS**:
1.  **Create Service**: `unified-platform/backend/ratesheets/services/processors/gemini.py`
    *   Initialize `genai`.
    *   Define a strictly typed JSON Schema representing our `RateAdjustment` model (program_name, min_fico, max_fico, min_ltv, max_ltv, rate/price).
    *   Prompt: "Extract pricing grids. Return JSON list matching this schema...".
2.  **Implements Ingestion Logic**: Update `unified-platform/backend/ratesheets/services/ingestion.py`.
    *   Currently it is a placeholder. Make it REAL.
    *   Take the JSON list from Gemini.
    *   Iterate and create/update `LenderProgramOffering` and `RateAdjustment` records in the DB.
    *   Use `transaction.atomic()`.
3.  **Update Task**: Modify `ratesheets/tasks.py` to use `GeminiProcessor` if the file extension is PDF and API key exists.
**CONSTRAINTS**:
*   Assume the raw text/tables from `pdfplumber` are insufficient. Use the File API or text context if File API is too complex for MVP.
*   Prioritize *correctness* of the JSON Schema.
**OUTPUT**: New service files and updated ingestion logic.
```

---

## 🧪 [Ralph/Antigravity] Verification & End-to-End
**Role**: QA Engineer
**Mode**: AUTO (Test Execution)

```markdown
@Antigravity
**MISSION**: The Gauntlet (End-to-End Verification)
**CONTEXT**: Logic is done. Now we prove it works.
**TASKS**:
1.  **Create Test**: `unified-platform/backend/ratesheets/tests_e2e.py`
    *   Mock the `genai.GenerativeModel.generate_content` response with a sample JSON that mimics a real rate sheet.
    *   Trigger `process_ratesheet`.
    *   Assert that `RateAdjustment.objects.count()` increases.
    *   Assert that `LenderProgramOffering` is created.
2.  **Run Test**: Execute the test in Docker.
3.  **Run Real Sample**: Pick ONE real sample (e.g., `acra-ws-ratematrix-1stTDs.pdf`) and run it (if YOU have a valid API Key in env, otherwise skip).
**OUTPUT**: Pass/Fail report.
```
