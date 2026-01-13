# TypeScript Style Guide - Unified CMTG Platform

This document defines TypeScript and Next.js conventions for the Unified CMTG Platform, based on Google TypeScript Style Guide with React/Next.js specific patterns.

## 1. Foundational Rules (Google Style Guide)

### 1.1 Language Rules
- **Variables:** Always `const` by default. Use `let` for reassignment. **Never `var`.**
- **Modules:** Use ES6 imports/exports. **No namespaces.**
- **Exports:** Named exports preferred. Avoid default exports (except for Next.js pages).
- **Type Assertions:** Avoid (`x as Type`). Let TypeScript infer or use explicit types.
- **Equality:** Always `===` and `!==` (never `==` or `!=`).
- **Semicolons:** Required at end of statements (enforced by Prettier).

### 1.2 Type System
- **`any` Type:** Forbidden. Use `unknown` or a specific type.
- **`{}` Type:** Never. Use `Record<string, unknown>` or `object`.
- **Optional:** Prefer `field?: Type` over `field: Type | undefined`.
- **Array Types:** Use `Type[]` for simple types, `Array<Type | string>` for unions.
- **`null` vs `undefined`:** Use `undefined` by default for Optional types.

### 1.3 Naming
- **Classes/Interfaces/Types/Enums:** `PascalCase`
- **Variables/Functions/Methods/Properties:** `lowerCamelCase`
- **Constants:** `CONSTANT_CASE` (module-level only)
- **No `_` prefix/suffix** for anything (including private, unused)

### 1.4 Comments
- **JSDoc:** `/** description */` for public APIs
- **Inline:** `// comment` for implementation
- **No type declarations in JSDoc:** TypeScript has types already

---

## 2. Next.js & React Patterns

### 2.1 Component Structure (App Router)
```typescript
// components/LoanPrograms/LoanProgramCard.tsx
import { FC, ReactNode } from 'react';
import Link from 'next/link';

interface LoanProgramCardProps {
  id: number;
  name: string;
  lenderName: string;
  minCreditScore: number;
  description?: ReactNode;
}

/**
 * Card component displaying a single loan program.
 * Used in listings and search results.
 */
export const LoanProgramCard: FC<LoanProgramCardProps> = ({
  id,
  name,
  lenderName,
  minCreditScore,
  description,
}) => {
  return (
    <article className="rounded-lg border border-gray-200 p-4 shadow-sm hover:shadow-md">
      <h3 className="mb-2 text-lg font-semibold">{name}</h3>
      <p className="mb-4 text-sm text-gray-600">{lenderName}</p>
      {description && <p className="mb-4 text-sm">{description}</p>}
      <div className="mb-4 flex items-center justify-between">
        <span className="text-xs text-gray-500">Min FICO: {minCreditScore}</span>
      </div>
      <Link
        href={`/loan-programs/${id}`}
        className="inline-block rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
      >
        View Details
      </Link>
    </article>
  );
};
```

### 2.2 Server Components (Data Fetching)
```typescript
// app/loan-programs/page.tsx
import { LoanProgramList } from '@/components/LoanPrograms/LoanProgramList';

interface SearchParams {
  lender?: string;
  page?: string;
}

interface PageProps {
  searchParams: Promise<SearchParams>;
}

/**
 * Loan Programs listing page.
 * Server component with async data fetching.
 */
export default async function LoanProgramsPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const page = parseInt(params.page ?? '1', 10);
  const lenderId = params.lender ? parseInt(params.lender, 10) : undefined;

  try {
    const data = await fetchLoanPrograms({ page, lenderId });
    return <LoanProgramList data={data} />;
  } catch (error) {
    return <ErrorFallback error={error} />;
  }
}
```

### 2.3 Client Components (Interactivity)
```typescript
// components/QuoteWizard.tsx
'use client';

import { FC, FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';

interface QuoteFormData {
  propertyState: string;
  loanAmount: number;
  creditScore: number;
  ltv: number;
}

/**
 * Interactive quote wizard for loan matching.
 * Requires 'use client' directive.
 */
export const QuoteWizard: FC = () => {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    const formData = new FormData(e.currentTarget);
    const data: QuoteFormData = {
      propertyState: formData.get('property_state') as string,
      loanAmount: parseInt(formData.get('loan_amount') as string, 10),
      creditScore: parseInt(formData.get('credit_score') as string, 10),
      ltv: parseFloat(formData.get('ltv') as string),
    };

    try {
      const response = await fetch('/api/v1/quote/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const result = await response.json();
      router.push(`/results?id=${result.quote_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && <p className="text-red-600">{error}</p>}
      {/* Form fields */}
      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Loading...' : 'Get Quotes'}
      </button>
    </form>
  );
};
```

---

## 3. Type Definitions

### 3.1 Types Organization
```typescript
// types/loan.ts
export type LoanPurpose = 'purchase' | 'refinance' | 'cash-out';
export type PropertyType = 'single-family' | 'multi-family' | 'commercial';
export type Occupancy = 'primary' | 'second-home' | 'investment';

export interface LoanProgram {
  id: number;
  name: string;
  lenderId: number;
  minCreditScore: number;
  maxLTV: number;
  baseRate: number;
  createdAt: string;
}

export interface QuoteRequest {
  propertyState: string;
  loanAmount: number;
  creditScore: number;
  ltv: number;
  loanPurpose: LoanPurpose;
  propertyType: PropertyType;
  occupancy: Occupancy;
}

