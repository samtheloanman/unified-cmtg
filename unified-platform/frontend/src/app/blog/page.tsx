import { getBlogPages, BlogPage } from '@/lib/wagtail-api';
import Link from 'next/link';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Blog | Custom Mortgage',
  description:
    'Mortgage news, tips, and insights from Custom Mortgage experts. Stay informed about the latest trends in home financing.',
  openGraph: {
    title: 'Blog | Custom Mortgage',
    description:
      'Mortgage news, tips, and insights from Custom Mortgage experts. Stay informed about the latest trends in home financing.',
    type: 'website',
  },
};

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
 * Strip HTML tags from intro text
 */
function stripHtml(html: string): string {
  return html.replace(/<[^>]*>/g, '').trim();
}

export default async function BlogIndexPage() {
  const posts = await getBlogPages();

  return (
    <div className="bg-white">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-gray-50 to-white py-12 px-6 border-b-4 border-[#1daed4]">
        <div className="max-w-7xl mx-auto">
          <h1
            className="text-5xl font-bold text-[#636363] mb-4"
            style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
          >
            Blog
          </h1>
          <p className="text-lg text-[#636363] max-w-2xl">
            Expert insights, mortgage tips, and industry news from the Custom Mortgage team.
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto py-12 px-6">
        {posts.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-[#636363] text-lg">No blog posts available at this time.</p>
            <p className="text-[#a5a5a5] mt-2">Check back soon for new content.</p>
          </div>
        ) : (
          <div className="space-y-8">
            {posts.map((post) => (
              <article
                key={post.id}
                className="border-2 border-gray-200 rounded-xl overflow-hidden hover:border-[#1daed4] transition-colors group"
              >
                <Link href={`/blog/${post.meta.slug}`} className="block">
                  <div className="p-6">
                    {/* Meta */}
                    <div className="flex items-center gap-4 text-sm text-[#a5a5a5] mb-3">
                      <time dateTime={post.date}>{formatDate(post.date)}</time>
                      {post.author && (
                        <>
                          <span>•</span>
                          <span>{post.author}</span>
                        </>
                      )}
                    </div>

                    {/* Title */}
                    <h3
                      className="text-2xl font-bold text-[#636363] group-hover:text-[#1daed4] transition-colors mb-3"
                      style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                    >
                      {post.title}
                    </h3>

                    {/* Intro */}
                    {post.intro && (
                      <p className="text-[#636363] leading-relaxed">{stripHtml(post.intro)}</p>
                    )}

                    {/* Read More */}
                    <div className="mt-4">
                      <span className="text-[#1daed4] font-semibold group-hover:underline">
                        Read More →
                      </span>
                    </div>
                  </div>
                </Link>
              </article>
            ))}
          </div>
        )}
      </div>

      {/* CTA Section */}
      <div className="bg-[#1daed4] py-12 px-6">
        <div className="max-w-4xl mx-auto text-center text-white">
          <h3
            className="text-4xl font-bold mb-4"
            style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
          >
            Ready to Get Started?
          </h3>
          <p className="text-lg mb-8 text-white/90">
            Get a personalized mortgage quote in minutes.
          </p>
          <Link
            href="/quote"
            className="inline-block bg-white text-[#636363] px-8 py-4 rounded-lg font-bold text-lg hover:bg-gray-100 transition-colors shadow-lg"
            style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
          >
            Get Your Quote
          </Link>
        </div>
      </div>
    </div>
  );
}
