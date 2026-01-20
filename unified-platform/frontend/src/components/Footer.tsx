'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { apiClient, SiteConfiguration, NavigationMenu } from '@/lib/api-client';

export default function Footer() {
    const [siteConfig, setSiteConfig] = useState<SiteConfiguration | null>(null);
    const [footerMenu, setFooterMenu] = useState<NavigationMenu | null>(null);

    useEffect(() => {
        async function fetchFooterData() {
            try {
                const [configRes, menuRes] = await Promise.all([
                    apiClient.cms.getSiteConfiguration(),
                    apiClient.cms.getNavigation('Footer')
                ]);
                if (configRes.success) setSiteConfig(configRes.data);
                if (menuRes.success) setFooterMenu(menuRes.data);
            } catch (err) {
                console.error("Failed to fetch footer data", err);
            }
        }
        fetchFooterData();
    }, []);

    // Raw HTML Override
    if (siteConfig?.footer_raw_html && siteConfig.footer_raw_html.trim()) {
        return <div dangerouslySetInnerHTML={{ __html: siteConfig.footer_raw_html }} />;
    } else if (footerMenu?.raw_html && footerMenu.raw_html.trim()) {
        return <div dangerouslySetInnerHTML={{ __html: footerMenu.raw_html }} />;
    }


    const currentYear = new Date().getFullYear();

    return (
        <footer className="bg-[#0f2933] text-white border-t-4 border-[#1daed4]">
            {/* Main Footer Content */}
            <div className="max-w-7xl mx-auto py-20 px-6">
                <div className="grid md:grid-cols-12 gap-12">

                    {/* Brand Column (Span 4) */}
                    <div className="md:col-span-4">
                        <Link href="/" className="inline-block mb-8">
                            {siteConfig?.logo_url ? (
                                <img src={siteConfig.logo_url} alt={siteConfig.site_name} className="h-16 w-auto object-contain brightness-0 invert" />
                            ) : (
                                <div className="text-4xl font-heading font-black tracking-tighter text-white uppercase leading-none" style={{ fontFamily: 'Bebas Neue, sans-serif' }}>
                                    Custom<span className="text-[#1daed4]">Mtg</span><br />
                                    <span className="text-lg tracking-[0.2em] opacity-50">Inc.</span>
                                </div>
                            )}
                        </Link>

                        <p className="text-white/60 text-sm leading-relaxed mb-8 max-w-sm">
                            A fintech real estate and finance agency providing precision lending solutions for residential and commercial clients nationwide.
                        </p>

                        <div className="flex gap-3">
                            {siteConfig?.linkedin && <a href={siteConfig.linkedin} className="w-10 h-10 border border-white/10 text-white/50 flex items-center justify-center hover:bg-[#1daed4] hover:text-white hover:border-[#1daed4] transition-all">in</a>}
                            {siteConfig?.facebook && <a href={siteConfig.facebook} className="w-10 h-10 border border-white/10 text-white/50 flex items-center justify-center hover:bg-[#1daed4] hover:text-white hover:border-[#1daed4] transition-all">fb</a>}
                            {siteConfig?.instagram && <a href={siteConfig.instagram} className="w-10 h-10 border border-white/10 text-white/50 flex items-center justify-center hover:bg-[#1daed4] hover:text-white hover:border-[#1daed4] transition-all">ig</a>}
                        </div>
                    </div>

                    {/* Navigation Columns (Span 2 each) */}
                    {Object.keys(footerMenu?.items || {}).length > 0 ? (
                        footerMenu?.items.map((item, idx) => {
                            if (item.type === 'sub_menu') {
                                return (
                                    <div key={item.id} className="md:col-span-2">
                                        <h4 className="text-lg font-bold text-[#1daed4] mb-8 uppercase tracking-widest font-heading" style={{ fontFamily: 'Bebas Neue, sans-serif' }}>
                                            {item.value.title}
                                        </h4>
                                        <ul className="space-y-4 text-xs font-bold tracking-wide uppercase text-white/70">
                                            {item.value.items?.map((subItem, subIdx) => (
                                                <li key={subIdx}>
                                                    <Link
                                                        href={subItem.link_url || '#'}
                                                        target={subItem.open_in_new_tab ? '_blank' : undefined}
                                                        className="hover:text-white hover:translate-x-1 inline-block transition-all"
                                                    >
                                                        {subItem.link_text}
                                                    </Link>
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                );
                            }
                            return null;
                        })
                    ) : (
                        /* Fallback Columns */
                        <>
                            <div className="md:col-span-2">
                                <h4 className="text-xl font-bold text-[#1daed4] mb-8 uppercase tracking-widest font-heading" style={{ fontFamily: 'Bebas Neue, sans-serif' }}>Programs</h4>
                                <ul className="space-y-4 text-xs font-bold tracking-wide uppercase text-white/70">
                                    <li><Link href="/programs" className="hover:text-white hover:translate-x-1 inline-block transition-all">View All</Link></li>
                                    <li><Link href="/programs/commercial" className="hover:text-white hover:translate-x-1 inline-block transition-all">Commercial</Link></li>
                                    <li><Link href="/programs/residential" className="hover:text-white hover:translate-x-1 inline-block transition-all">Residential</Link></li>
                                </ul>
                            </div>
                            <div className="md:col-span-2">
                                <h4 className="text-xl font-bold text-[#1daed4] mb-8 uppercase tracking-widest font-heading" style={{ fontFamily: 'Bebas Neue, sans-serif' }}>Company</h4>
                                <ul className="space-y-4 text-xs font-bold tracking-wide uppercase text-white/70">
                                    <li><Link href="/about" className="hover:text-white hover:translate-x-1 inline-block transition-all">About Us</Link></li>
                                    <li><Link href="/contact" className="hover:text-white hover:translate-x-1 inline-block transition-all">Contact</Link></li>
                                    <li><Link href="/careers" className="hover:text-white hover:translate-x-1 inline-block transition-all">Careers</Link></li>
                                </ul>
                            </div>
                        </>
                    )}

                    {/* Contact Info (Span 4) */}
                    <div className="md:col-span-4 pl-0 md:pl-8 border-l border-white/5">
                        <h4 className="text-xl font-bold text-white mb-8 uppercase tracking-widest font-heading" style={{ fontFamily: 'Bebas Neue, sans-serif' }}>Contact Us</h4>

                        <div className="space-y-6">
                            {siteConfig?.phone_number && (
                                <div>
                                    <p className="text-[10px] uppercase text-[#1daed4] tracking-widest mb-1">Phone</p>
                                    <a href={`tel:${siteConfig.phone_number}`} className="text-2xl font-bold text-white hover:text-[#1daed4] transition-colors">{siteConfig.phone_number}</a>
                                </div>
                            )}

                            {siteConfig?.address && (
                                <div>
                                    <p className="text-[10px] uppercase text-[#1daed4] tracking-widest mb-1">Headquarters</p>
                                    <p className="text-white/60 text-sm whitespace-pre-line leading-relaxed">{siteConfig.address}</p>
                                </div>
                            )}

                            <div>
                                <Link href="/quote" className="inline-block mt-4 bg-[#1daed4] text-white px-8 py-4 font-bold uppercase tracking-widest text-sm hover:bg-white hover:text-[#0f2933] transition-all">
                                    Start Application
                                </Link>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Bottom Bar - Legal */}
            <div className="bg-[#0a1f26] py-10 px-6 border-t border-white/5">
                <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6 text-[10px] text-white/30 uppercase tracking-widest font-bold">
                    <p>
                        © 2001-{currentYear} Custom MTG Inc. All Rights Reserved.
                    </p>
                    <div className="flex gap-6">
                        <Link href="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link>
                        <Link href="/terms" className="hover:text-white transition-colors">Terms of Use</Link>
                        <Link href="/licensing" className="hover:text-white transition-colors">Licensing</Link>
                    </div>
                </div>
                <div className="max-w-7xl mx-auto mt-6 text-[9px] text-white/20 text-center leading-relaxed">
                    Customer Service: (877) 976-5669 | 16501 Ventura Blvd Ste 400, Encino, CA 91436 | CalBRE # 02018146 | NMLS # 1556995 <br />
                    All information in this site is deemed reliable but is not guaranteed and is subject to change.
                </div>
            </div>
        </footer>
    );
}
