'use client';

import Link from 'next/link';
import { useState } from 'react';

// Navigation structure matching production site with correct program links
const navigation = {
    topBar: {
        phone: '877-976-5669',
        applyUrl: 'https://custommortgage.floify.com/',
    },
    mainNav: [
        {
            label: 'Residential Mortgage',
            href: '/programs',
            children: [
                { label: 'FHA VOE Only Mortgage', href: '/programs/fha-voe-only-mortgage-loans' },
                { label: 'Super Jumbo Loans', href: '/programs/super-jumbo-residential-mortgage-loans' },
                { label: 'FHA Streamline Mortgage', href: '/programs/fha-streamline-mortgage-loans' },
                { label: 'Reverse Mortgage', href: '/programs/reverse-mortgages-loan-programs' },
                { label: 'VA Loans', href: '/programs/verterain-va-loans' },
                { label: 'Construction Loans', href: '/programs/construction-loans-2' },
                { label: 'View All Residential →', href: '/programs' },
            ],
        },
        {
            label: 'Commercial Mortgage',
            href: '/programs/commercial-mortgage-loans',
            children: [
                { label: 'Stated Income Commercial', href: '/programs/stated-income-commercial-loans' },
                { label: 'SBA Loans', href: '/programs/business-loans' },
                { label: 'Church Financing', href: '/programs/cmre' },
                { label: 'Multifamily Loans', href: '/programs/apartment-finance-mortgage-loans' },
                { label: 'Mixed Use Loans', href: '/programs/retail-property-loans' },
                { label: 'View All Commercial →', href: '/programs' },
            ],
        },
        {
            label: 'NonQM / Stated Income',
            href: '/programs',
            children: [
                { label: 'Bank Statement Loans', href: '/programs/bank-statement-loans' },
                { label: 'Asset Depletion', href: '/programs/asset-depletion-loans' },
                { label: 'No Ratio Loans', href: '/programs/no-ratio-loans' },
                { label: '1099 Only Loans', href: '/programs/1099-only-loans' },
                { label: 'View All NonQM →', href: '/programs' },
            ],
        },
        {
            label: 'Hard Money',
            href: '/programs/hard-money-loans',
            children: [
                { label: 'Fix and Flip', href: '/programs/fix-flip-rehab-loan-rehab-mortgage-loans' },
                { label: 'Bridge Loans', href: '/programs/rehab-loans' },
                { label: 'Create Your Own Terms', href: '/programs/hard-money-mortgage-loans' },
                { label: 'View All Hard Money →', href: '/programs' },
            ],
        },
        { label: 'Recently Funded', href: '/funded-loans' },
        { label: 'Blog', href: '/blog' },
    ],
};

export default function Header() {
    const [openDropdown, setOpenDropdown] = useState<string | null>(null);
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    return (
        <header className="sticky top-0 z-50">
            {/* Top Bar */}
            <div className="bg-[#1daed4] text-white text-sm py-2 px-4">
                <div className="max-w-7xl mx-auto flex justify-between items-center">
                    <a href={`tel:${navigation.topBar.phone.replace(/-/g, '')}`} className="flex items-center gap-2 hover:underline">
                        📞 {navigation.topBar.phone}
                    </a>
                    <div className="flex items-center gap-4">
                        <Link href="/quote" className="hover:underline hidden sm:inline">Get Quote</Link>
                        <a href={navigation.topBar.applyUrl} target="_blank" rel="noopener noreferrer"
                            className="bg-white text-[#1daed4] px-4 py-1 rounded font-bold hover:bg-gray-100 transition-colors">
                            APPLY NOW
                        </a>
                    </div>
                </div>
            </div>

            {/* Main Navigation */}
            <nav className="bg-[#636363] text-white">
                <div className="max-w-7xl mx-auto px-4">
                    <div className="flex justify-between items-center h-16">
                        {/* Logo */}
                        <Link href="/" className="text-2xl md:text-3xl font-bold tracking-wide" style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}>
                            CUSTOM MORTGAGE
                        </Link>

                        {/* Desktop Navigation */}
                        <div className="hidden lg:flex items-center space-x-1">
                            {navigation.mainNav.map((item) => (
                                <div
                                    key={item.label}
                                    className="relative"
                                    onMouseEnter={() => item.children && setOpenDropdown(item.label)}
                                    onMouseLeave={() => setOpenDropdown(null)}
                                >
                                    <Link
                                        href={item.href}
                                        className={`px-3 py-2 text-sm font-medium hover:text-[#1daed4] transition-colors flex items-center gap-1 ${openDropdown === item.label ? 'text-[#1daed4]' : ''
                                            }`}
                                        style={{ fontFamily: 'Bebas Neue, Arial, sans-serif', letterSpacing: '0.05em' }}
                                    >
                                        {item.label}
                                        {item.children && (
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                            </svg>
                                        )}
                                    </Link>

                                    {/* Dropdown */}
                                    {item.children && openDropdown === item.label && (
                                        <div className="absolute left-0 top-full w-64 bg-white text-[#636363] shadow-xl rounded-b-lg overflow-hidden z-50">
                                            {item.children.map((child) => (
                                                <Link
                                                    key={child.label}
                                                    href={child.href}
                                                    className="block px-4 py-3 text-sm hover:bg-[#1daed4] hover:text-white transition-colors border-b border-gray-100 last:border-b-0"
                                                >
                                                    {child.label}
                                                </Link>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>

                        {/* Mobile Menu Button */}
                        <button
                            className="lg:hidden p-2"
                            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                            aria-label="Toggle menu"
                        >
                            {mobileMenuOpen ? (
                                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            ) : (
                                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                                </svg>
                            )}
                        </button>
                    </div>
                </div>

                {/* Mobile Menu */}
                {mobileMenuOpen && (
                    <div className="lg:hidden bg-[#636363] border-t border-gray-500">
                        <div className="px-4 py-4 space-y-2">
                            {navigation.mainNav.map((item) => (
                                <div key={item.label}>
                                    <Link
                                        href={item.href}
                                        className="block py-2 text-lg font-medium hover:text-[#1daed4]"
                                        style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                                        onClick={() => setMobileMenuOpen(false)}
                                    >
                                        {item.label}
                                    </Link>
                                    {item.children && (
                                        <div className="pl-4 space-y-1">
                                            {item.children.slice(0, 3).map((child) => (
                                                <Link
                                                    key={child.label}
                                                    href={child.href}
                                                    className="block py-1 text-sm text-gray-300 hover:text-[#1daed4]"
                                                    onClick={() => setMobileMenuOpen(false)}
                                                >
                                                    {child.label}
                                                </Link>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            ))}
                            <div className="pt-4 border-t border-gray-500">
                                <Link
                                    href="/quote"
                                    className="block w-full text-center py-3 bg-[#1daed4] text-white font-bold rounded-lg"
                                    style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                                    onClick={() => setMobileMenuOpen(false)}
                                >
                                    GET YOUR QUOTE
                                </Link>
                            </div>
                        </div>
                    </div>
                )}
            </nav>
        </header>
    );
}
