# Open Broker LOS - Project Brief

**Mission:** Build an open-source, broker-centric Loan Origination System (LOS) that gives brokers ownership of their data.
**Core Philosophy:** "Data Sovereignty." Don't lock data inside proprietary JSON blobs (like Floify) or PDF forms. Flatten the standard 1003 (MISMO v3.4) into a queryable, relational database.

## 🚀 The Vision
Most LOS platforms (LendingPad, Encompass, Floify) are black boxes. You submit data, they hold it. We want to build a **Headless LOS Core** that:
1.  **Ingests MISMO 3.4/Fannie Mae 3.2** data (from Floify, Calyx, etc.).
2.  **Stores it Relationally**: Instead of one huge JSON blob, we break it down into `Borrowers`, `Assets`, `Liabilities`, `Properties`, etc.
3.  **Exposes an API**: For pricing engines, doc generators, and CRMs.

## 🏗 Architecture (Proposed)

### 1. The Core (Django)
We will use Django because its ORM is perfect for complex relational modeling (and MISMO is *very* relational).
*   **App**: `open_los`
*   **Database**: PostgreSQL
*   **API**: Django Ninja (faster/simpler than DRF) or stick to DRF.

### 2. The Data Model (The Hard Part)
We need to map the "UrlA" (Uniform Residential Loan Application) to tables.
*   `LoanApplication` (The root)
*   `Borrower` (linked to Application)
*   `EmploymentEntry` (linked to Borrower)
*   `AssetEntry` (linked to Borrower/Application)
*   `LiabilityEntry` (linked to Borrower)
*   `RealEstateOwned` (linked to Borrower)
*   `LoanTransactionDetails` (The numbers: Purchase Price, Loan Amount, LTV)

## 🛠 Roadmap

### Phase 1: The Schema (Day 1)
*   Define the Django models that mirror the 1003 Sections.
*   Focus on the "Critical 50%" fields first (ignoring obscure edge cases).

### Phase 2: The Ingestor
*   Build a parser that takes the `Floify 1003 JSON` (or Fannie 3.2 file) and "hydrates" our database tables.

### Phase 3: The API
*   Endpoints to `GET /application/{id}` and receive the full reconstructed object.

---

## 📂 Project Location
`unified-cmtg/open-broker-los/`
