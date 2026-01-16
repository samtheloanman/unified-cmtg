# Claude Code Prompt: Phase F.7 - Next.js CMS Integration

**Track**: `finalization_20260114`  
**Phase**: F.7  
**Priority**: HIGH  
**Estimated Time**: 6-8 hours  
**Can Run Parallel With**: F.5, F.6, F.8

---

## MISSION

Integrate Next.js frontend with Wagtail headless CMS API to display program pages, local SEO pages, and blog content.

## CONTEXT

- Wagtail CMS models created in F.1 (ProgramPage, BlogPage, FundedLoanPage)
- Backend API available at `http://localhost:8001/api/v2/`
- Existing frontend at `unified-platform/frontend/`
- Need dynamic routing for programs and flat URLs for local pages

## REFERENCE FILES

- Existing components: `frontend/src/components/QuoteWizard/`
- Backend API: `backend/api/views.py`
- Design system: Uses cyan primary (`#1daed4`)

## TASKS

### 1. Create Wagtail API Client

**File**: `frontend/src/lib/wagtail-api.ts`

```typescript
const WAGTAIL_API = process.env.NEXT_PUBLIC_WAGTAIL_API || 'http://localhost:8001/api/v2';

export interface WagtailPage {
  id: number;
  meta: {
    type: string;
    slug: string;
    html_url: string;
  };
  title: string;
}

export interface ProgramPage extends WagtailPage {
  program_type: string;
  min_loan_amount: string;
  max_loan_amount: string;
  min_credit_score: number;
  interest_rate_min: number | null;
  interest_rate_max: number | null;
  max_ltv: number;
  program_description: string;
  requirements: string;
  highlights: string;
  faq: Array<{
    type: 'faq_item';
    value: {
      question: string;
      answer: string;
    };
  }>;
  available_states: string[];
}

export interface BlogPage extends WagtailPage {
  date: string;
  author: string;
  intro: string;
  body: string;
  featured_image: {
    url: string;
    alt: string;
  } | null;
}

// Fetch all pages of a type
export async function getPages<T extends WagtailPage>(
  type: string,
  params?: Record<string, string>
): Promise<T[]> {
  const searchParams = new URLSearchParams({
    type,
    fields: '*',
    ...params,
  });
  
  const response = await fetch(`${WAGTAIL_API}/pages/?${searchParams}`, {
    next: { revalidate: 60 }, // ISR: revalidate every 60 seconds
  });
  
  if (!response.ok) {
    throw new Error(`Failed to fetch pages: ${response.statusText}`);
  }
  
  const data = await response.json();
  return data.items as T[];
}

// Fetch single page by slug
export async function getPageBySlug<T extends WagtailPage>(
  slug: string,
  type?: string
): Promise<T | null> {
  const searchParams = new URLSearchParams({ slug, fields: '*' });
  if (type) searchParams.append('type', type);
  
  const response = await fetch(`${WAGTAIL_API}/pages/?${searchParams}`, {
    next: { revalidate: 60 },
  });
  
  if (!response.ok) {
    return null;
  }
  
  const data = await response.json();
  return data.items[0] as T || null;
}

// Fetch page by ID
export async function getPageById<T extends WagtailPage>(id: number): Promise<T | null> {
  const response = await fetch(`${WAGTAIL_API}/pages/${id}/?fields=*`, {
    next: { revalidate: 60 },
  });
  
  if (!response.ok) {
    return null;
  }
  
  return response.json() as Promise<T>;
}
```

### 2. Create Program Index Page

**File**: `frontend/src/app/programs/page.tsx`

```tsx
import { getPages, ProgramPage } from '@/lib/wagtail-api';
import Link from 'next/link';

export const metadata = {
  title: 'Loan Programs | Custom Mortgage',
  description: 'Explore our wide range of mortgage loan programs including DSCR, FHA, VA, and more.',
};

export default async function ProgramsPage() {
  const programs = await getPages<ProgramPage>('cms.ProgramPage');
  
  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold mb-8">Loan Programs</h1>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {programs.map((program) => (
            <Link
              key={program.id}
              href={`/programs/${program.meta.slug}`}
              className="block p-6 bg-gray-800 rounded-xl hover:bg-gray-700 transition"
            >
              <h2 className="text-xl font-bold text-cyan-400 mb-2">
                {program.title}
              </h2>
              <p className="text-gray-400 text-sm mb-4">
                {program.program_type}
              </p>
              <div className="text-sm">
                <p>Loan Range: ${Number(program.min_loan_amount).toLocaleString()} - ${Number(program.max_loan_amount).toLocaleString()}</p>
                <p>Min Credit: {program.min_credit_score}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
```

