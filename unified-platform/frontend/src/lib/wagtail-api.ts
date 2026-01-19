/**
 * Wagtail CMS API Client
 *
 * Type-safe client for fetching pages and content from Wagtail headless CMS API.
 * Uses ISR (Incremental Static Regeneration) with 60-second revalidation.
 */

const WAGTAIL_API = process.env.NEXT_PUBLIC_WAGTAIL_API || 'http://localhost:8001/api/v2';

// =============================================================================
// BASE TYPES
// =============================================================================

export interface WagtailPageMeta {
  type: string;
  detail_url: string;
  html_url: string;
  slug: string;
  first_published_at: string | null;
  parent: { id: number; meta: { type: string; detail_url: string } } | null;
}

export interface WagtailPage {
  id: number;
  meta: WagtailPageMeta;
  title: string;
}

export interface WagtailImage {
  id: number;
  meta: {
    type: string;
    detail_url: string;
    download_url: string;
  };
  title: string;
}

// =============================================================================
// PROGRAM PAGE
// =============================================================================

export interface CMSProgramPage extends WagtailPage {
  // === PROGRAM INFO TAB ===
  program_type: 'residential' | 'commercial' | 'hard_money' | 'nonqm' | 'reverse_mortgage';
  linked_program_type: number | null;
  available_states: string[];
  minimum_loan_amount: string | null;
  maximum_loan_amount: string | null;
  min_credit_score: number | null;

  // === PROGRAM DETAILS TAB (Rich Content) ===
  mortgage_program_highlights: string;
  what_are: string;
  details_about_mortgage_loan_program: string;
  benefits_of: string;
  requirements: string;
  how_to_qualify_for: string;
  why_us: string;
  faq: { type: 'faq_item'; value: { question: string; answer: string } }[];

  // === FINANCIAL TERMS TAB ===
  interest_rates: string;
  max_ltv: string;
  max_debt_to_income_ratio: number | null;
  min_dscr: number | null;

  // === PROPERTY & LOAN TAB ===
  property_types: string[];
  occupancy_types: string[];
  lien_position: string[];
  amortization_terms: string[];
  purpose_of_mortgage: string[];
  refinance_types: string[];
  income_documentation_type: string[];
  prepayment_penalty: string;

  // === BORROWER DETAILS TAB ===
  borrower_types: string[];
  citizenship_requirements: string[];
  credit_events_allowed: string[];
  mortgage_lates_allowed: string[];

  // === LOCATION TAB ===
  is_local_variation: boolean;
  target_city: string;
  target_state: string;
  target_region: string;

  // === META ===
  featured_image: WagtailImage | null;
  schema_markup: Record<string, unknown> | null;
  source_url: string;
}

// =============================================================================
// FUNDED LOAN PAGE (Case Studies)
// =============================================================================

export interface FundedLoanPage extends WagtailPage {
  loan_amount: string | null;
  loan_type: string;
  property_type: string;
  location: string;
  close_date: string | null;
  description: string;
  source_url: string;
}

// =============================================================================
// BLOG PAGE (for future implementation)
// =============================================================================

export interface BlogPage extends WagtailPage {
  date: string;
  author: string;
  intro: string;
  body: string;
  featured_image: WagtailImage | null;
}

// =============================================================================
// HOME PAGE
// =============================================================================

export interface HomePage extends WagtailPage {
  hero_title: string;
  hero_subtitle: string;
  hero_cta_text: string;
  hero_cta_url: string;
}

// =============================================================================
// API RESPONSE TYPES
// =============================================================================

export interface WagtailPagesResponse<T extends WagtailPage> {
  meta: {
    total_count: number;
  };
  items: T[];
}

// =============================================================================
// API CLIENT FUNCTIONS
// =============================================================================

/**
 * Fetch pages from Wagtail API with optional filtering
 */
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
    console.error(`Failed to fetch pages: ${response.status} ${response.statusText}`);
    return [];
  }

  const data: WagtailPagesResponse<T> = await response.json();
  return data.items;
}

/**
 * Fetch a single page by slug
 */
export async function getPageBySlug<T extends WagtailPage>(
  slug: string,
  type?: string
): Promise<T | null> {
  const searchParams = new URLSearchParams({ slug, fields: '*' });
  if (type) {
    searchParams.append('type', type);
  }

  const response = await fetch(`${WAGTAIL_API}/pages/?${searchParams}`, {
    next: { revalidate: 60 },
  });

  if (!response.ok) {
    console.error(`Failed to fetch page by slug: ${response.status}`);
    return null;
  }

  const data: WagtailPagesResponse<T> = await response.json();
  return data.items[0] ?? null;
}

/**
 * Fetch a single page by ID
 */
export async function getPageById<T extends WagtailPage>(id: number): Promise<T | null> {
  const response = await fetch(`${WAGTAIL_API}/pages/${id}/?fields=*`, {
    next: { revalidate: 60 },
  });

  if (!response.ok) {
    console.error(`Failed to fetch page by ID: ${response.status}`);
    return null;
  }

  return response.json() as Promise<T>;
}

/**
 * Get the home page
 */
export async function getHomePage(): Promise<HomePage | null> {
  const pages = await getPages<HomePage>('cms.HomePage');
  return pages[0] ?? null;
}

/**
 * Get all program pages
 */
export async function getProgramPages(): Promise<CMSProgramPage[]> {
  return getPages<CMSProgramPage>('cms.ProgramPage');
}

/**
 * Get program page by slug
 */
export async function getProgramBySlug(slug: string): Promise<CMSProgramPage | null> {
  return getPageBySlug<CMSProgramPage>(slug, 'cms.ProgramPage');
}

/**
 * Get all funded loan pages (case studies)
 */
export async function getFundedLoanPages(): Promise<FundedLoanPage[]> {
  return getPages<FundedLoanPage>('cms.FundedLoanPage');
}

/**
 * Get funded loan page by slug
 */
export async function getFundedLoanBySlug(slug: string): Promise<FundedLoanPage | null> {
  return getPageBySlug<FundedLoanPage>(slug, 'cms.FundedLoanPage');
}

/**
 * Get all blog posts
 * Note: BlogPage model needs to be created in Wagtail backend
 */
export async function getBlogPages(): Promise<BlogPage[]> {
  return getPages<BlogPage>('cms.BlogPage');
}

/**
 * Get blog post by slug
 */
export async function getBlogBySlug(slug: string): Promise<BlogPage | null> {
  return getPageBySlug<BlogPage>(slug, 'cms.BlogPage');
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Format program type for display
 */
export function formatProgramType(type: string): string {
  const typeMap: Record<string, string> = {
    residential: 'Residential',
    commercial: 'Commercial',
    hard_money: 'Hard Money',
    nonqm: 'Non-QM',
    reverse_mortgage: 'Reverse Mortgage',
  };
  return typeMap[type] || type;
}

/**
 * Format currency string for display
 */
export function formatLoanAmount(amount: string | null): string {
  if (!amount) return 'N/A';
  const num = parseFloat(amount);
  if (isNaN(num)) return amount;
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(num);
}
