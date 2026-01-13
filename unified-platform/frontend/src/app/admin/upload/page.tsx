'use client';

import { useState } from 'react';
import { API_BASE } from '@/lib/api';

export default function RateSheetUploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [lenderName, setLenderName] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !lenderName) {
      setMessage({ type: 'error', text: 'Please provide both a lender name and a PDF file.' });
      return;
    }

    setLoading(true);
    setMessage(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('lender_name', lenderName);

    try {
      const response = await fetch(`${API_BASE}/api/v1/ratesheets/upload/`, {
        method: 'POST',
        body: formData, // fetch automatically sets Content-Type to multipart/form-data
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const data = await response.json();
      setMessage({ type: 'success', text: 'Rate sheet uploaded successfully!' });
      setFile(null);
      setLenderName('');
      // Reset file input manually if needed, but state reset is primary
    } catch (err) {
      setMessage({ type: 'error', text: err instanceof Error ? err.message : 'Upload failed' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-lg bg-card rounded-xl shadow-lg p-8">
        <h1 className="text-2xl font-bold text-center mb-6 text-primary">Upload Rate Sheet</h1>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium mb-2">Lender Name</label>
            <input
              type="text"
              value={lenderName}
              onChange={(e) => setLenderName(e.target.value)}
              className="w-full p-3 rounded bg-input border border-gray-700 focus:border-accent focus:ring-1 focus:ring-accent outline-none transition"
              placeholder="e.g. Acme Lending"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Rate Sheet PDF</label>
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              className="w-full p-2 rounded bg-input border border-gray-700 text-sm file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-white hover:file:bg-primary/90"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-accent text-primary font-bold rounded hover:opacity-90 transition disabled:opacity-50"
          >
            {loading ? 'Uploading...' : 'Upload Rate Sheet'}
          </button>
        </form>

        {message && (
          <div
            className={`mt-6 p-4 rounded text-center border ${
              message.type === 'success'
                ? 'bg-green-900/20 border-green-500 text-green-200'
                : 'bg-red-900/20 border-red-500 text-red-200'
            }`}
          >
            {message.text}
          </div>
        )}
      </div>
    </div>
  );
}
