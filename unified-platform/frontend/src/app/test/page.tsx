import React from 'react';

export default async function TestPage() {
    // Server-side fetch from within the Docker container
    // accessing the backend service directly
    const apiUrl = 'http://backend:8000/api/v1/health/';
    let status = 'Unknown';
    let error = null;
    let rawData = null;

    try {
        console.log(`Fetching from ${apiUrl}...`);
        const res = await fetch(apiUrl, { cache: 'no-store' });

        if (!res.ok) {
            throw new Error(`HTTP Error: ${res.status} ${res.statusText}`);
        }

        const data = await res.json();
        rawData = JSON.stringify(data, null, 2);
        status = data.status === 'ok' ? '✅ SUCCESS' : '⚠️ UNEXPECTED RESPONSE';
    } catch (e: any) {
        console.error('Fetch error:', e);
        status = '❌ FAILED';
        error = e.message || String(e);
    }

    return (
        <div className="p-10 max-w-2xl mx-auto font-sans">
            <h1 className="text-3xl font-bold mb-6 text-gray-800">Unified Platform Connectivity Test</h1>

            <div className={`p-6 rounded-lg border-2 ${error ? 'border-red-300 bg-red-50' : 'border-green-300 bg-green-50'}`}>
                <div className="flex items-center justify-between mb-4">
                    <span className="font-semibold text-lg">Backend Connection</span>
                    <span className={`px-3 py-1 rounded-full text-sm font-bold ${error ? 'bg-red-200 text-red-800' : 'bg-green-200 text-green-800'}`}>
                        {status}
                    </span>
                </div>

                <div className="space-y-2 text-sm">
                    <p><span className="font-semibold">Source:</span> Next.js Server (Container)</p>
                    <p><span className="font-semibold">Target:</span> <code>{apiUrl}</code></p>
                </div>

                {error && (
                    <div className="mt-4 p-3 bg-white rounded border border-red-200">
                        <p className="font-mono text-red-600 text-xs break-all">{error}</p>
                    </div>
                )}

                {rawData && (
                    <div className="mt-4">
                        <p className="text-xs text-gray-500 mb-1">Response Data:</p>
                        <pre className="bg-white p-3 rounded border border-gray-200 overflow-auto text-xs font-mono">
                            {rawData}
                        </pre>
                    </div>
                )}
            </div>

            <div className="mt-8 text-sm text-gray-500">
                <p>This page tests the internal Docker network connectivity between the frontend container and the backend container.</p>
                <p>If this fails, ensure both services are on the same network and the backend is running on port 8000.</p>
            </div>
        </div>
    );
}
