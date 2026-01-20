'use client';

import { useEffect, useRef, useState } from 'react';

interface ScrollRevealProps {
    children: React.ReactNode;
    width?: 'fit-content' | '100%';
    delay?: number; // Delay in ms
    animation?: 'fade-up' | 'fade-in' | 'slide-in-right' | 'scale-up';
    className?: string;
}

export const ScrollReveal = ({
    children,
    width = 'fit-content',
    delay = 0,
    animation = 'fade-up',
    className = ''
}: ScrollRevealProps) => {
    const [isVisible, setIsVisible] = useState(false);
    const ref = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting) {
                    setIsVisible(true);
                    observer.unobserve(entry.target);
                }
            },
            {
                root: null,
                rootMargin: '0px',
                threshold: 0.1, // Trigger when 10% visible
            }
        );

        if (ref.current) {
            observer.observe(ref.current);
        }

        return () => {
            if (ref.current) {
                observer.unobserve(ref.current);
            }
        };
    }, []);

    const getTransform = () => {
        if (!isVisible) {
            switch (animation) {
                case 'fade-up': return 'translateY(40px)';
                case 'slide-in-right': return 'translateX(-40px)';
                case 'scale-up': return 'scale(0.95)';
                case 'fade-in': return 'none';
                default: return 'translateY(40px)';
            }
        }
        return 'none';
    };

    const getOpacity = () => (isVisible ? 1 : 0);

    return (
        <div
            ref={ref}
            className={className}
            style={{
                width,
                transform: getTransform(),
                opacity: getOpacity(),
                transition: `all 0.8s cubic-bezier(0.17, 0.55, 0.55, 1) ${delay}ms`,
                willChange: 'transform, opacity',
            }}
        >
            {children}
        </div>
    );
};
