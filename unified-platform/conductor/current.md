# Current Sprint: Phase 2 - Pricing Engine Porting

**Date**: 2026-01-13  
**Focus**: Port pricing models and logic from legacy cmtgdirect

---

## 🔴 Immediate Tasks (Today)

| # | Task | Test | Status |
|---|------|------|--------|
| 1 | Verify legacy cmtgdirect on 8000 | `curl localhost:8000/admin/` → 200 | ✅ |
| 2 | Frontend connectivity test | Visit `localhost:3001/test` → "API ok" | ⏳ |
| 3 | Create Wagtail superuser | Login to `localhost:8001/admin/` | ✅ |
| 4 | Create legacy superuser | Login to `localhost:8000/admin/` | ✅ |

---

## ✅ Completed Today

- [x] Django + Wagtail running on 8001
- [x] Health API at `/api/v1/health/`
- [x] Docker compose with `runtime: runc`
- [x] PRD updated with programmatic SEO
- [x] New features spec red-teamed

---

## 🔄 Blockers

| Blocker | Resolution |
|---------|------------|
| WordPress plugins causing errors | Disabled Yoast/Kadence plugins |
| Unified platform needs unique ports | Using 8001/3001/5433/6380 |

---

## 📋 Phase 1 Checklist

- [x] Repo structure created
- [x] Backend Dockerfile
- [x] Frontend Dockerfile
- [x] docker-compose.yml with health checks
- [x] Django project initialized
- [x] Wagtail configured in INSTALLED_APPS
- [x] Health API endpoint
- [x] Migrations applied
- [x] Superuser created (Wagtail: admin/admin)
- [x] Legacy superuser created (cmtgdirect: admin/admin)
- [ ] Frontend API test page

---

## 📆 This Week's Schedule

| Day | Task |
|-----|------|
| Sun | Complete Phase 1 |
| Mon | Start Phase 2: Port models |
| Tue | Phase 2: Port logic |
| Wed | Phase 2: Rate adjustments |
| Thu | Phase 2: Pricing API |
| Fri | Phase 2 verification |
| Sat | Start Phase 3 |

---

**Next Action**: Verify frontend connectivity - visit `http://localhost:3001/test`

