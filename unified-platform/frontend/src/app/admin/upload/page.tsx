'use client';

import { useState } from 'react';
import { apiClient } from '@/lib/api-client';

export default function RateSheetUploadPage() {
  const [pdfUrl, setPdfUrl] = useState('');
  const [lenderId, setLenderId] = useState('');
  const [effectiveDate, setEffectiveDate] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [taskId, setTaskId] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!pdfUrl) {
      setMessage({ type: 'error', text: 'Please provide a PDF URL.' });
      return;
    }

    setLoading(true);
    setMessage(null);
    setTaskId(null);

    try {
      const response = await apiClient.rateSheets.upload({
        pdf_url: pdfUrl,
        lender_id: lenderId ? parseInt(lenderId) : undefined,
        effective_date: effectiveDate || undefined,
      });

      if (!response.success) {
        throw new Error(response.error.detail || response.error.error);
      }

      setMessage({
        type: 'success',
        text: `Rate sheet ingestion started! Task ID: ${response.data.task_id}`
      });
      setTaskId(response.data.task_id);
      setPdfUrl('');
      setLenderId('');
      setEffectiveDate('');
    } catch (err) {
      setMessage({
        type: 'error',
        text: err instanceof Error ? err.message : 'Upload failed'
      });
    } finally {
      setLoading(false);
    }
  };

  const checkStatus = async () => {
    if (!taskId) return;

    setLoading(true);
    try {
      const response = await apiClient.rateSheets.getTaskStatus(taskId);

      if (!response.success) {
        throw new Error(response.error.detail || response.error.error);
      }

      setMessage({
        type: response.data.status === 'failed' ? 'error' : 'success',
        text: `Status: ${response.data.status} - ${response.data.message}`
      });
    } catch (err) {
      setMessage({
        type: 'error',
        text: err instanceof Error ? err.message : 'Status check failed'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="bg-[#636363] text-white py-4 px-6">
        <div className="max-w-4xl mx-auto flex justify-between items-center">
          <h1
            className="text-3xl font-bold tracking-wide"
            style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
          >
            CUSTOM MORTGAGE - ADMIN
          </h1>
          <span
            className="text-sm tracking-widest"
            style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
          >
            RATE SHEET UPLOAD
          </span>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto py-12 px-6">
        <div className="bg-white border-2 border-[#a5a5a5] rounded-lg shadow-lg p-8">
          <div className="mb-8">
            <h2
              className="text-4xl font-bold text-[#636363] mb-2"
              style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
            >
              Upload Rate Sheet
            </h2>
            <p className="text-[#636363]">
              Trigger automated rate sheet ingestion by providing a PDF URL.
              The system will parse the document and extract pricing data.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* PDF URL Input */}
            <div>
              <label
                className="block text-sm font-semibold text-[#636363] mb-2"
                htmlFor="pdfUrl"
              >
                Rate Sheet PDF URL <span className="text-[#1daed4]">*</span>
              </label>
              <input
                id="pdfUrl"
                type="url"
                value={pdfUrl}
                onChange={(e) => setPdfUrl(e.target.value)}
                className="w-full p-3 rounded border-2 border-[#a5a5a5] focus:border-[#1daed4] focus:outline-none transition-colors text-[#636363]"
                placeholder="https://example.com/ratesheet.pdf"
                required
              />
              <p className="text-xs text-[#a5a5a5] mt-1">
                Must be a publicly accessible PDF URL
              </p>
            </div>

            {/* Lender ID Input (Optional) */}
            <div>
              <label
                className="block text-sm font-semibold text-[#636363] mb-2"
                htmlFor="lenderId"
              >
                Lender ID <span className="text-[#a5a5a5]">(Optional)</span>
              </label>
              <input
                id="lenderId"
                type="number"
                value={lenderId}
                onChange={(e) => setLenderId(e.target.value)}
                className="w-full p-3 rounded border-2 border-[#a5a5a5] focus:border-[#1daed4] focus:outline-none transition-colors text-[#636363]"
                placeholder="e.g., 1"
              />
              <p className="text-xs text-[#a5a5a5] mt-1">
                If omitted, lender will be extracted from PDF
              </p>
            </div>

            {/* Effective Date Input (Optional) */}
            <div>
              <label
                className="block text-sm font-semibold text-[#636363] mb-2"
                htmlFor="effectiveDate"
              >
                Effective Date <span className="text-[#a5a5a5]">(Optional)</span>
              </label>
              <input
                id="effectiveDate"
                type="date"
                value={effectiveDate}
                onChange={(e) => setEffectiveDate(e.target.value)}
                className="w-full p-3 rounded border-2 border-[#a5a5a5] focus:border-[#1daed4] focus:outline-none transition-colors text-[#636363]"
              />
              <p className="text-xs text-[#a5a5a5] mt-1">
                Date when these rates become effective
              </p>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-4 bg-[#1daed4] hover:bg-[#17a0c4] text-white font-bold rounded-lg transition-colors shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
              style={{ fontFamily: 'Bebas Neue, Arial, sans-serif', fontSize: '1.25rem' }}
            >
              {loading ? 'Processing...' : 'Start Ingestion'}
            </button>
          </form>

          {/* Status Message */}
          {message && (
            <div
              className={`mt-6 p-4 rounded-lg border-2 ${
                message.type === 'success'
                  ? 'bg-[#1daed4]/10 border-[#1daed4] text-[#636363]'
                  : 'bg-red-50 border-red-500 text-red-700'
              }`}
            >
              <p className="font-semibold mb-1">
                {message.type === 'success' ? '✓ Success' : '✗ Error'}
              </p>
              <p className="text-sm">{message.text}</p>
            </div>
          )}

          {/* Task Status Check */}
          {taskId && (
            <div className="mt-6 p-4 bg-gray-50 border border-[#a5a5a5] rounded-lg">
              <p className="text-sm text-[#636363] mb-3">
                <span className="font-semibold">Task ID:</span> <code className="bg-white px-2 py-1 rounded text-[#1daed4]">{taskId}</code>
              </p>
              <button
                onClick={checkStatus}
                disabled={loading}
                className="px-6 py-2 bg-white border-2 border-[#636363] hover:bg-gray-50 text-[#636363] font-semibold rounded transition-colors disabled:opacity-50"
              >
                {loading ? 'Checking...' : 'Check Status'}
              </button>
            </div>
          )}
        </div>

        {/* Info Card */}
        <div className="mt-8 bg-[#1daed4]/10 border-l-4 border-[#1daed4] p-6 rounded">
          <h3
            className="text-2xl font-bold text-[#636363] mb-3"
            style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
          >
            How It Works
          </h3>
          <ol className="space-y-2 text-[#636363]">
            <li className="flex items-start">
              <span className="font-bold text-[#1daed4] mr-2">1.</span>
              <span>Provide a URL to a publicly accessible rate sheet PDF</span>
            </li>
            <li className="flex items-start">
              <span className="font-bold text-[#1daed4] mr-2">2.</span>
              <span>Celery task downloads and parses the PDF using PdfPlumber</span>
            </li>
            <li className="flex items-start">
              <span className="font-bold text-[#1daed4] mr-2">3.</span>
              <span>Gemini AI extracts structured pricing data (rates, adjustments, terms)</span>
            </li>
            <li className="flex items-start">
              <span className="font-bold text-[#1daed4] mr-2">4.</span>
              <span>Data is saved to RateSheet and RateAdjustment models</span>
            </li>
            <li className="flex items-start">
              <span className="font-bold text-[#1daed4] mr-2">5.</span>
              <span>Pricing becomes immediately available for quote calculations</span>
            </li>
          </ol>
        </div>
      </div>

      {/* Footer */}
      <div className="bg-[#636363] text-white py-8 px-6 mt-12">
        <div className="max-w-4xl mx-auto text-center">
          <p className="text-sm">
            © 2026 Custom Mortgage Inc. | Internal Admin Tool
          </p>
        </div>
      </div>
    </div>
  );
}
