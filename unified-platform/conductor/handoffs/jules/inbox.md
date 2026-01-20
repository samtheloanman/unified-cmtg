# Jules Inbox

## F.9 Production Hardening & Testing - Guidance

**Priority**: HIGH  
**From**: Antigravity (Gemini CLI)  
**Date**: 2026-01-20 15:51 PST

---

### Phase F.9 Execution Strategy

Based on the current status (F.1-F.8 ✅ Complete), you are cleared to proceed with F.9 Production Hardening & Testing.

### ✅ What You Should Do

#### 1. Security Audit (Your Primary Focus)
```bash
cd unified-platform/backend

# System checks
python manage.py check --deploy

# Environment validation
python manage.py shell
>>> from django.conf import settings
>>> print(f"DEBUG: {settings.DEBUG}")  # Should be False for production
>>> print(f"SECRET_KEY source: {'ENV' if os.getenv('SECRET_KEY') else 'HARDCODED'}")
>>> print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
>>> print(f"CORS_ALLOWED_ORIGINS: {settings.CORS_ALLOWED_ORIGINS}")
```

**Expected actions:**
- [ ] Verify `DEBUG=False` in production settings
- [ ] Confirm `SECRET_KEY` loaded from environment variable
- [ ] Review CORS whitelist (should only include production domains)
- [ ] Check SQL injection prevention (Django ORM handles this, verify no raw SQL)
- [ ] Check XSS prevention (template auto-escaping enabled)

#### 2. Performance Optimization (Your Secondary Focus)
```bash
# Add database indexes for common queries
# Check models: ProgramPage, LocalProgramPage, City, Office
# Look for fields commonly used in WHERE/JOIN clauses

# Example in cms/models/pages.py:
class Meta:
    indexes = [
        models.Index(fields=['slug']),
        models.Index(fields=['state']),
        models.Index(fields=['live', '-first_published_at']),
    ]
```

**Configuration tasks:**
- [ ] Add database indexes to models
- [ ] Configure Django cache framework (Redis recommended)
- [ ] Review static file serving strategy
- [ ] Implement Docker multi-stage builds (if not done)

### ⏸️ What To Defer to Antigravity

#### E2E Testing (Antigravity's Responsibility)
- Browser-based End-to-End tests
- Quote Wizard flow testing
- Program page load testing
- Local page load testing

#### SEO Verification (Antigravity's Responsibility)
- Sitemap.xml generation
- robots.txt configuration
- Meta tag verification across pages
- Schema markup validation
- Lighthouse SEO scoring

#### Load Testing (Gemini CLI with Antigravity)
- Locust/Apache Bench installation
- API endpoint load testing
- Concurrent user simulation
- Response time profiling

---

### 🎯 Your Success Criteria for F.9

Complete these items, then report back:

1. **Security Audit**: All `manage.py check --deploy` warnings resolved
2. **Environment Config**: Production settings properly externalized
3. **Database Optimization**: Indexes added to high-traffic models
4. **Cache Strategy**: Redis or equivalent configured
5. **Docker**: Multi-stage build implemented (if applicable)

**Report Format (to `conductor/handoffs/gemini/inbox.md`):**
```
## F.9 Security & Performance Complete

**Completed**:
- ✅ Django deploy checks passed
- ✅ Environment variables validated
- ✅ CORS whitelist configured
- ✅ Database indexes added ([N] models updated)
- ✅ Cache backend configured

**Ready for**:
- E2E Testing (Antigravity)
- SEO Verification (Antigravity)
- Load Testing (Gemini CLI)

**Blockers**: [None / List any issues]
```

---

### 📋 Reference Materials

- Checklist: `conductor/tracks/finalization_20260114/checklist.md` (lines 170-210)
- Django Deploy Checklist: https://docs.djangoproject.com/en/stable/howto/deployment/checklist/
- Security Settings: https://docs.djangoproject.com/en/stable/topics/security/

---

### Questions Answered (from Prior Conversation)

Based on conversation history, here are answers to common F.9 questions:

| Question | Answer |
|----------|--------|
| Should I run live API tests (OpenRouter, Floify)? | **No** - F.8 already validated Floify integration. F.6 validated AI content generation. Focus on static analysis and configuration review. |
| Should I create test pages/data? | **No** - Read-only verification preferred. F.1-F.8 already seeded necessary data. |
| Can I run `pip install` safely? | **Yes** - requirements.txt is the source of truth. Safe to install. |
| Is this a "health check" or full hardening? | **Full hardening** - This is production prep, not just verification. Apply all security best practices. |

---

### ⚠️ Escalation Points

Escalate to Gemini CLI if:
- Deploy checks reveal critical security issues
- Database migration conflicts
- Docker build failures
- Need clarification on production deployment strategy

---

*Dispatched by Antigravity Meta-Orchestrator*
