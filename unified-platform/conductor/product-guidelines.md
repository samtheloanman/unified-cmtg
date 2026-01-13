# Product Guidelines

## 1. Core Brand Principles

Our brand identity is built on four core pillars that must be reflected in all content, design, and user interactions.

*   **Trustworthiness & Authority:** We are the definitive experts in the mortgage and real estate industry, especially for complex and unique scenarios. Our platform is backed by a proven team with decades of experience in navigating challenging transactions and adhering to the highest standards of compliance. Our tone is confident, knowledgeable, and reassuring, reflecting our deep understanding of the regulatory landscape.
*   **Client-Centric Care:** "We are different because we care." The user experience should feel supportive and empowering. We provide proactive solutions and clear guidance, translating complex situations into manageable steps. The platform is not just a tool; it's a partner dedicated to helping clients achieve their goals with confidence.
*   **Innovation & Technology:** We are a "FinTech" company at our core. The platform should feel modern, intelligent, and efficient. We leverage AI and technology not as a gimmick, but to provide a genuinely smarter, more streamlined, and transparent mortgage process, particularly in managing intricate details like rate adjustments and compliance.
*   **Simplicity & User-Friendliness:** Despite the inherent complexity of the mortgage world and the challenging transactions we specialize in, our platform must be intuitive and easy to navigate. We translate convoluted processes into simple, guided steps for the user, removing ambiguity and stress, and ensuring clarity in all communications.

## 2. Brand Messaging & Tone

*   **Primary Message:** "Custom Mortgage (operating brand of Custom MTG Inc) is a nationwide FinTech real estate and finance agency that provides tailored, precise financing solutions for every unique need. Our expert, client-focused team is dedicated to guiding you through even the most challenging transactions with care, confidence, and strict adherence to compliance. Our strategic focus is on CMRE (Custom Mortgage and Real Estate) to unify our offerings."
*   **Tone:** The tone should be a blend of **authoritative expertise, reassuring guidance, and meticulous precision.** We are the calm, expert guide through a difficult process, always emphasizing our ability to find solutions where others cannot.

## 3. Key Value Propositions to Emphasize

*   **Expertise-Driven:** "A proven team of loan professionals," "Specializing in unique mortgage requirements," "Experts in tough transactions," "Deep understanding of compliance."
*   **Caring Approach:** "We are different because we care," "Guidance every step of the way," "Proactive problem-solving."
*   **Technology-Powered:** "FinTech Financing Solutions," "Streamline your transactions with modern technology," "Precise rate management."
*   **Compliance & Reliability:** "Adhering to the highest standards of compliance," "Accurate and transparent terms."
*   **Personalization:** "Tailored for your unique needs."

## 4. Visual & UI/UX Guidelines

### 4.1 Core Philosophy
The new frontend will be a high-fidelity evolution of the existing production site, improving upon it while maintaining brand consistency. Key content will be prioritized "above the fold" to ensure critical information and calls-to-action are immediately visible. The overall aesthetic must remain clean, uncluttered, and professional, reflecting our expertise.

### 4.2 Logo Usage
The primary logo is a text-based design, representing our operating brand. Future iterations will incorporate the CMRE acronym.
*   **Operating Brand Logo:** `CUSTOM MORTGAGE`
*   **Font:** `Bebas Neue Bold`
*   **Tagline:** `NATIONWIDE LENDER` or `CUSTOM MORTGAGE + REAL ESTATE`
*   **Tagline Font:** `Bebas Neue` (with a wide kerning of `200`)

### 4.3 Typography
*   **Primary Heading Font:** `Bebas Neue Bold` should be used for all major headings (H1, H2) to maintain a strong, authoritative feel.
*   **Secondary/Book Font:** `Bebas Neue Book` should be used for subheadings and body copy where appropriate to provide a clean, readable experience.
*   **Body Text:** A standard, highly-readable sans-serif font (like Lato, Open Sans, or Roboto, which are often paired with Bebas Neue) should be used for paragraphs and long-form text to ensure legibility.

