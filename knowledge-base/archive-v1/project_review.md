# Project Review: custommortgage vs cmtgdirect

## Executive Summary
**Recommendation: Keep Separate**

The two projects represent distinct architectural components (Frontend/CMS vs Backend API) using different technology stacks. Merging them would likely increase complexity without significant benefit.

## 1. Project Analysis

### A. custommortgage
*   **Type**: Content Management System & Frontend
*   **Tech Stack**: WordPress (PHP), Python (utilities), Astro (intended frontend)
*   **Primary Function**: Managing content, SEO, landing pages, and user-facing presentation.
*   **Observations**:
    *   Contains WordPress core files (`wp-content`, `wp-config.php`).
    *   Includes extensive Python scripts for content migration and analysis.
    *   **CRITICAL NOTE**: The `README.md` references a `disgingOS` directory (Active Astro frontend), but **this directory is missing from the file system** in the current checkout.

### B. cmtgdirect (Custom Mortgage Direct)
*   **Type**: Backend API & Pricing Engine
*   **Tech Stack**: Django (Python), PostgreSQL, Docker
*   **Primary Function**: Loan pricing logic, pre-qualification calculations, and lender data management.
*   **Observations**:
    *   Clean Service-Oriented Architecture (SOA).
    *   Designed as a standalone API to be consumed by other apps (like `custommortgage`).

## 2. Comparison

| Feature | custommortgage | cmtgdirect |
| :--- | :--- | :--- |
| **Language** | PHP / Python (Scripts) / JS (missing) | Python (Django) |
| **Role** | Frontend / CMS | Backend API / Logic |
| **Database** | MySQL (implied by WP) | PostgreSQL |
| **Scaling** | Caching heavy (Varnish/CDN) | CPU/Memory heavy (Calculations) |
| **Team** | Marketing / Frontend | Backend / Data Science |

## 3. Recommendation Details

### Why Keep Separate?
1.  **Separation of Concerns**: One handles *content* (text, images, pages), the other handles *logic* (math, pricing, rates). This is a best practice.
2.  **Tech Stack Mismatch**: Mixing a PHP application with a Python/Django application in a single repository (monorepo) requires complex tooling to manage dependencies and build pipelines effectively.
3.  **Deployment Independence**: You can deploy updates to the pricing engine (`cmtgdirect`) without risking downtime on the main marketing site (`custommortgage`), and vice versa.
4.  **API Contract**: `cmtgdirect` is designed as an API. `custommortgage` should treat it as an external service.

## 4. Alternative: Unified Django Backend (User Proposed)

You asked if you should merge everything into the Django backend since you are moving to Astro.

### The "Unified Backend" Strategy
In this scenario, you would **migrate all WordPress content (Posts, Pages, ACF Fields)** into Django models and use Django as your Headless CMS for Astro.

| Pros | Cons |
| :--- | :--- |
| **Single Source of Truth**: "Loan Programs" often duplicate data (Marketing text vs. Pricing logic). Merging them puts everything in one database table. | **Loss of Page Builder**: You lose Elementor/Gutenberg. Marketing teams usually struggle with the plain Django Admin interface compared to WP. |
| **Simplified Hosting**: No need for WP Engine + a separate Python host. Just one containerized Django app. | **Heavy Migration**: You must rewrite all ACF logic and fields into Django Models/Serializers. |
| **Performance**: Fetching data from local Postgres is often faster/cleaner than hitting the WP REST API. | **Reinventing Wheels**: You'll need to rebuild "Page Management", "SEO Meta Fields", "Redirects", etc., which WP gives for free. |

### The Critical Decision Factor
**Do non-technical users need to edit the website?**
*   **YES**: Keep **WordPress**. Building a visual page editor in Django is extremely difficult.
*   **NO (Devs only)**: Move to **Django**. It will be cleaner and easier to manage in the long run.

### Action Items
1.  **Locate `disgingOS`**: The `custommortgage` README suggests a modern frontend exists, but it is not currently in the folder. You should locate this code if you intend to work on the frontend.
3.  **Define Integration**: Ensure `custommortgage` (or its missing frontend) has the correct API keys and endpoints to talk to `cmtgdirect`.

## 5. Constraint Analysis: Agentic Marketing & Affiliate Workflow

