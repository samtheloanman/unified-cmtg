---
name: Pattern Recognition Engine
tier: 1-Comprehension
category: Understanding
priority: Critical
---

# Pattern Recognition Engine

## Purpose

Identify and document architectural patterns in existing code. Ensures new generated code matches the project's established patterns exactly.

## When to Use (Trigger Conditions)

- Before generating new code in a module
- Understanding reference code provided by L1
- Validating new code matches existing patterns
- Planning refactoring strategies
- Documenting architectural decisions

## Input Parameters

```
files_to_analyze: list or string
  File contents or paths to scan for patterns

pattern_categories: list (default: all)
  Specific patterns to look for:
  ["Repository", "Manager", "Factory", "Builder",
   "Singleton", "Observer", "Strategy", etc.]

language: string (default: auto-detect)
  Target language for pattern context:
  ["Python", "JavaScript", "TypeScript", "SQL"]

include_anti_patterns: boolean (default: true)
  Also identify patterns to AVOID in this codebase

show_evidence: boolean (default: true)
  Include code examples from the codebase
```

## Output Structure

```markdown
## PATTERN ANALYSIS: [file or module]

### Detected Patterns

#### Pattern Name
- **Evidence:** Code location and evidence
- **Purpose:** Why this pattern is used here
- **Usage:** How developers use it in this project
- **How to Replicate:** Clear steps for new code
- **Variation:** Project-specific twist

### Anti-Patterns to Avoid

#### Pattern to Avoid
- **Why:** What's wrong with this pattern
- **Example:** Bad implementation in this project
- **What to Do Instead:** Better approach

### Pattern Relationships

- Pattern A used with Pattern B
- Dependencies and interactions
- Integration guidelines

### Quick Reference

Summary table of patterns and usage frequency
```

## Example Output

```
## PATTERN ANALYSIS: backend/api/models.py

### Detected Patterns

#### Repository/Manager Pattern (Django ORM)

**Evidence:**
File: backend/api/models.py, line 45
```python
class LoanProgramManager(models.Manager):
    def active(self):
        return self.filter(is_active=True).order_by('-created_at')

    def for_lender(self, lender_id):
        return self.filter(lender_id=lender_id)

class LoanProgram(models.Model):
    objects = LoanProgramManager()
```

**Purpose:**
Provides custom query methods for complex filtering. Encapsulates query logic.

**Usage in Project:**
- Used in 12 model definitions (models.py files across all apps)
- Custom managers for filtering, prefetching, related queries
- Always named `<ModelName>Manager`

**How to Replicate:**
1. Create custom Manager class inheriting `models.Manager`
2. Add custom query methods (public methods on manager)
3. Assign to `objects` attribute on model
4. Use in views: `LoanProgram.objects.active()`

**Project-Specific Variations:**
- Some managers include QuerySet subclasses for chaining
- Timestamped filters common (auto_now fields)
- Performance optimization with `select_related()` hints in docstrings

---

#### QuerySet Chaining Pattern

**Evidence:**
File: backend/pricing/models.py
```python
class LoanProgramQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def recent(self):
        return self.order_by('-created_at')

class LoanProgramManager(models.Manager):
    def get_queryset(self):
        return LoanProgramQuerySet(self.model)

    def active(self):
        return self.get_queryset().active()

    def active_and_recent(self):
        return self.active().recent()  # Chainable!
```

**Purpose:**
Allows chaining multiple filters: `LoanProgram.objects.active().recent()`

**Usage:**
Used when complex query chains needed. Less common than simple Manager.

**How to Replicate:**
1. Create custom QuerySet class
2. Add public methods for each filter/operation
3. Create Manager that returns QuerySet
4. Use: `Model.objects.method1().method2()`

---

#### Wagtail StreamField Pattern (CMS Content)

**Evidence:**
File: backend/cms/models.py
```python
class LoanProgramPage(Page):
    body = StreamField([
        ('paragraph', blocks.RichTextBlock()),
        ('highlight', blocks.StructBlock([
            ('title', blocks.CharBlock()),
            ('description', blocks.TextBlock()),
        ])),
    ], null=True, blank=True)
```

**Purpose:**
Flexible content blocks for CMS pages. Non-developers can edit page structure.

**Usage:**
Used in content pages, not data models. Pages inherit from Wagtail Page.

**How to Replicate:**
1. Model inherits from `wagtail.core.models.Page`
2. Define StreamField with block types
3. Allow non-developers to edit in Wagtail admin
4. Render in templates with `{% include_block field %}`

---

#### Signal/Hook Pattern

**Evidence:**
File: backend/api/models.py, bottom
```python
from django.db.models.signals import post_save

def create_default_rates(sender, instance, created, **kwargs):
    if created:
        instance.initialize_default_rates()

