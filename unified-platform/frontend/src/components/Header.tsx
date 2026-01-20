'use client';

import Link from 'next/link';
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
                    apiClient.cms.getNavigation('Main Header'),
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

    const phoneDisplay = siteConfig?.phone_number || '(877) 976-5669';
    const phoneHref = `tel:${phoneDisplay.replace(/[^0-9]/g, '')}`;

    return (
        <header className="sticky top-0 z-50 shadow-md">
            {/* Top Bar - Premium Dark Gradient */}
            <div className="bg-gradient-to-r from-slate-900 to-slate-800 text-white text-xs md:text-sm py-2 px-4 border-b border-white/10">
                <div className="max-w-7xl mx-auto flex justify-between items-center">
                    <a href={phoneHref} className="flex items-center gap-2 hover:text-[var(--primary)] transition-colors font-medium">
                        <span className="text-[var(--primary)]">📞</span> {phoneDisplay}
                    </a>
                    <div className="flex items-center gap-4">
                        <Link href="/quote" className="hover:text-[var(--primary)] transition-colors hidden sm:inline font-medium uppercase tracking-wider">
                            Get Quote
                        </Link>
                        <a href="https://custommortgage.floify.com/" target="_blank" rel="noopener noreferrer"
                            className="bg-[var(--primary)] hover:bg-[var(--primary-dark)] text-white px-5 py-1.5 rounded-full font-bold text-xs uppercase tracking-widest transition-all shadow-lg hover:shadow-[var(--primary)]/30">
                            Apply Now
                        </a>
                    </div>
                </div>
            </div>

            {/* Main Navigation - Glassmorphism */}
            <nav className="bg-white/95 backdrop-blur-md border-b border-gray-100 text-slate-800">
                <div className="max-w-7xl mx-auto px-4">
                    <div className="flex justify-between items-center h-20">
                        {/* Logo */}
                        <Link href="/" className="flex items-center gap-3 group">
                            {siteConfig?.logo_url ? (
                                <img src={siteConfig.logo_url} alt={siteConfig.site_name} className="h-12 w-auto object-contain" />
                            ) : (
                                <span className="text-3xl font-heading font-normal tracking-wide text-slate-900 group-hover:text-[var(--primary)] transition-colors">
                                    {siteConfig?.site_name || 'CUSTOM MORTGAGE'}
                                </span>
                            )}
                        </Link>

                        {/* Desktop Navigation */}
                        <div className="hidden lg:flex items-center space-x-1">
                            {navData?.items.map((item) => {
                                // Sub Menu
                                if (item.type === 'sub_menu' && item.value.items) {
                                    return (
                                        <div
                                            key={item.id}
                                            className="relative group"
                                            onMouseEnter={() => setOpenDropdown(item.id)}
                                            onMouseLeave={() => setOpenDropdown(null)}
                                        >
                                            <button
                                                className={`px-4 py-2 text-sm font-bold uppercase tracking-wider hover:text-[var(--primary)] transition-colors flex items-center gap-1 font-heading
                                                    ${openDropdown === item.id ? 'text-[var(--primary)]' : 'text-slate-600'}`}
                                            >
                                                {item.value.title}
                                                <svg className={`w-3 h-3 transition-transform ${openDropdown === item.id ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                                </svg>
                                            </button>

                                            {/* Dropdown Menu */}
                                            {openDropdown === item.id && (
                                                <div className="absolute left-0 top-full w-72 bg-white shadow-2xl rounded-b-xl overflow-hidden z-50 border-t-2 border-[var(--primary)] animate-in fade-in slide-in-from-top-2 duration-200">
                                                    <div className="py-2">
                                                        {item.value.items.map((subItem, idx) => (
                                                            <Link
                                                                key={idx}
                                                                href={subItem.link_url || '#'}
                                                                target={subItem.open_in_new_tab ? '_blank' : undefined}
                                                                className="block px-6 py-3 text-sm text-slate-600 hover:bg-slate-50 hover:text-[var(--primary)] hover:pl-7 transition-all border-b border-slate-50 last:border-0"
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
                                            className="px-4 py-2 text-sm font-bold uppercase tracking-wider text-slate-600 hover:text-[var(--primary)] transition-colors font-heading"
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
                            className="lg:hidden p-2 text-slate-600"
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

                {/* Mobile Menu Overlay */}
                {mobileMenuOpen && (
                    <div className="lg:hidden bg-slate-900 border-t border-slate-800 absolute w-full h-[calc(100vh-80px)] overflow-y-auto">
                        <div className="px-6 py-8 space-y-6">
                            {navData?.items.map((item) => {
                                if (item.type === 'sub_menu' && item.value.items) {
                                    return (
                                        <div key={item.id}>
                                            <h3 className="text-[var(--primary)] text-sm font-bold uppercase tracking-widest mb-3 font-heading">
                                                {item.value.title}
                                            </h3>
                                            <div className="space-y-3 pl-4 border-l border-slate-700">
                                                {item.value.items.map((subItem, idx) => (
                                                    <Link
                                                        key={idx}
                                                        href={subItem.link_url || '#'}
                                                        className="block text-slate-300 hover:text-white text-base font-medium"
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
                                            className="block text-white text-xl font-heading font-normal tracking-wide hover:text-[var(--primary)]"
                                            onClick={() => setMobileMenuOpen(false)}
                                        >
                                            {item.value.link_text}
                                        </Link>
                                    );
                                }
                                return null;
                            })}

                            <div className="pt-8 mt-8 border-t border-slate-800">
                                <Link
                                    href="/quote"
                                    className="block w-full text-center py-4 bg-[var(--primary)] text-white font-bold rounded-lg uppercase tracking-widest shadow-lg shadow-[var(--primary)]/20"
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