You mentioned two specific goals that heavily influence this decision:
1.  **Agentic Marketing**: Using agents to create campaigns from site content.
2.  **Affiliate Program**: Using `AffiliateWP` (found in `wp-content/plugins/affiliate-wp`).

### A. The Affiliate Tool Blocker
**`AffiliateWP` is a "Big" Plugin.** It handles tracking cookies, user registration, dashboards, payouts, and integrations.
*   **If you merge to Django**: You lose this plugin. You would have to **rebuild** the entire affiliate system from scratch (Weeks/Months of work) or buy a SaaS solution (e.g., Rewardful, FirstPromoter) to replace it.
*   **Recommendation**: Unless you plan to pay for a SaaS affiliate tool ($50-$100/mo) that integrates via API, **you are stuck with WordPress** for the backend if you want to keep `AffiliateWP`.

### B. Agentic Workflow
*   **Agents don't care about the backend**: Agents consume *data*.
    *   **WordPress**: Agents can use the WP REST API to read content and `wp-cli` (as seen in your `agent_tools.py`) to write changes.
    *   **Django**: Agents would use the Django REST API.
    *   **Verdict**: While Django is cleaner for *programmers*, your existing `agent_tools.py` is already written for WordPress/WP-CLI. Migrating to Django means rewriting all these agent tools.

### Final "Merge" Recommendation
**Do NOT merge backends yet.**
*   **Reason**: The cost of replacing `AffiliateWP` + rewriting your marketing agents is too high right now.
*   **Better Path**: Keep running WordPress as a "Headless Content & Affiliate Engine". Let Astro fetch content from WP and pricing from Django.
*   **Agent Strategy**: Enhance your existing `agent_tools.py` to work with the WP API more robustly. They can still "broadcast" to SocialPilot regardless of where the data lives.

## 6. Django Alternatives & The "Subdomain Pilot" Strategy

You asked about **Django-native alternatives** to replace WordPress and proposed launching a **combined project on a subdomain (`cmre.c-mtg.com`)**.

### A. Django Alternatives to WordPress
If you commit to the "Unified Django" path, you need replacements for the WP ecosystem:
1.  **cms**: **Wagtail**. It is the gold standard for Django CMSs. It provides a "StreamField" editor that is comparable to Gutenberg/Elementor but cleaner for developers.
    *   *Verdict*: excellent replacement for WordPress core.
2.  **Affiliates**: **`django-affiliate`** or **`django-referral-system`**.
    *   *Warning*: These are **basic libraries**, not full-featured products like AffiliateWP. They handle tracking links (`?ref=123`), but you will have to **build** the UI for dashboards, payouts, and email notifications yourself.

### B. The "Subdomain Pilot" Roadmap (Recommended)
Your idea to use `cmre.c-mtg.com` is the perfect way to test this "Unified" hypothesis without breaking your main business.

**Phase 1: The "Vertical Slice" Pilot (Weeks 1-4)**
*   **Goal**: Prove Django can handle *one* full marketing flow.
*   **Setup**: Deploy the merged Django app (CustomDirect + Wagtail + Custom Affiliate Logic) to `cmre.c-mtg.com`.
*   **Content**: Migrate *5 key pages* (not all 2800).
*   **Affiliates**: Build a *minimal* referral tracker in Django (just tracking clicks -> leads).
*   **Traffic**: Send *paid traffic* or specific email campaigns to the subdomain.

**Phase 2: Evaluation**
*   Compare conversion rates and "Dev Happiness".
*   *If success*: slowly migrate all WP content to the subdomain and eventually flip the main domain.
*   *If failure* (too hard to manage content/affiliates): Kill the pilot, keep WP for marketing, and use Django just for the App.

### Final Decision Matrix
| Feature | Hybrid (WP + Django) | Unified (Django Only) |
| :--- | :--- | :--- |
| **Content Editing** | Easy (Elementor) | Medium (Wagtail) |
| **Affiliate System** | **Powerful (AffiliateWP)** | **Basic (Custom Build)** |
| **Dev Experience** | Fragmented | Clean / Monorepo |
| **Migration Risk** | Low | High |

**My advice**: Start the **Subdomain Pilot**. It allows you to start building the "Dream Architecture" (Unified Django) without killing the "Cash Cow" (WordPress + AffiliateWP) today.
