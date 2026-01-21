'use client';

import Link from 'next/link';
import Image from 'next/image';
import { useState, useEffect } from 'react';
import { apiClient, NavigationMenu, SiteConfiguration } from '@/lib/api-client';

export default function Header() {
    const [openDropdown, setOpenDropdown] = useState<string | null>(null);
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    const [navData, setNavData] = useState<NavigationMenu | null>(null);
    const [siteConfig, setSiteConfig] = useState<SiteConfiguration | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchData() {
            try {
                const [navRes, configRes] = await Promise.all([
                    apiClient.cms.getNavigation('main-header'),
                    apiClient.cms.getSiteConfiguration()
                ]);

                if (navRes.success) setNavData(navRes.data);
                if (configRes.success) setSiteConfig(configRes.data);
            } catch (error) {
                console.error("Failed to fetch header data", error);
            } finally {
                setLoading(false);
            }
        }
        fetchData();
    }, []);

    // Fallback if loading or error (keep skeleton or minimal)
    if (loading) {
        return <header className="h-24 bg-white animate-pulse" />;
    }

    // Raw HTML Override
    if (navData?.raw_html && navData.raw_html.trim()) {
        return <div dangerouslySetInnerHTML={{ __html: navData.raw_html }} />;
    }

    const phoneDisplay = siteConfig?.phone_number || '(877) 976-5669';
    const phoneHref = `tel:${phoneDisplay.replace(/[^0-9]/g, '')}`;

    return (
        <header className="sticky top-0 z-50 font-sans">
            {/* Top Bar - Cyan Background to match production */}
            <div className="bg-[#1daed4] text-white py-0 px-4 relative z-20 border-b border-[#0f8aab]">
                <div className="max-w-7xl mx-auto flex justify-between items-center text-sm font-bold tracking-widest uppercase h-10">
                    {/* Left: Apply Now Button + Sign In */}
                    <div className="flex items-center gap-6 divide-x divide-white/20">
                        <a href="https://custommortgage.floify.com/" target="_blank" rel="noopener noreferrer"
                            className="flex items-center gap-2 hover:text-white/80 transition-opacity pr-6">
                            <span className="text-white text-lg">✓</span>
                            <span>Apply Now</span>
                        </a>

                        <a href="https://custommortgage.floify.com/" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 hover:text-white/80 transition-opacity pl-6">
                            <span className="text-white text-lg">➜</span>
                            <span>Sign In</span>
                        </a>
                    </div>

                    {/* Center/Right: Phone */}
                    <div className="flex items-center gap-2">
                        <span className="transform flip-x">📞</span>
                        <a href={phoneHref} className="hover:text-white/80 transition-opacity text-base">
                            {phoneDisplay}
                        </a>
                    </div>

                    {/* Far Right: Request Call Back (Hidden on mobile usually) */}
                    <div className="hidden md:block text-xs font-normal opacity-90">
                        Request Call Back
                    </div>
                </div>
            </div>

            {/* Main Navigation - White Background */}
            <nav className="bg-white border-b border-gray-200 text-[#0f2933] relative z-10 shadow-sm">
                <div className="max-w-7xl mx-auto px-4">
                    <div className="flex justify-between items-center h-24">
                        {/* Logo */}
                        <Link href="/" className="flex items-center shrink-0">
                            <Image
                                src="/assets/logo-color.png"
                                alt="Custom Mortgage + Real Estate"
                                width={240}
                                height={64}
                                className="h-16 w-auto object-contain"
                                priority
                            />
                        </Link>

                        {/* Desktop Navigation - Centered & Bold */}
                        <div className="hidden lg:flex items-center justify-center flex-1 ml-12 space-x-12">
                            {navData?.items.map((item) => {
                                // Sub Menu
                                if (item.type === 'sub_menu' && item.value.items) {
                                    return (
                                        <div
                                            key={item.id}
                                            className="relative group h-full flex items-center h-24"
                                            onMouseEnter={() => setOpenDropdown(item.id)}
                                            onMouseLeave={() => setOpenDropdown(null)}
                                        >
                                            <button
                                                className={`py-2 text-lg font-bold uppercase tracking-wide hover:text-[#1daed4] transition-colors flex items-center gap-1 font-heading text-[#0f2933]`}
                                                style={{ fontFamily: 'Bebas Neue, sans-serif' }}
                                            >
                                                {item.value.title}
                                                <svg className={`w-3 h-3 transition-transform ${openDropdown === item.id ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                                </svg>
                                            </button>

                                            {/* Mega Menu Dropdown */}
                                            {openDropdown === item.id && (
                                                <div className="absolute left-0 top-full pt-0 w-64 z-50">
                                                    <div className="bg-white border-t-4 border-[#1daed4] border-x border-b border-gray-100 shadow-2xl py-0">
                                                        {item.value.items.map((subItem, idx) => (
                                                            <Link
                                                                key={idx}
                                                                href={subItem.link_url || '#'}
                                                                target={subItem.open_in_new_tab ? '_blank' : undefined}
                                                                className="block px-6 py-4 text-sm font-bold text-gray-600 hover:bg-[#f8f9fa] hover:text-[#1daed4] hover:pl-8 transition-all border-b border-gray-100 last:border-0 uppercase tracking-wider"
                                                            >
                                                                {subItem.link_text}
                                                            </Link>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    );
                                }

                                // Simple Link
                                if (item.type === 'link') {
                                    return (
                                        <Link
                                            key={item.id}
                                            href={item.value.link_url || '#'}
                                            target={item.value.open_in_new_tab ? '_blank' : undefined}
                                            className="py-2 text-lg font-bold uppercase tracking-wide text-[#0f2933] hover:text-[#1daed4] transition-colors font-heading"
                                            style={{ fontFamily: 'Bebas Neue, sans-serif' }}
                                        >
                                            {item.value.link_text}
                                        </Link>
                                    );
                                }
                                return null;
                            })}
                        </div>

                        {/* Mobile Menu Button */}
                        <button
                            className="lg:hidden p-2 text-[#0f2933]"
                            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                            aria-label="Toggle menu"
                        >
                            {mobileMenuOpen ? (
                                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            ) : (
                                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                                </svg>
                            )}
                        </button>
                    </div>
                </div>

                {/* Mobile Menu Overlay */}
                {mobileMenuOpen && (
                    <div className="lg:hidden bg-white fixed inset-0 top-[115px] z-50 overflow-y-auto pb-20">
                        <div className="px-6 py-8 space-y-6">
                            {navData?.items.map((item) => {
                                if (item.type === 'sub_menu' && item.value.items) {
                                    return (
                                        <div key={item.id} className="border-b border-gray-100 pb-4">
                                            <h3 className="text-[#1daed4] text-xl font-bold uppercase tracking-wide mb-3 font-heading" style={{ fontFamily: 'Bebas Neue, sans-serif' }}>
                                                {item.value.title}
                                            </h3>
                                            <div className="space-y-3 pl-4 border-l-2 border-gray-100">
                                                {item.value.items.map((subItem, idx) => (
                                                    <Link
                                                        key={idx}
                                                        href={subItem.link_url || '#'}
                                                        className="block text-gray-600 hover:text-[#1daed4] text-sm font-bold uppercase tracking-wider"
                                                        onClick={() => setMobileMenuOpen(false)}
                                                    >
                                                        {subItem.link_text}
                                                    </Link>
                                                ))}
                                            </div>
                                        </div>
                                    );
                                }
                                if (item.type === 'link') {
                                    return (
                                        <Link
                                            key={item.id}
                                            href={item.value.link_url || '#'}
                                            className="block text-[#0f2933] text-2xl font-heading font-bold tracking-wide hover:text-[#1daed4] border-b border-gray-100 pb-4"
                                            style={{ fontFamily: 'Bebas Neue, sans-serif' }}
                                            onClick={() => setMobileMenuOpen(false)}
                                        >
                                            {item.value.link_text}
                                        </Link>
                                    );
                                }
                                return null;
                            })}

                            <div className="pt-4">
                                <Link
                                    href="/quote"
                                    className="block w-full text-center py-4 bg-[#1daed4] text-white font-bold text-xl uppercase tracking-widest hover:bg-[#17a0c4] transition-colors"
                                    style={{ fontFamily: 'Bebas Neue, sans-serif' }}
                                    onClick={() => setMobileMenuOpen(false)}
                                >
                                    Get Your Quote
                                </Link>
                            </div>
                        </div>
                    </div>
                )}
            </nav>
        </header>
    );
}