export interface QuoteResponse {
  quoteId: string;
  matchingPrograms: LoanProgram[];
  timestamp: string;
}
```

### 3.2 Strict Typing
```typescript
// ✅ Good
interface User {
  id: number;
  name: string;
  email: string;
  role: 'admin' | 'user' | 'guest';
}

const getUser = (id: number): Promise<User | null> => {
  // ...
};

// ❌ Bad
interface User {
  [key: string]: any; // Too loose
}

const getUser = (id: unknown) => {
  // No return type
  return fetch(`/api/users/${id}`);
};
```

---

## 4. API Client Pattern

### 4.1 Typed API Client
```typescript
// lib/api.ts
import { QuoteRequest, QuoteResponse } from '@/types/loan';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

/**
 * Fetch from API with error handling and typed responses.
 */
async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new ApiError(
      response.status,
      error.detail || `API error: ${response.statusText}`,
    );
  }

  return response.json() as Promise<T>;
}

export const loanApi = {
  getPrograms: (lenderId?: number) =>
    fetchApi<LoanProgram[]>(`/loan-programs/?lender=${lenderId ?? ''}`),

  getQuote: (request: QuoteRequest) =>
    fetchApi<QuoteResponse>('/quote/', {
      method: 'POST',
      body: JSON.stringify(request),
    }),
};
```

---

## 5. Custom Hooks Pattern

### 5.1 Data Fetching Hooks
```typescript
// hooks/useQuote.ts
import { useCallback, useEffect, useState } from 'react';
import { QuoteRequest, QuoteResponse } from '@/types/loan';
import { loanApi } from '@/lib/api';

interface UseQuoteState {
  data: QuoteResponse | null;
  isLoading: boolean;
  error: Error | null;
}

export const useQuote = (request: QuoteRequest | null) => {
  const [state, setState] = useState<UseQuoteState>({
    data: null,
    isLoading: false,
    error: null,
  });

  const fetchQuote = useCallback(async (req: QuoteRequest) => {
    setState({ data: null, isLoading: true, error: null });
    try {
      const data = await loanApi.getQuote(req);
      setState({ data, isLoading: false, error: null });
    } catch (error) {
      setState({
        data: null,
        isLoading: false,
        error: error instanceof Error ? error : new Error('Unknown error'),
      });
    }
  }, []);

  useEffect(() => {
    if (request) {
      fetchQuote(request);
    }
  }, [request, fetchQuote]);

  return { ...state, refetch: () => request && fetchQuote(request) };
};
```

---

## 6. Testing Patterns

### 6.1 Jest + React Testing Library
```typescript
// __tests__/LoanProgramCard.test.tsx
import { render, screen } from '@testing-library/react';
import { LoanProgramCard } from '@/components/LoanPrograms/LoanProgramCard';

describe('LoanProgramCard', () => {
  it('renders program details', () => {
    render(
      <LoanProgramCard
        id={1}
        name="30-Year Fixed"
        lenderName="Test Bank"
        minCreditScore={680}
      />,
    );

    expect(screen.getByText('30-Year Fixed')).toBeInTheDocument();
    expect(screen.getByText('Test Bank')).toBeInTheDocument();
    expect(screen.getByText(/Min FICO: 680/)).toBeInTheDocument();
  });

  it('renders optional description', () => {
    render(
      <LoanProgramCard
        id={1}
        name="30-Year Fixed"
        lenderName="Test Bank"
        minCreditScore={680}
        description="Premium rates"
      />,
    );

    expect(screen.getByText('Premium rates')).toBeInTheDocument();
  });
});
```

### 6.2 E2E Tests (Playwright)
```typescript
// e2e/quote-wizard.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Quote Wizard', () => {
  test('should submit quote and show results', async ({ page }) => {
    await page.goto('/');

    await page.fill('input[name="property_state"]', 'CA');
    await page.fill('input[name="loan_amount"]', '500000');
    await page.fill('input[name="credit_score"]', '720');

    await page.click('button:has-text("Get Quotes")');

    await expect(page).toHaveURL(/\/results/);
    await expect(page.locator('text=Matching Programs')).toBeVisible();
  });
});
```

---

## 7. Configuration Files

### 7.1 tsconfig.json
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020", "dom", "dom.iterable"],
    "jsx": "preserve",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "allowJs": true,
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,
    "forceConsistentCasingInFileNames": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "skipDefaultLibCheck": true,
    "incremental": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules"]
}
```

### 7.2 .eslintrc.json
```json
{
  "extends": [
    "next/core-web-vitals",
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended"
  ],
  "rules": {
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/no-unused-vars": [
      "error",
      { "argsIgnorePattern": "^_" }
    ],
    "eqeqeq": ["error", "always"],
    "quotes": ["error", "single"],
    "semi": ["error", "always"]
  }
}
```

### 7.3 prettier.config.js
```javascript
module.exports = {
  semi: true,
  trailingComma: 'es5',
  singleQuote: true,
  printWidth: 88,
  tabWidth: 2,
  useTabs: false,
};
```

---

## 8. Import Organization

```typescript
// Standard library (none for browser)

// Third-party
import { FC, ReactNode, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

// Local types
import type { LoanProgram, QuoteRequest } from '@/types/loan';

// Local components
import { LoanProgramCard } from '@/components/LoanPrograms/LoanProgramCard';

// Local utilities
import { loanApi } from '@/lib/api';
import { formatCurrency } from '@/lib/utils';
```

---

## 9. Be Consistent

When editing existing code, match the surrounding patterns. Consistency over these guidelines when in conflict.

---

*Last Updated: 2026-01-12*
*Based on: [Google TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html)*