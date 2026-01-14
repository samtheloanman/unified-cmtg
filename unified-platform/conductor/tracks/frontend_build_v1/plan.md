# Conductor Track: High-Fidelity Frontend Build (v1)

**Phase**: Phase 5 (Frontend)
**Source of Truth**: [designOS_instructions.md](file:///home/samalabam/.gemini/antigravity/brain/969d8981-5a6e-4d06-a2dc-6044e954466b/designOS_instructions.md)
**Status**: ⏳ PENDING REVIEW

## Overview
This track manages the implementation of the `unified-cmtg` frontend using the specs and components exported from `designOS`. It follows a "Specification-First" approach to ensure a 1:1 clone of `custommortgageinc.com`.

## Agent Assignments
- **Orchestrator (L1)**: Central management of the track.
- **Frontend Architect (L2)**: Integrates designOS components and wires them to Wagtail.
- **QA Tester (L2)**: Verifies UI fidelity and responsiveness.

## Tasks

### 1. Integration Setup
- [ ] Import `product-plan/` from `designOS` export.
- [ ] Initialize `unified-platform/frontend/src/components/design-system` with `colors.json` and `typography.json`.
- [ ] Update `tailwind.config.ts` to reflect brand design tokens.

### 2. Application Shell
- [ ] Implement `Header` component from shell spec.
- [ ] Implement `Footer` component from shell spec.
- [ ] Update `app/layout.tsx` to include the branded shell.

### 3. Template Implementation
- [ ] **Home Page**: Implement `HomeTemplate` using `product-plan/sections/home-page/`.
- [ ] **Program Page**: Implement `ProgramTemplate` with Wagtail StreamField integration.
- [ ] **Funded Loans**: Implement `FundedLoansTemplate` with grid layout.
- [ ] **Locations**: Implement `LocationTemplate` for programmatic SEO.

### 4. Interactive Components
- [ ] **Quote Wizard**: Integrate the step-based wizard and connect to `/api/v1/quote/`.
- [ ] **Rate Table**: Implement the dynamic rate table with sorting/filtering.

## Success Criteria
- [ ] Frontend matches `custommortgageinc.com` visual hierarchy.
- [ ] Accessibility score > 90.
- [ ] All components are 1:1 with `designOS` specifications.
- [ ] Quote Wizard successfully returns rates from the seeded Django backend.
