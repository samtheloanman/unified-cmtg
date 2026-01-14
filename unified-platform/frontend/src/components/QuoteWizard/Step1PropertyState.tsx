'use client';

import { useState } from 'react';

const US_STATES = [
    { code: 'AL', name: 'Alabama' }, { code: 'AK', name: 'Alaska' }, { code: 'AZ', name: 'Arizona' },
    { code: 'AR', name: 'Arkansas' }, { code: 'CA', name: 'California' }, { code: 'CO', name: 'Colorado' },
    { code: 'CT', name: 'Connecticut' }, { code: 'DE', name: 'Delaware' }, { code: 'FL', name: 'Florida' },
    { code: 'GA', name: 'Georgia' }, { code: 'HI', name: 'Hawaii' }, { code: 'ID', name: 'Idaho' },
    { code: 'IL', name: 'Illinois' }, { code: 'IN', name: 'Indiana' }, { code: 'IA', name: 'Iowa' },
    { code: 'KS', name: 'Kansas' }, { code: 'KY', name: 'Kentucky' }, { code: 'LA', name: 'Louisiana' },
    { code: 'ME', name: 'Maine' }, { code: 'MD', name: 'Maryland' }, { code: 'MA', name: 'Massachusetts' },
    { code: 'MI', name: 'Michigan' }, { code: 'MN', name: 'Minnesota' }, { code: 'MS', name: 'Mississippi' },
    { code: 'MO', name: 'Missouri' }, { code: 'MT', name: 'Montana' }, { code: 'NE', name: 'Nebraska' },
    { code: 'NV', name: 'Nevada' }, { code: 'NH', name: 'New Hampshire' }, { code: 'NJ', name: 'New Jersey' },
    { code: 'NM', name: 'New Mexico' }, { code: 'NY', name: 'New York' }, { code: 'NC', name: 'North Carolina' },
    { code: 'ND', name: 'North Dakota' }, { code: 'OH', name: 'Ohio' }, { code: 'OK', name: 'Oklahoma' },
    { code: 'OR', name: 'Oregon' }, { code: 'PA', name: 'Pennsylvania' }, { code: 'RI', name: 'Rhode Island' },
    { code: 'SC', name: 'South Carolina' }, { code: 'SD', name: 'South Dakota' }, { code: 'TN', name: 'Tennessee' },
    { code: 'TX', name: 'Texas' }, { code: 'UT', name: 'Utah' }, { code: 'VT', name: 'Vermont' },
    { code: 'VA', name: 'Virginia' }, { code: 'WA', name: 'Washington' }, { code: 'WV', name: 'West Virginia' },
    { code: 'WI', name: 'Wisconsin' }, { code: 'WY', name: 'Wyoming' },
];

interface Step1Props {
    value: string;
    onChange: (value: string) => void;
    onNext: () => void;
}

export default function Step1PropertyState({ value, onChange, onNext }: Step1Props) {
    const [error, setError] = useState('');

    const handleNext = () => {
        if (!value) {
            setError('Please select a state');
            return;
        }
        setError('');
        onNext();
    };

    return (
        <div>
            <h3 className="text-3xl font-bold text-[#636363] mb-2" style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}>
                Where is the Property?
            </h3>
            <p className="text-[#636363] mb-6">Select the state where the property is located.</p>

            <div className="mb-6">
                <label className="block text-sm font-semibold text-[#636363] mb-2">
                    Property State *
                </label>
                <select
                    value={value}
                    onChange={(e) => {
                        onChange(e.target.value);
                        if (error) setError('');
                    }}
                    className={`
            w-full p-4 border-2 rounded-lg text-lg
            focus:outline-none focus:border-[#1daed4]
            ${error ? 'border-red-500' : 'border-[#a5a5a5]'}
          `}
                >
                    <option value="">Select a state...</option>
                    {US_STATES.map(state => (
                        <option key={state.code} value={state.code}>
                            {state.name}
                        </option>
                    ))}
                </select>
                {error && <p className="mt-2 text-sm text-red-500">{error}</p>}
            </div>

            <button
                onClick={handleNext}
                className="w-full py-4 bg-[#1daed4] hover:bg-[#17a0c4] text-white font-bold rounded-lg transition-colors text-lg shadow-md hover:shadow-lg"
                style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
            >
                Continue
            </button>
        </div>
    );
}
