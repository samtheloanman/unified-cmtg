'use client';

import { useState } from 'react';
import StepIndicator from './StepIndicator';
import Step1PropertyState from './Step1PropertyState';
import Step2LoanAmount from './Step2LoanAmount';
import Step3CreditScore from './Step3CreditScore';
import Step4PropertyValue from './Step4PropertyValue';
import ResultsCard from '../ResultsCard';
import LoadingSpinner from '../LoadingSpinner';

export interface FormData {
    property_state: string;
    loan_amount: number;
    credit_score: number;
    property_value: number;
}

export interface QuoteResult {
    ltv: number;
    matches_found: number;
    quotes: Array<{
        lender: string;
        program: string;
        base_rate: number;
        points: number;
    }>;
}

const INITIAL_FORM_DATA: FormData = {
    property_state: '',
    loan_amount: 0,
    credit_score: 0,
    property_value: 0,
};

export default function QuoteWizard() {
    const [step, setStep] = useState(1);
    const [formData, setFormData] = useState<FormData>(INITIAL_FORM_DATA);
    const [results, setResults] = useState<QuoteResult | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const updateFormData = (field: keyof FormData, value: string | number) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    const nextStep = () => {
        if (step < 4) {
            setStep(step + 1);
        } else {
            handleSubmit();
        }
    };

    const prevStep = () => {
        if (step > 1) {
            setStep(step - 1);
        }
    };

    const handleSubmit = async () => {
        setLoading(true);
        setError(null);

        try {
            const res = await fetch('http://localhost:8001/api/v1/quote/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData),
            });

            if (!res.ok) {
                if (res.status >= 500) {
                    throw new Error('Something went wrong. Please try again.');
                }
                const errorData = await res.json();
                throw new Error(errorData.detail || 'Validation error');
            }

            const data = await res.json();
            setResults(data);
            setStep(5); // Results step
        } catch (err) {
            if (err instanceof TypeError) {
                setError('Unable to connect. Please check your connection.');
            } else if (err instanceof Error) {
                setError(err.message);
            } else {
                setError('An unexpected error occurred.');
            }
        } finally {
            setLoading(false);
        }
    };

    const resetWizard = () => {
        setStep(1);
        setFormData(INITIAL_FORM_DATA);
        setResults(null);
        setError(null);
    };

    if (loading) {
        return <LoadingSpinner message="Getting your personalized quote..." />;
    }

    if (step === 5 && results) {
        return <ResultsCard results={results} onReset={resetWizard} />;
    }

    return (
        <div className="w-full max-w-xl mx-auto">
            <StepIndicator currentStep={step} totalSteps={4} />

            <div className="bg-white border-2 border-[#a5a5a5] rounded-lg shadow-lg p-8 mt-6">
                {step === 1 && (
                    <Step1PropertyState
                        value={formData.property_state}
                        onChange={(val) => updateFormData('property_state', val)}
                        onNext={nextStep}
                    />
                )}

                {step === 2 && (
                    <Step2LoanAmount
                        value={formData.loan_amount}
                        onChange={(val) => updateFormData('loan_amount', val)}
                        onNext={nextStep}
                        onBack={prevStep}
                    />
                )}

                {step === 3 && (
                    <Step3CreditScore
                        value={formData.credit_score}
                        onChange={(val) => updateFormData('credit_score', val)}
                        onNext={nextStep}
                        onBack={prevStep}
                    />
                )}

                {step === 4 && (
                    <Step4PropertyValue
                        value={formData.property_value}
                        onChange={(val) => updateFormData('property_value', val)}
                        onNext={nextStep}
                        onBack={prevStep}
                        isSubmitting={loading}
                    />
                )}

                {error && (
                    <div className="mt-6 p-4 bg-red-50 border-l-4 border-red-500 text-red-700 rounded">
                        {error}
                    </div>
                )}
            </div>
        </div>
    );
}
