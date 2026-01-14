'use client';

import { useState } from 'react';

interface Step2Props {
    value: number;
    onChange: (value: number) => void;
    onNext: () => void;
    onBack: () => void;
}

const formatCurrency = (num: number): string => {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }).format(num);
};

const parseCurrency = (str: string): number => {
    return Number(str.replace(/[^0-9.-]+/g, '')) || 0;
};

export default function Step2LoanAmount({ value, onChange, onNext, onBack }: Step2Props) {
    const [displayValue, setDisplayValue] = useState(value ? formatCurrency(value) : '');
    const [error, setError] = useState('');

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const rawValue = e.target.value;
        const numValue = parseCurrency(rawValue);
        setDisplayValue(rawValue);
        onChange(numValue);
        if (error) setError('');
    };

    const handleBlur = () => {
        if (value) {
            setDisplayValue(formatCurrency(value));
        }
    };

    const handleFocus = () => {
        if (value) {
            setDisplayValue(value.toString());
        }
    };

    const handleNext = () => {
        if (!value || value < 50000) {
            setError('Minimum loan amount is $50,000');
            return;
        }
        if (value > 50000000) {
            setError('Maximum loan amount is $50,000,000');
            return;
        }
        setError('');
        onNext();
    };

    return (
        <div>
            <h3 className="text-3xl font-bold text-[#636363] mb-2" style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}>
                Loan Amount
            </h3>
            <p className="text-[#636363] mb-6">How much are you looking to borrow?</p>

            <div className="mb-6">
                <label className="block text-sm font-semibold text-[#636363] mb-2">
                    Desired Loan Amount *
                </label>
                <div className="relative">
                    <span className="absolute left-4 top-1/2 -translate-y-1/2 text-[#636363] text-lg">$</span>
                    <input
                        type="text"
                        value={displayValue}
                        onChange={handleChange}
                        onBlur={handleBlur}
                        onFocus={handleFocus}
                        placeholder="500,000"
                        className={`
              w-full p-4 pl-8 border-2 rounded-lg text-lg
              focus:outline-none focus:border-[#1daed4]
              ${error ? 'border-red-500' : 'border-[#a5a5a5]'}
            `}
                    />
                </div>
                {error && <p className="mt-2 text-sm text-red-500">{error}</p>}
                <p className="mt-2 text-xs text-[#a5a5a5]">Min: $50,000 | Max: $50,000,000</p>
            </div>

            <div className="flex gap-4">
                <button
                    onClick={onBack}
                    className="flex-1 py-4 bg-white border-2 border-[#a5a5a5] hover:border-[#636363] text-[#636363] font-bold rounded-lg transition-colors text-lg"
                    style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                >
                    Back
                </button>
                <button
                    onClick={handleNext}
                    className="flex-1 py-4 bg-[#1daed4] hover:bg-[#17a0c4] text-white font-bold rounded-lg transition-colors text-lg shadow-md hover:shadow-lg"
                    style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                >
                    Continue
                </button>
            </div>
        </div>
    );
}
