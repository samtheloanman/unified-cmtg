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
                    apiClient.cms.getNavigation('Footer') // Assuming "Footer" menu exists
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
        <footer className="bg-[#1c4b57] text-white border-t border-[#133740]">
            {/* Main Footer Content */}
            <div className="max-w-7xl mx-auto py-16 px-6">
                <div className="grid md:grid-cols-4 gap-12 text-center md:text-left">

                    {/* Brand Column */}
                    <div className="col-span-1 md:col-span-1">
                        <Link href="/" className="inline-block mb-6">
                            {siteConfig?.logo_url ? (
                                <img src={siteConfig.logo_url} alt={siteConfig.site_name} className="h-12 w-auto object-contain brightness-0 invert" />
                            ) : (
                                <span className="text-3xl font-heading font-bold tracking-wide text-white">
                                    CM+RE
                                </span>
                            )}
                        </Link>

                        <p className="text-white/80 text-sm leading-relaxed mb-6 font-headings">
                            A fintech real estate and finance agency for individuals and businesses.
                            <br /><br />
                            Residential • Commercial
                        </p>
                        <div className="flex gap-4 justify-center md:justify-start">
                            {siteConfig?.linkedin && <a href={siteConfig.linkedin} className="w-10 h-10 rounded-full bg-white text-[#1c4b57] flex items-center justify-center hover:bg-[#1daed4] hover:text-white transition-colors">in</a>}
                            {siteConfig?.facebook && <a href={siteConfig.facebook} className="w-10 h-10 rounded-full bg-white text-[#1c4b57] flex items-center justify-center hover:bg-[#1daed4] hover:text-white transition-colors">fb</a>}
                            {siteConfig?.instagram && <a href={siteConfig.instagram} className="w-10 h-10 rounded-full bg-white text-[#1c4b57] flex items-center justify-center hover:bg-[#1daed4] hover:text-white transition-colors">ig</a>}
                        </div>
                    </div>

                    {/* Navigation Columns (Dynamic) */}
                    {Object.keys(footerMenu?.items || {}).length > 0 ? (
                        footerMenu?.items.map((item) => {
                            if (item.type === 'sub_menu') {
                                return (
                                    <div key={item.id}>
                                        <h4 className="text-lg font-heading font-bold text-white mb-6 uppercase tracking-wider">
                                            {item.value.title}
                                        </h4>
                                        <ul className="space-y-3 text-sm text-white/80">
                                            {item.value.items?.map((subItem, idx) => (
                                                <li key={idx}>
                                                    <Link
                                                        href={subItem.link_url || '#'}
                                                        target={subItem.open_in_new_tab ? '_blank' : undefined}
                                                        className="hover:text-[#1daed4] transition-colors"
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
                        /* Fallback Static Columns if no menu found yet */
                        <>
                            <div>
                                <h4 className="text-xl font-heading font-bold mb-6 uppercase tracking-wider">Quick Links</h4>
                                <ul className="space-y-3 text-base text-white/90">
                                    <li><Link href="/programs" className="hover:text-[#1daed4]">Loan Programs</Link></li>
                                    <li><Link href="/funded-loans" className="hover:text-[#1daed4]">Recently Funded</Link></li>
                                    <li><Link href="/quote" className="hover:text-[#1daed4]">Get a Quote</Link></li>
                                </ul>
                            </div>
                            <div>
                                <h4 className="text-xl font-heading font-bold mb-6 uppercase tracking-wider">Info</h4>
                                <ul className="space-y-3 text-base text-white/90">
                                    <li><Link href="/disclaimer" className="hover:text-[#1daed4]">Disclaimer</Link></li>
                                    <li><Link href="/support" className="hover:text-[#1daed4]">Support</Link></li>
                                    <li><Link href="/privacy" className="hover:text-[#1daed4]">Privacy Policy</Link></li>
                                </ul>
                            </div>
                        </>
                    )}

                    {/* Contact Info */}
                    <div>
                        <h4 className="text-xl font-heading font-bold mb-6 uppercase tracking-wider">Contact</h4>
                        <ul className="space-y-4 text-base text-white/90">
                            {siteConfig?.address && (
                                <li className="flex items-start gap-3 justify-center md:justify-start">
                                    <span className="text-[#1daed4]">📍</span>
                                    <span className="whitespace-pre-line text-left">{siteConfig.address}</span>
                                </li>
                            )}
                            {siteConfig?.phone_number && (
                                <li className="flex items-start gap-3 justify-center md:justify-start">
                                    <span className="text-[#1daed4]">📞</span>
                                    <a href={`tel:${siteConfig.phone_number}`} className="hover:text-white transition-colors">{siteConfig.phone_number}</a>
                                </li>
                            )}
                            <li className="flex items-start gap-3 justify-center md:justify-start">
                                <span className="text-[#1daed4]">🕒</span>
                                <span>Monday - Friday:<br />9:00 AM - 9:00 PM PST</span>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>

            {/* Bottom Bar - Legal */}
            <div className="bg-[#133740] py-8 px-6">
                <div className="max-w-7xl mx-auto text-xs text-white/60 text-center space-y-4">
                    <p className="font-bold italic">
                        COPYRIGHT © 2001-{currentYear} CUSTOM MTG INC DBA CUSTOM MORTGAGE AND REAL ESTATE -- ** ALL INFORMATION IN THIS SITE IS DEEMED RELIABLE BUT IS NOT GUARANTEED AND IS SUBJECT TO CHANGE.
                    </p>
                    <p>
                        Custom MTG Inc is not responsible for any errors or omissions in the information provided.
                    </p>
                    <div className="pt-4 border-t border-white/10 mt-4">
                        <p className="uppercase tracking-wider font-bold">
                            CUSTOM MTG INC., 16501 VENTURA BLVD STE 400, ENCINO, CA 91436 <br />
                            CALBRE # 02018146 - NMLS # 1556995
                        </p>
                    </div>
                    <p className="text-[10px] opacity-50">
                        COMMERCIAL AND HARD MONEY LOANS AVAILABLE NATIONWIDE
                    </p>
                </div>
            </div>
        </footer>
    );
}
