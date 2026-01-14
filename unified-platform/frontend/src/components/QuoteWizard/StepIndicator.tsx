interface StepIndicatorProps {
    currentStep: number;
    totalSteps: number;
}

const STEP_LABELS = ['State', 'Loan', 'Credit', 'Value'];

export default function StepIndicator({ currentStep, totalSteps }: StepIndicatorProps) {
    return (
        <div className="w-full">
            {/* Step Counter */}
            <div className="text-center mb-4">
                <span className="text-lg font-bold text-[#636363]" style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}>
                    Step {currentStep} of {totalSteps}
                </span>
            </div>

            {/* Progress Bar */}
            <div className="flex items-center justify-between relative">
                {/* Background Line */}
                <div className="absolute top-1/2 left-0 right-0 h-1 bg-[#a5a5a5] -translate-y-1/2 z-0" />

                {/* Progress Line */}
                <div
                    className="absolute top-1/2 left-0 h-1 bg-[#1daed4] -translate-y-1/2 z-0 transition-all duration-300"
                    style={{ width: `${((currentStep - 1) / (totalSteps - 1)) * 100}%` }}
                />

                {/* Step Circles */}
                {Array.from({ length: totalSteps }, (_, i) => {
                    const stepNum = i + 1;
                    const isCompleted = stepNum < currentStep;
                    const isCurrent = stepNum === currentStep;

                    return (
                        <div key={stepNum} className="flex flex-col items-center z-10">
                            <div
                                className={`
                  w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm
                  transition-all duration-300
                  ${isCompleted
                                        ? 'bg-[#1daed4] text-white'
                                        : isCurrent
                                            ? 'bg-[#1daed4] text-white ring-4 ring-[#1daed4]/30'
                                            : 'bg-white border-2 border-[#a5a5a5] text-[#636363]'
                                    }
                `}
                            >
                                {isCompleted ? '✓' : stepNum}
                            </div>
                            <span className={`
                mt-2 text-xs font-medium
                ${isCurrent ? 'text-[#1daed4]' : 'text-[#636363]'}
              `}>
                                {STEP_LABELS[i]}
                            </span>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
