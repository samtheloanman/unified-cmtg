import Link from 'next/link';

export default function NotFound() {
    return (
        <div className="min-h-screen bg-white flex flex-col">
            {/* Header */}
            <div className="bg-[#636363] text-white py-4 px-6">
                <div className="max-w-7xl mx-auto flex justify-between items-center">
                    <Link href="/" className="text-3xl font-bold tracking-wide" style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}>
                        CUSTOM MORTGAGE
                    </Link>
                </div>
            </div>

            {/* Error Content */}
            <div className="flex-1 flex items-center justify-center px-6">
                <div className="text-center">
                    <h1 className="text-9xl font-bold text-[#1daed4]" style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}>
                        404
                    </h1>
                    <h2 className="text-3xl font-bold text-[#636363] mt-4" style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}>
                        Page Not Found
                    </h2>
                    <p className="text-gray-500 mt-4 max-w-md mx-auto">
                        The page you're looking for doesn't exist or has been moved.
                        Let's get you back on track.
                    </p>
                    <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
                        <Link
                            href="/"
                            className="px-8 py-3 bg-[#1daed4] hover:bg-[#17a0c4] text-white font-bold rounded-lg transition-colors"
                            style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                        >
                            Go Home
                        </Link>
                        <Link
                            href="/quote"
                            className="px-8 py-3 border-2 border-[#636363] text-[#636363] hover:bg-gray-50 font-bold rounded-lg transition-colors"
                            style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                        >
                            Get a Quote
                        </Link>
                    </div>
                </div>
            </div>

            {/* Footer */}
            <div className="bg-[#636363] text-white py-6 px-6">
                <div className="max-w-7xl mx-auto text-center">
                    <p className="text-sm">© 2026 Custom Mortgage Inc.</p>
                </div>
            </div>
        </div>
    );
}
