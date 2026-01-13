# 🏁 FINAL SPRINT: Browser-Testable MVP

## 📊 Current Status (2026-01-13 12:15 PST)

| Component | Status | URL |
|-----------|--------|-----|
| **Backend API** | ✅ Working | http://localhost:8001 |
| **Frontend** | 🔴 Default Page | http://localhost:3001 |
| **Database** | ✅ Running | postgres:5433 |
| **Redis** | ✅ Running | redis:6380 |
| **Google API Key** | ✅ Configured | Set in docker-compose |

---

## 🚧 What's Missing for Browser Test

| Gap | Who | Time |
|-----|-----|------|
| **Frontend Quote Page** (`/quote`) | Jules | 20 min |
| **Seed Data** (Lender, Programs, Adjustments) | Jules | 10 min |
| **Frontend API Connection** | Jules | 10 min |

---

## 🎯 Agent Prompts for Final Sprint

---

### 📋 JULES PROMPT (Primary - Do This First)

```markdown
# MISSION: Complete Frontend Quote Page

## CONTEXT
- Backend API is working at http://localhost:8001/api/v1/quote/
- Frontend is on port 3001 but shows default Next.js page
- Need to create /quote route with form

## TASK 1: Create Quote Page (20 min)
File: `frontend/src/app/quote/page.tsx`

```tsx
'use client';
import { useState } from 'react';

export default function QuotePage() {
  const [formData, setFormData] = useState({
    property_state: 'CA',
    loan_amount: 500000,
    credit_score: 740,
    property_value: 650000
  });
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8001/api/v1/quote/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const data = await res.json();
      setResults(data);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <h1 className="text-3xl font-bold mb-8">Mortgage Quote Calculator</h1>
      
      <form onSubmit={handleSubmit} className="max-w-md space-y-4">
        <div>
          <label>State</label>
          <input 
            type="text" 
            value={formData.property_state}
            onChange={(e) => setFormData({...formData, property_state: e.target.value})}
            className="w-full p-2 bg-gray-800 rounded"
          />
        </div>
        <div>
          <label>Loan Amount</label>
          <input 
            type="number" 
            value={formData.loan_amount}
            onChange={(e) => setFormData({...formData, loan_amount: Number(e.target.value)})}
            className="w-full p-2 bg-gray-800 rounded"
          />
        </div>
        <div>
          <label>Credit Score</label>
          <input 
            type="number" 
            value={formData.credit_score}
            onChange={(e) => setFormData({...formData, credit_score: Number(e.target.value)})}
            className="w-full p-2 bg-gray-800 rounded"
          />
        </div>
        <div>
          <label>Property Value</label>
          <input 
            type="number" 
            value={formData.property_value}
            onChange={(e) => setFormData({...formData, property_value: Number(e.target.value)})}
            className="w-full p-2 bg-gray-800 rounded"
          />
        </div>
        <button 
          type="submit" 
          disabled={loading}
          className="w-full p-3 bg-blue-600 hover:bg-blue-700 rounded font-bold"
        >
          {loading ? 'Loading...' : 'Get Quote'}
        </button>
      </form>

      {results && (
        <div className="mt-8 p-4 bg-gray-800 rounded">
          <h2 className="text-xl font-bold mb-4">Results</h2>
          <pre>{JSON.stringify(results, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
```

## TASK 2: Create Seed Data Command (10 min)
File: `backend/pricing/management/commands/seed_data.py`

```python
from django.core.management.base import BaseCommand
from pricing.models import Lender, ProgramType, LenderProgramOffering, RateAdjustment

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Create lender
        lender, _ = Lender.objects.get_or_create(
            company_name="Acra Lending",
            defaults={'include_states': ['CA','TX','FL'], 'is_active': True}
        )
        
        # Create program
        program, _ = ProgramType.objects.get_or_create(
            name="DSCR 30-Year Fixed",
            defaults={
                'category': 'non_qm',
                'property_types': ['residential'],
                'entity_types': ['individual'],
                'purposes': ['purchase'],
                'occupancy': ['investment'],
                'base_min_fico': 660,
                'base_max_ltv': 80.0
            }
        )
        
        # Create offering
        offering, _ = LenderProgramOffering.objects.get_or_create(
            lender=lender, program_type=program,
            defaults={
                'min_rate': 7.25, 'max_rate': 8.5,
                'min_fico': 660, 'max_ltv': 80.0,
                'min_loan': 75000, 'max_loan': 2000000,
                'is_active': True
            }
        )
        
        self.stdout.write(self.style.SUCCESS('Seed data created!'))
```

Run: `docker compose exec backend python manage.py seed_data`

## TASK 3: Verify
1. Open http://localhost:3001/quote
2. Fill form, click "Get Quote"
3. See results
```

---

### 📋 CLAUDE CODE PROMPT (Secondary)

```markdown
# MISSION: Fix Any Integration Issues

After Jules creates the frontend, verify:
1. CORS is enabled for frontend requests
2. API returns proper response format
3. Matching service queries real data

Check `backend/config/settings/base.py` for CORS:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
]
```

Run tests: `docker compose exec backend python manage.py test`
```

---

### 📋 GEMINI CLI PROMPT

```markdown
# MISSION: Full Integration Verification

After Jules and Claude finish:
1. Test API: curl http://localhost:8001/api/v1/quote/
2. Test Frontend: curl http://localhost:3001/quote
3. Run tests: docker compose exec backend python manage.py test
4. Report any failures
```

---

## ✅ Success Criteria

- [ ] http://localhost:3001/quote shows quote form
- [ ] Form submits and displays results
- [ ] Results show at least 1 matching program
- [ ] All backend tests pass