post_save.connect(create_default_rates, sender=LoanProgram)
```

**Purpose:**
Automatic actions when model events occur (creation, deletion, save).

**Usage:**
Used for auditing, cache invalidation, related object creation. **Flag for review!**

**How to Replicate:**
1. Import signal: `from django.db.models.signals import post_save`
2. Define signal handler function
3. Connect handler to model via `post_save.connect()`
4. Handler receives: sender, instance, created, kwargs

**Anti-Pattern Warning:**
❌ Don't create complex logic in signals (hard to debug)
❌ Don't create signal dependencies (confusing flow)
✓ Do keep signals simple and clearly documented

---

### Anti-Patterns to Avoid

#### Raw SQL Queries in Views

**Why:**
- Security vulnerability (SQL injection)
- Hard to maintain (SQL changes break code)
- Not portable (database-specific syntax)
- Misses Django ORM benefits (caching, prefetch)

**Bad Example (Don't do this!):**
```python
# ❌ WRONG - Raw SQL in view
def get_rates(request):
    cursor = connection.cursor()
    rates = cursor.execute(
        "SELECT * FROM api_rateadjustment WHERE fico_min <= %s",
        [request.GET.get('fico')]
    )
```

**What to Do Instead:**
```python
# ✓ RIGHT - Use Django ORM
def get_rates(request):
    fico = int(request.GET.get('fico'))
    rates = RateAdjustment.objects.filter(
        fico_min__lte=fico
    ).select_related('loan_program')
```

---

#### Overly Complex Model Methods

**Why:**
- Violates Single Responsibility Principle
- Hard to test
- Business logic scattered across codebase
- Difficult to reuse

**Anti-Pattern:**
```python
# ❌ Model doing too much
class LoanApplication(models.Model):
    def send_email_and_update_status_and_notify_lender(self):
        # 50 lines of email, status, notification logic
        pass
```

**Better Approach:**
```python
# ✓ Split responsibilities
class LoanApplication(models.Model):
    def approve(self):
        """Change status to approved"""
        self.status = 'approved'
        self.save()

# In a service module or Celery task:
def handle_approval(application_id):
    """Handle all side effects of approval"""
    app = LoanApplication.objects.get(id=application_id)
    send_approval_email(app)
    notify_lender(app)
    update_external_systems(app)
```

---

#### Missing Database Constraints

**Why:**
- Data integrity issues
- Race conditions possible
- Inconsistent state possible
- Database queries become defensive

**Pattern to Implement:**
```python
# ✓ Include constraints in Meta
class LoanProgram(models.Model):
    loan_amount_min = models.DecimalField(...)
    loan_amount_max = models.DecimalField(...)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(loan_amount_max__gt=models.F('loan_amount_min')),
                name='loan_amount_max_greater_than_min'
            ),
        ]
```

---

### Pattern Relationships

**Manager → Serializer → View Flow:**
```
Custom Manager (complex queries)
    ↓
DRF Serializer (JSON conversion)
    ↓
ViewSet (HTTP request handling)
    ↓
Response to client
```

**Model → Migration → Test Flow:**
```
Model definition
    ↓
Django migration (schema change)
    ↓
Tests verify migration works
    ↓
Safe deployment
```

---

### Quick Reference Table

| Pattern Name | Frequency | Difficulty | Common Use |
|---|---|---|---|
| Manager/Repository | Very High | Low | Query optimization |
| Signal/Hook | Medium | Medium | Auto-creation, auditing |
| QuerySet Chaining | Medium | Medium | Complex filtering |
| StreamField | High | Medium | CMS content |
| Validators | High | Low | Data validation |
| Permissions | High | Medium | API access control |

---

## How I Use This Skill

**Before Generating Code:**
1. Analyze reference code with Pattern Recognition Engine
2. Identify key patterns: Manager, Serializer, Validation style
3. Note project-specific variations
4. Generate new code using exact same patterns

**Example:**
```
Task: Generate RateAdjustment model similar to LoanProgram

Step 1: Detect patterns in LoanProgram
  - Uses custom Manager with active() method
  - Has custom clean() validation
  - Includes created_at/updated_at timestamps
  - Has business logic methods with docstrings

Step 2: Generate RateAdjustment following same patterns
  - Same Manager structure
  - Same validation approach
  - Same timestamp fields
  - Similar docstring style
```

## Quality Checklist

When analyzing patterns, I verify:
- [ ] All patterns identified with code evidence
- [ ] Anti-patterns clearly marked
- [ ] How to replicate instructions clear
- [ ] Project-specific variations noted
- [ ] Pattern relationships documented
- [ ] Quick reference accurate
- [ ] No conflicting patterns identified

---

**Next Step:** Use detected patterns as blueprint for new code generation.