### 4.4 Color Palette
*   **Primary Accent (Cyan):** `#1daed4` - Used for calls-to-action, links, and key highlights.
*   **Primary Text & Dark Elements:** `#636363` - A dark gray used for main headings and body text for a softer feel than pure black.
*   **Borders & Light Gray Elements:** `#a5a5a5` - Used for borders, secondary text, and disabled states.
*   **Background:** A clean white (`#FFFFFF`) or very light off-white should be the primary background to keep the design feeling open and uncluttered.

### 4.5 Layout & Structure
The layout should follow the established structure of the production site. This includes:
*   **Header:** A clear top bar with primary actions (`Apply Now`, `Sign In`) and a main navigation bar with dropdowns.
*   **Hero Section:** A prominent section at the top of key pages with a strong headline and a clear call-to-action.
*   **Card-Based Sections:** Use a grid or card layout for featured services (e.g., Loan Programs) to present information in a structured, digestible format. Each card should have a clear title, brief description, and actions.
*   **Dynamic Content:** Testimonials and "Recently Funded" sections should be displayed clearly, potentially in carousels or filterable lists.
*   **Footer:** A comprehensive footer containing quick links, contact information, and social media links is required.
Existing pages (e.g., program pages like `/nonqm-stated-no-doc-income-mortgage-loans/`) will serve as initial templates for iterative improvement.

### 4.6 Animation
The platform should feel dynamic and modern. The use of animations, such as **Lottie files**, is encouraged to enhance the user experience, particularly for loading states, success confirmations, or to draw attention to key features. Animations should be smooth and professional, not distracting.

### 4.7 UI/UX Principles
*   Clarity over clutter.
*   Guided user journeys.
*   Accessibility (WCAG 2.1 AA standard).
*   Consistency across the platform.

## 5. SEO & AI Content Strategy

### 5.1 SEO-First Design & Structure
SEO is a foundational requirement, not an afterthought. The platform's architecture and design must be built for search visibility from day one.
*   **URL Structure:** URLs must be clean, semantic, and follow the existing successful patterns (e.g., `/nonqm-stated-no-doc-income-mortgage-loans/`).
*   **Mobile-First Indexing:** The design must be fully responsive and optimized for mobile devices.
*   **Core Web Vitals:** The frontend architecture must be optimized for fast loading times (LCP), interactivity (FID/INP), and visual stability (CLS).

### 5.2 Comprehensive Schema Markup
All content entities across the site must be marked up with the appropriate `Schema.org` vocabulary to provide explicit context to search engines and AI models.
*   **Loan Programs:** Use `LoanProduct` schema, detailing rates, terms, and eligibility.
*   **Articles & Guides:** Use `Article` or `BlogPosting` schema.
*   **Reviews & Testimonials:** Use `Review` schema.
*   **Company Info:** Use `Organization` and `LocalBusiness` schema.
*   **Q&A Content:** Use `FAQPage` schema to directly address common user questions.

### 5.3 Content Strategy for AI Consumption
Our goal is for AI search engines (like Google's AI Overviews) to use our content as a primary source for answers and to refer clients to us. Content must be structured accordingly.
*   **Answer-Focused Content:** Pages should be structured to directly answer specific questions (e.g., "What is a Non-QM loan?"). Start pages with a concise, factual summary that an AI can easily extract.
*   **Structured Data:** Use lists, tables, and clear headings (`<h2>`, `<h3>`) to break down complex information into digestible chunks that are easy for AI models to parse.
*   **E-E-A-T Signals:** Emphasize **Experience, Expertise, Authoritativeness, and Trustworthiness**. Author bios, case studies ("Recently Funded"), and clear sourcing for data are critical. This reinforces why our content is a reliable source for AI models.
*   **Clear Calls-to-Action:** Every piece of "answer" content should be followed by a logical next step or call-to-action, guiding the user (and the AI) toward a conversion.
