import { getBlogPages, getBlogBySlug, BlogPage } from '@/lib/wagtail-api';
import { notFound } from 'next/navigation';
import Link from 'next/link';
import { Metadata } from 'next';

interface Props {
  params: Promise<{ slug: string }>;
}

/**
 * Generate static paths for all blog posts at build time
 */
export async function generateStaticParams() {
  const posts = await getBlogPages();
  return posts.map((post) => ({
    slug: post.meta.slug,
  }));
}

/**
 * Generate metadata for SEO
 */
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const post = await getBlogBySlug(slug);

  if (!post) {
    return { title: 'Post Not Found | Custom Mortgage' };
  }

  const description =
    post.intro?.replace(/<[^>]*>/g, '').slice(0, 160) ||
    `Read ${post.title} on the Custom Mortgage blog.`;

  return {
    title: `${post.title} | Custom Mortgage Blog`,
    description,
    openGraph: {
      title: `${post.title} | Custom Mortgage Blog`,
      description,
      type: 'article',
      publishedTime: post.date,
      authors: post.author ? [post.author] : undefined,
    },
  };
}

/**
 * Format date for display
 */
function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

/**
 * Generate BlogPosting schema markup for SEO
 */
function generateSchemaMarkup(post: BlogPage) {
  return {
    '@context': 'https://schema.org',
    '@type': 'BlogPosting',
    headline: post.title,
    datePublished: post.date,
    author: post.author
      ? {
          '@type': 'Person',
          name: post.author,
        }
      : undefined,
    publisher: {
      '@type': 'Organization',
      name: 'Custom Mortgage Inc.',
      url: 'https://custommortgageinc.com',
    },
    description: post.intro?.replace(/<[^>]*>/g, '').slice(0, 160),
  };
}

export default async function BlogDetailPage({ params }: Props) {
  const { slug } = await params;
  const post = await getBlogBySlug(slug);

  if (!post) {
    notFound();
  }

  const schemaMarkup = generateSchemaMarkup(post);

  return (
    <>
      {/* Schema Markup for SEO */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(schemaMarkup) }}
      />

      <div className="min-h-screen bg-white">
        {/* Header */}
        <div className="bg-[#636363] text-white py-4 px-6">
          <div className="max-w-7xl mx-auto flex justify-between items-center">
            <Link href="/">
              <h1
                className="text-3xl font-bold tracking-wide"
                style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
              >
                CUSTOM MORTGAGE
              </h1>
            </Link>
            <span
              className="text-sm tracking-widest"
              style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
            >
              NATIONWIDE LENDER
            </span>
          </div>
        </div>

        {/* Breadcrumb */}
        <div className="bg-gray-50 border-b border-gray-200 py-3 px-6">
          <div className="max-w-3xl mx-auto">
            <nav className="text-sm">
              <Link href="/" className="text-[#1daed4] hover:underline">
                Home
              </Link>
              <span className="mx-2 text-gray-400">/</span>
              <Link href="/blog" className="text-[#1daed4] hover:underline">
                Blog
              </Link>
              <span className="mx-2 text-gray-400">/</span>
              <span className="text-[#636363]">{post.title}</span>
            </nav>
          </div>
        </div>

        {/* Article */}
        <article className="max-w-3xl mx-auto py-12 px-6">
          {/* Header */}
          <header className="mb-8">
            <h1
              className="text-4xl md:text-5xl font-bold text-[#636363] mb-4"
              style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
            >
              {post.title}
            </h1>
            <div className="flex items-center gap-4 text-[#a5a5a5]">
              <time dateTime={post.date}>{formatDate(post.date)}</time>
              {post.author && (
                <>
                  <span>•</span>
                  <span>By {post.author}</span>
                </>
              )}
            </div>
          </header>

          {/* Featured Image */}
          {post.featured_image && (
            <div className="mb-8">
              <img
                src={post.featured_image.meta.download_url}
                alt={post.featured_image.title || post.title}
                className="w-full rounded-xl"
              />
            </div>
          )}

          {/* Intro */}
          {post.intro && (
            <div
              className="text-xl text-[#636363] leading-relaxed mb-8 font-medium"
              dangerouslySetInnerHTML={{ __html: post.intro }}
            />
          )}

          {/* Body */}
          {post.body && (
            <div
              className="prose prose-lg max-w-none prose-headings:text-[#636363] prose-headings:font-bold prose-p:text-[#636363] prose-li:text-[#636363] prose-a:text-[#1daed4] prose-a:no-underline hover:prose-a:underline prose-blockquote:border-[#1daed4] prose-blockquote:text-[#636363]"
              dangerouslySetInnerHTML={{ __html: post.body }}
            />
          )}

          {/* Share / CTA */}
          <div className="mt-12 pt-8 border-t-2 border-gray-200">
            <div className="bg-gray-50 rounded-xl p-6">
              <h3
                className="text-2xl font-bold text-[#636363] mb-4"
                style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
              >
                Ready to Get Started?
              </h3>
              <p className="text-[#636363] mb-6">
                Get a personalized mortgage quote from our expert team.
              </p>
              <Link
                href="/quote"
                className="inline-block bg-[#1daed4] text-white px-6 py-3 rounded-lg font-bold hover:bg-[#17a0c4] transition-colors"
                style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
              >
                Get Your Quote
              </Link>
            </div>
          </div>
        </article>

        {/* Back to Blog */}
        <div className="max-w-3xl mx-auto px-6 pb-12">
          <Link
            href="/blog"
            className="inline-flex items-center text-[#1daed4] font-semibold hover:underline"
          >
            ← Back to Blog
          </Link>
        </div>

        {/* Footer */}
        <div className="bg-[#636363] text-white py-8 px-6">
          <div className="max-w-7xl mx-auto text-center">
            <p className="text-sm">
              © {new Date().getFullYear()} Custom Mortgage Inc. | Nationwide Lender | FinTech
              Financing Solutions
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
