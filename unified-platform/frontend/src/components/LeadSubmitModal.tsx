'use client';

import { useState } from 'react';
import { apiClient, type Quote } from '@/lib/api-client';

interface LeadSubmitModalProps {
    selectedQuote: Quote;
    isOpen: boolean;
    onClose: () => void;
    onSuccess: () => void;
}

export default function LeadSubmitModal({
    selectedQuote,
    isOpen,
    onClose,
    onSuccess,
}: LeadSubmitModalProps) {
    const [formData, setFormData] = useState({
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            const response = await apiClient.leads.submitLead({
                first_name: formData.first_name,
                last_name: formData.last_name,
                email: formData.email,
                phone: formData.phone,
                loan_amount: selectedQuote.min_loan,
                selected_program: selectedQuote.program,
                selected_lender: selectedQuote.lender,
            });

            if (!response.success) {
                throw new Error(response.error?.detail || response.error?.error || 'Failed to submit application');
            }

            onSuccess();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-2xl max-w-md w-full max-h-[90vh] overflow-y-auto">
                {/* Header */}
                <div className="bg-[#636363] text-white px-6 py-4 flex justify-between items-center">
                    <h2
                        className="text-2xl font-bold"
                        style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                    >
                        Apply Now
                    </h2>
                    <button
                        onClick={onClose}
                        className="text-white/80 hover:text-white text-2xl leading-none"
                        aria-label="Close"
                    >
                        ×
                    </button>
                </div>

                {/* Body */}
                <div className="p-6">
                    {/* Selected Program Info */}
                    <div className="bg-[#1daed4]/10 border border-[#1daed4] rounded-lg p-4 mb-6">
                        <p className="text-sm text-[#636363] mb-1">Selected Program:</p>
                        <p className="font-bold text-[#636363]">{selectedQuote.lender}</p>
                        <p className="text-sm text-[#636363]">{selectedQuote.program}</p>
                        <p className="text-2xl font-bold text-[#1daed4] mt-2">
                            {selectedQuote.base_rate}%
                        </p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-4">
                        {/* First Name */}
                        <div>
                            <label
                                htmlFor="first_name"
                                className="block text-sm font-semibold text-[#636363] mb-2"
                            >
                                First Name <span className="text-[#1daed4]">*</span>
                            </label>
                            <input
                                id="first_name"
                                type="text"
                                required
                                value={formData.first_name}
                                onChange={(e) =>
                                    setFormData({ ...formData, first_name: e.target.value })
                                }
                                className="w-full p-3 border-2 border-[#a5a5a5] rounded focus:border-[#1daed4] focus:outline-none text-[#636363]"
                                placeholder="John"
                            />
                        </div>

                        {/* Last Name */}
                        <div>
                            <label
                                htmlFor="last_name"
                                className="block text-sm font-semibold text-[#636363] mb-2"
                            >
                                Last Name <span className="text-[#1daed4]">*</span>
                            </label>
                            <input
                                id="last_name"
                                type="text"
                                required
                                value={formData.last_name}
                                onChange={(e) =>
                                    setFormData({ ...formData, last_name: e.target.value })
                                }
                                className="w-full p-3 border-2 border-[#a5a5a5] rounded focus:border-[#1daed4] focus:outline-none text-[#636363]"
                                placeholder="Doe"
                            />
                        </div>

                        {/* Email */}
                        <div>
                            <label
                                htmlFor="email"
                                className="block text-sm font-semibold text-[#636363] mb-2"
                            >
                                Email <span className="text-[#1daed4]">*</span>
                            </label>
                            <input
                                id="email"
                                type="email"
                                required
                                value={formData.email}
                                onChange={(e) =>
                                    setFormData({ ...formData, email: e.target.value })
                                }
                                className="w-full p-3 border-2 border-[#a5a5a5] rounded focus:border-[#1daed4] focus:outline-none text-[#636363]"
                                placeholder="john@example.com"
                            />
                            <p className="text-xs text-[#a5a5a5] mt-1">
                                We&apos;ll send your application link to this email
                            </p>
                        </div>

                        {/* Phone */}
                        <div>
                            <label
                                htmlFor="phone"
                                className="block text-sm font-semibold text-[#636363] mb-2"
                            >
                                Phone <span className="text-[#a5a5a5]">(Optional)</span>
                            </label>
                            <input
                                id="phone"
                                type="tel"
                                value={formData.phone}
                                onChange={(e) =>
                                    setFormData({ ...formData, phone: e.target.value })
                                }
                                className="w-full p-3 border-2 border-[#a5a5a5] rounded focus:border-[#1daed4] focus:outline-none text-[#636363]"
                                placeholder="(555) 123-4567"
                            />
                        </div>

                        {/* Error Message */}
                        {error && (
                            <div className="bg-red-50 border-2 border-red-500 rounded-lg p-4 text-red-700">
                                <p className="font-semibold">Error</p>
                                <p className="text-sm">{error}</p>
                            </div>
                        )}

                        {/* Submit Button */}
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full py-4 bg-[#1daed4] hover:bg-[#17a0c4] text-white font-bold rounded-lg transition-colors shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
                            style={{
                                fontFamily: 'Bebas Neue, Arial, sans-serif',
                                fontSize: '1.25rem',
                            }}
                        >
                            {loading ? 'Submitting...' : 'Start Your Application'}
                        </button>

                        <p className="text-xs text-center text-[#a5a5a5]">
                            By clicking &quot;Start Your Application&quot; you agree to receive email
                            communication from Custom Mortgage Inc.
                        </p>
                    </form>
                </div>
            </div>
        </div>
    );
}
