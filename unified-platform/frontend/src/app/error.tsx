'use client';

import { useEffect } from 'react';
import Link from 'next/link';

export default function Error({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    useEffect(() => {
        // Log error to monitoring service (e.g., Sentry)
        console.error('Application Error:', error);
    }, [error]);

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
                    <div className="w-24 h-24 mx-auto mb-6 bg-red-100 rounded-full flex items-center justify-center">
                        <svg className="w-12 h-12 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                    </div>
                    <h1 className="text-4xl font-bold text-[#636363]" style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}>
                        Something Went Wrong
                    </h1>
                    <p className="text-gray-500 mt-4 max-w-md mx-auto">
                        We encountered an unexpected error. Our team has been notified.
                        Please try again or contact support if the problem persists.
                    </p>
                    {error.digest && (
                        <p className="text-xs text-gray-400 mt-2">
                            Error ID: {error.digest}
                        </p>
                    )}
                    <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
                        <button
                            onClick={reset}
                            className="px-8 py-3 bg-[#1daed4] hover:bg-[#17a0c4] text-white font-bold rounded-lg transition-colors"
                            style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                        >
                            Try Again
                        </button>
                        <Link
                            href="/"
                            className="px-8 py-3 border-2 border-[#636363] text-[#636363] hover:bg-gray-50 font-bold rounded-lg transition-colors"
                            style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                        >
                            Go Home
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
