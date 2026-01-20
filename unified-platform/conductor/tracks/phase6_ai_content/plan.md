# Phase F.6: AI Content Generation Pipeline

## 🎯 Objective
Enable high-fidelity, compliant, and localized content generation for 100+ mortgage programs using the Gemini 2.0 Flash model.

## 🏗️ Technical Implementation

### 1. AI Service Layer (`cms/services/ai_content_generator.py`)
- **Dual Provider Support**: Gemini 2.0 Flash (Primary) + OpenAI (Fallback)
- **Dynamic Persona Injection**: 
  - Automatically identifies program topics (e.g., SBA, Commercial, VA)
  - injects specific expert personas (e.g., "Senior Commercial Underwriter", "Military Specialist")
- **JSON Structured Output**: Forces LLMs to return strict JSON for direct schema mapping

### 2. Program Content (`manage.py generate_program_content`)
- **Scope**: Populates primary `ProgramPage` nodes
- **Fields Generated**: 
  - `mortgage_program_highlights` (HTML)
  - `what_are` (HTML)
  - `benefits_of` (HTML)
  - `requirements` (HTML)
  - `faq` (StreamField)
  - `seo_title` & `seo_description`

### 3. Local Landing Pages (`manage.py generate_local_pages`)
- **Scope**: Creates `LocalProgramPage` nodes (e.g., /fha-loans-los-angeles-ca/)
- **Logic**:
  - Assigns nearest `Office` via Haversine distance
  - Generates localized Intro + FAQs
  - Injects `LocalBusiness` + `MortgageLoan` Schema markup

### 4. Master Hierarchy
- **Source**: `program_hierarchy.md`
- **Coverage**: 100+ defined loan programs
- **Shells**: Auto-created for any missing programs via `create_program_shells`

## 🛡️ Security
- **API Key Management**: Rotated compromised key. New key stored in `.env.local`, removed from `docker-compose.yml`.

## 🧪 Verification
- **Run**: `python manage.py generate_program_content --programs super-jumbo --force`
- **Output**: Verified HTML content, correct FAQs, and SEO tags.