### 3. Create Program Detail Page

**File**: `frontend/src/app/programs/[slug]/page.tsx`

```tsx
import { getPageBySlug, getPages, ProgramPage } from '@/lib/wagtail-api';
import { notFound } from 'next/navigation';
import Link from 'next/link';

interface Props {
  params: { slug: string };
}

// Generate static params for all programs
export async function generateStaticParams() {
  const programs = await getPages<ProgramPage>('cms.ProgramPage');
  return programs.map((program) => ({
    slug: program.meta.slug,
  }));
}

// Generate metadata
export async function generateMetadata({ params }: Props) {
  const program = await getPageBySlug<ProgramPage>(params.slug, 'cms.ProgramPage');
  
  if (!program) {
    return { title: 'Program Not Found' };
  }
  
  return {
    title: `${program.title} | Custom Mortgage`,
    description: program.program_description?.slice(0, 160) || '',
  };
}

export default async function ProgramDetailPage({ params }: Props) {
  const program = await getPageBySlug<ProgramPage>(params.slug, 'cms.ProgramPage');
  
  if (!program) {
    notFound();
  }
  
  // Schema markup for SEO
  const schemaData = {
    '@context': 'https://schema.org',
    '@type': 'MortgageLoan',
    name: program.title,
    loanType: program.program_type,
    amount: {
      '@type': 'MonetaryAmount',
      minValue: Number(program.min_loan_amount),
      maxValue: Number(program.max_loan_amount),
      currency: 'USD',
    },
  };
  
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(schemaData) }}
      />
      
      <div className="min-h-screen bg-gray-900 text-white">
        <div className="max-w-4xl mx-auto px-4 py-12">
          {/* Breadcrumb */}
          <nav className="mb-6 text-sm">
            <Link href="/programs" className="text-cyan-400 hover:underline">
              Programs
            </Link>
            <span className="mx-2">/</span>
            <span>{program.title}</span>
          </nav>
          
          {/* Header */}
          <h1 className="text-4xl font-bold mb-4">{program.title}</h1>
          <p className="text-xl text-gray-400 mb-8">{program.program_type}</p>
          
          {/* Key Stats */}
          <div className="grid md:grid-cols-4 gap-4 mb-8">
            <div className="bg-gray-800 p-4 rounded-lg">
              <p className="text-gray-400 text-sm">Loan Amount</p>
              <p className="text-lg font-bold">
                ${Number(program.min_loan_amount).toLocaleString()} - ${Number(program.max_loan_amount).toLocaleString()}
              </p>
            </div>
            <div className="bg-gray-800 p-4 rounded-lg">
              <p className="text-gray-400 text-sm">Min Credit Score</p>
              <p className="text-lg font-bold">{program.min_credit_score}</p>
            </div>
            <div className="bg-gray-800 p-4 rounded-lg">
              <p className="text-gray-400 text-sm">Max LTV</p>
              <p className="text-lg font-bold">{program.max_ltv}%</p>
            </div>
            {program.interest_rate_min && (
              <div className="bg-gray-800 p-4 rounded-lg">
                <p className="text-gray-400 text-sm">Rate Range</p>
                <p className="text-lg font-bold">
                  {program.interest_rate_min}% - {program.interest_rate_max}%
                </p>
              </div>
            )}
          </div>
          
          {/* Description */}
          {program.program_description && (
            <section className="mb-8">
              <h2 className="text-2xl font-bold mb-4">About This Program</h2>
              <div 
                className="prose prose-invert"
                dangerouslySetInnerHTML={{ __html: program.program_description }}
              />
            </section>
          )}
          
          {/* Requirements */}
          {program.requirements && (
            <section className="mb-8">
              <h2 className="text-2xl font-bold mb-4">Requirements</h2>
              <div 
                className="prose prose-invert"
                dangerouslySetInnerHTML={{ __html: program.requirements }}
              />
            </section>
          )}
          
          {/* FAQ */}
          {program.faq && program.faq.length > 0 && (
            <section className="mb-8">
              <h2 className="text-2xl font-bold mb-4">Frequently Asked Questions</h2>
              <div className="space-y-4">
                {program.faq.map((item, index) => (
                  <details key={index} className="bg-gray-800 rounded-lg">
                    <summary className="p-4 cursor-pointer font-medium">
                      {item.value.question}
                    </summary>
                    <div 
                      className="p-4 pt-0 prose prose-invert"
                      dangerouslySetInnerHTML={{ __html: item.value.answer }}
                    />
                  </details>
                ))}
              </div>
            </section>
          )}
          
          {/* CTA */}
          <div className="bg-gradient-to-r from-cyan-600 to-blue-600 p-6 rounded-xl text-center">
            <h3 className="text-2xl font-bold mb-4">Ready to Get Started?</h3>
            <Link
              href="/quote"
              className="inline-block bg-white text-gray-900 px-8 py-3 rounded-lg font-bold hover:bg-gray-100 transition"
            >
              Get Your Quote
            </Link>
          </div>
        </div>
      </div>
    </>
  );
}
```

