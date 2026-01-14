interface LoadingSpinnerProps {
    message?: string;
}

export default function LoadingSpinner({ message = 'Loading...' }: LoadingSpinnerProps) {
    return (
        <div className="flex flex-col items-center justify-center py-16">
            {/* Spinner */}
            <div className="relative w-16 h-16 mb-6">
                <div className="absolute inset-0 border-4 border-[#a5a5a5]/30 rounded-full"></div>
                <div className="absolute inset-0 border-4 border-transparent border-t-[#1daed4] rounded-full animate-spin"></div>
            </div>

            {/* Message */}
            <p className="text-lg text-[#636363] font-medium animate-pulse">
                {message}
            </p>

            {/* Sub-message */}
            <p className="text-sm text-[#a5a5a5] mt-2">
                Searching our network of lenders...
            </p>
        </div>
    );
}
