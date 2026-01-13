# Conductor Tracks - Unified CMTG Platform

> **Purpose**: Workflow tracks for AI agents. Each track = major workstream.  
> **Rule**: Task complete only when tests pass ✅

---

## 🎯 Track Overview

| Track | Phase | Week | Status | Description |
|-------|-------|------|--------|-------------|
| [Foundation](./tracks/phase1_foundation/) | 1 | 1 | 🟡 In Progress | Docker + Django + Wagtail |
| [Pricing Engine](./tracks/phase2_pricing/) | 2 | 2 | ⏳ Pending | Port cmtgdirect logic |
| [Content Migration](./tracks/phase3_content/) | 3 | 3 | ⏳ Pending | WordPress → Wagtail |
| [Programmatic SEO](./tracks/phase3a_seo/) | 3a | 4 | ⏳ Pending | 10K+ local pages |
| [Rate Sheet Agent](./tracks/phase4_ratesheet/) | 4 | 5 | ⏳ Pending | PDF extraction |
| [Floify Integration](./tracks/phase5_floify/) | 5 | 6 | ⏳ Pending | Lead capture |
| [AI Blog](./tracks/phase6_blog/) | 6 | 7-8 | ⏳ Pending | NotebookLM + content |
| [Affiliate Program](./tracks/phase7_affiliate/) | 7 | 9 | ⏳ Pending | Referral tracking |
| [Investment Waitlist](./tracks/phase8_investment/) | 8 | 10 | ⏳ Pending | Coming soon MVP |
| [Community Forum](./tracks/phase9_forum/) | 9 | 11-12 | ⏳ Deferred | Forum engine |

---

## 🔴 Current Priority

**Active Track**: Phase 1 - Foundation  
**Next Task**: Verify frontend connectivity test

---

## 🤖 Agent Assignments

| Track | Primary Agent | Support |
|-------|---------------|---------|
| Foundation | QA Tester | Pricing Engineer |
| Pricing Engine | Pricing Engineer | QA Tester |
| Content Migration | Wagtail Expert | Frontend Architect |
| Programmatic SEO | Wagtail Expert | Rate Sheet Agent |
| Rate Sheets | Rate Sheet Agent | Pricing Engineer |
| Floify | Frontend Architect | Pricing Engineer |
| AI Blog | Content Agent | Marketing Automation |
| Affiliate | Marketing Agent | Pricing Engineer |
| Investment | Research Agent | Legal |
| Forum | Frontend Architect | Moderation Agent |

---

## 🔗 Dependencies

```mermaid
flowchart TD
    P1[Phase 1: Foundation] --> P2[Phase 2: Pricing]
    P1 --> P3[Phase 3: Content]
    P2 --> P4[Phase 4: Rate Sheets]
    P3 --> P3a[Phase 3a: Programmatic SEO]
    P3a --> P5[Phase 5: Floify]
    P4 --> P5
    P5 --> P6[Phase 6: AI Blog]
    P5 --> P7[Phase 7: Affiliate]
    P6 --> P8[Phase 8: Investment]
    P7 --> P8
    P8 --> P9[Phase 9: Forum]
```

---

## 📋 How to Use

### Start a Track
```bash
/conductor start phase1_foundation
```

### Track Structure
```
tracks/phase1_foundation/
├── plan.md          # Task breakdown + tests
├── context.md       # Background for agents
└── checklist.md     # Progress tracking
```

---

## 📊 Research Tasks Queue

| Task | Priority | Status |
|------|----------|--------|
| Best affordable RE API | High | ⏳ Pending |
| Affiliate disclaimer | High | ⏳ Pending |
| Misago alternatives | Medium | ⏳ Pending |
| DST 1031 structure | Medium | ⏳ Pending |

---

**Last Updated**: 2026-01-12 01:14 PST
