# 🌙 Operation Night Owl 3.0: Multimodal Intelligence (Gemini API)

**Mission Update**: We are upgrading to the **Gemini 1.5 Pro/Flash API**. Instead of "parsing tables," we will have the LLM "read" the PDF and generate structured JSON that maps directly to our database models.

---

## 🏗️ Task 1: Jules - The GenAI Integrator
**Objective**: Prepare the Django environment for Google Generative AI integration.

### 🛡️ Constraints & Safety Directives
1.  **Lightweight**: The `google-generativeai` SDK is much lighter than OCR binaries.
2.  **Environment Variables**: Ensure `GOOGLE_API_KEY` is read from `os.environ`.
3.  **Security**: Do not log full API responses if they contain sensitive PII (though rate sheets are usually public B2B data).

### 📋 Execution Plan
1.  **Dependency Upgrade**:
    *   Add `google-generativeai` to `requirements.txt`.
2.  **Configuration**:
    *   Update `config/settings/base.py` to check for `GOOGLE_API_KEY`.
    *   Add logging warning if key is missing (Graceful degradation).
3.  **Build**:
    *   Rebuild backend (`docker compose up -d --build`).

---

## 🧠 Task 2: Antigravity - The Prompt Engineer
**Objective**: Create a `GeminiExtractionService` that uploads PDFs and strictly enforces a JSON schema output for 100% data integrity.

### 🔬 Deep Research & Thinking Requirements
*   **The "Context" Advantage**: Gemini can distinguish between a "30 Year Fixed" table and a "Arm 5/1" table implies semantic understanding.
*   **Safety Mechanism**: LLMs can hallucinate digits.
    *   *Requirement*: Implementing a "Confidence Check" or "Double Pass" ideally, but for MVP, we rely on strict Schema.
*   **Schema Definition**:
    *   Define a Python `TypedDict` or JSON Schema that exactly matches `Ratesheet.programs[]` structure.
    *   Fields: `program_name`, `min_fico`, `max_fico`, `ltv_buckets` (list of `{max_ltv, adjustment}`).

### 📋 Execution Plan
1.  **Create Service**: `ratesheets/services/processors/gemini.py`.
2.  **Implement Client**:
    *   `genai.configure(api_key=...)`.
    *   `genai.upload_file(path)` (Leverage the File API for PDF ingestion).
3.  **The Master Prompt**:
    *   Context: "You are a Mortgage Underwriting Assistant. Extract all pricing adjustments from this rate sheet."
    *   Constraint: "Return ONLY valid JSON matching this schema..."
    *   Handling: "If a value is 'msg' or 'contact', ignore or mark as null."
4.  **Integration**:
    *   Update the `process_ratesheet` task to use this service if `GOOGLE_API_KEY` is present.

---

## 🚀 Handoff Protocol
*   **Jules**: Install SDK.
*   **Antigravity**: Write the Prompt & Schema Logic.