### 4. Create Blog Index Page

**File**: `frontend/src/app/blog/page.tsx`

```tsx
import { getPages, BlogPage } from '@/lib/wagtail-api';
import Link from 'next/link';

export const metadata = {
  title: 'Blog | Custom Mortgage',
  description: 'Mortgage news, tips, and insights from Custom Mortgage experts.',
};

export default async function BlogIndexPage() {
  const posts = await getPages<BlogPage>('cms.BlogPage');
  
  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="max-w-4xl mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold mb-8">Blog</h1>
        
        <div className="space-y-6">
          {posts.map((post) => (
            <Link
              key={post.id}
              href={`/blog/${post.meta.slug}`}
              className="block p-6 bg-gray-800 rounded-xl hover:bg-gray-700 transition"
            >
              <p className="text-sm text-gray-400 mb-2">
                {new Date(post.date).toLocaleDateString()} • {post.author}
              </p>
              <h2 className="text-xl font-bold text-cyan-400 mb-2">
                {post.title}
              </h2>
              <p className="text-gray-300">{post.intro}</p>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
```

### 5. Create Blog Detail Page

**File**: `frontend/src/app/blog/[slug]/page.tsx`

```tsx
import { getPageBySlug, getPages, BlogPage } from '@/lib/wagtail-api';
import { notFound } from 'next/navigation';
import Link from 'next/link';

interface Props {
  params: { slug: string };
}

export async function generateStaticParams() {
  const posts = await getPages<BlogPage>('cms.BlogPage');
  return posts.map((post) => ({
    slug: post.meta.slug,
  }));
}

export async function generateMetadata({ params }: Props) {
  const post = await getPageBySlug<BlogPage>(params.slug, 'cms.BlogPage');
  
  if (!post) {
    return { title: 'Post Not Found' };
  }
  
  return {
    title: `${post.title} | Custom Mortgage Blog`,
    description: post.intro,
  };
}

export default async function BlogDetailPage({ params }: Props) {
  const post = await getPageBySlug<BlogPage>(params.slug, 'cms.BlogPage');
  
  if (!post) {
    notFound();
  }
  
  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="max-w-3xl mx-auto px-4 py-12">
        <nav className="mb-6 text-sm">
          <Link href="/blog" className="text-cyan-400 hover:underline">
            Blog
          </Link>
          <span className="mx-2">/</span>
          <span>{post.title}</span>
        </nav>
        
        <article>
          <header className="mb-8">
            <h1 className="text-4xl font-bold mb-4">{post.title}</h1>
            <p className="text-gray-400">
              {new Date(post.date).toLocaleDateString()} • {post.author}
            </p>
          </header>
          
          <div 
            className="prose prose-invert prose-lg max-w-none"
            dangerouslySetInnerHTML={{ __html: post.body }}
          />
        </article>
      </div>
    </div>
  );
}
```

### 6. Update Environment Variables

**File**: `frontend/.env.local`

```
NEXT_PUBLIC_WAGTAIL_API=http://localhost:8001/api/v2
NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1
```

### 7. Test Pages

```bash
# Build to check for errors
npm run build

# Start dev server
npm run dev

# Test URLs:
# - http://localhost:3001/programs
# - http://localhost:3001/programs/[slug]
# - http://localhost:3001/blog
# - http://localhost:3001/blog/[slug]
```

## SUCCESS CRITERIA

- [ ] Wagtail API client created and working
- [ ] `/programs` shows all program pages
- [ ] `/programs/[slug]` shows individual program with all fields
- [ ] `/blog` shows all blog posts
- [ ] `/blog/[slug]` shows individual blog post
- [ ] Schema markup present in program pages
- [ ] Build passes without errors
- [ ] Lighthouse SEO score > 90

## HANDOFF

After completion, write to `conductor/handoffs/gemini/inbox.md`:
```
F.7 Complete: Next.js integrated with Wagtail CMS API.
- Programs index and detail pages working
- Blog index and detail pages working
- Schema markup implemented
- Build passing
Ready for F.9 (Testing).
```

Commit: `git commit -m "feat(frontend): F.7 Next.js Wagtail CMS integration"`
