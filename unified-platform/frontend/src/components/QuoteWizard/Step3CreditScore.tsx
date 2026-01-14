'use client';

import { useState } from 'react';

interface Step3Props {
    value: number;
    onChange: (value: number) => void;
    onNext: () => void;
    onBack: () => void;
}

const CREDIT_RANGES = [
    { label: 'Excellent (760+)', min: 760, max: 850 },
    { label: 'Very Good (720-759)', min: 720, max: 759 },
    { label: 'Good (680-719)', min: 680, max: 719 },
    { label: 'Fair (640-679)', min: 640, max: 679 },
    { label: 'Poor (580-639)', min: 580, max: 639 },
    { label: 'Very Poor (Below 580)', min: 300, max: 579 },
];

export default function Step3CreditScore({ value, onChange, onNext, onBack }: Step3Props) {
    const [error, setError] = useState('');

    const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        onChange(Number(e.target.value));
        if (error) setError('');
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const numValue = Number(e.target.value);
        if (numValue >= 300 && numValue <= 850) {
            onChange(numValue);
            if (error) setError('');
        }
    };

    const handleNext = () => {
        if (!value || value < 300 || value > 850) {
            setError('Please enter a valid credit score (300-850)');
            return;
        }
        setError('');
        onNext();
    };

    const getCreditLabel = (score: number): string => {
        const range = CREDIT_RANGES.find(r => score >= r.min && score <= r.max);
        return range?.label.split(' ')[0] || '';
    };

    const getCreditColor = (score: number): string => {
        if (score >= 760) return '#22c55e'; // green
        if (score >= 720) return '#84cc16'; // lime
        if (score >= 680) return '#eab308'; // yellow
        if (score >= 640) return '#f97316'; // orange
        return '#ef4444'; // red
    };

    return (
        <div>
            <h3 className="text-3xl font-bold text-[#636363] mb-2" style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}>
                Credit Score
            </h3>
            <p className="text-[#636363] mb-6">What is your estimated FICO credit score?</p>

            <div className="mb-6">
                <div className="flex justify-between items-center mb-4">
                    <label className="block text-sm font-semibold text-[#636363]">
                        Your Credit Score *
                    </label>
                    <div className="flex items-center gap-2">
                        <input
                            type="number"
                            value={value || ''}
                            onChange={handleInputChange}
                            min={300}
                            max={850}
                            placeholder="740"
                            className={`
                w-20 p-2 border-2 rounded text-center text-lg font-bold
                focus:outline-none focus:border-[#1daed4]
                ${error ? 'border-red-500' : 'border-[#a5a5a5]'}
              `}
                        />
                        {value > 0 && (
                            <span
                                className="text-sm font-semibold px-2 py-1 rounded"
                                style={{
                                    backgroundColor: getCreditColor(value) + '20',
                                    color: getCreditColor(value)
                                }}
                            >
                                {getCreditLabel(value)}
                            </span>
                        )}
                    </div>
                </div>

                {/* Slider */}
                <div className="relative pt-1">
                    <input
                        type="range"
                        min={300}
                        max={850}
                        value={value || 700}
                        onChange={handleSliderChange}
                        className="w-full h-3 bg-gradient-to-r from-red-400 via-yellow-400 to-green-400 rounded-lg appearance-none cursor-pointer"
                        style={{
                            WebkitAppearance: 'none',
                        }}
                    />
                    <div className="flex justify-between text-xs text-[#a5a5a5] mt-1">
                        <span>300</span>
                        <span>580</span>
                        <span>680</span>
                        <span>760</span>
                        <span>850</span>
                    </div>
                </div>

                {error && <p className="mt-2 text-sm text-red-500">{error}</p>}
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
