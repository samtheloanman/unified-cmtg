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

    const currentYear = new Date().getFullYear();

    return (
        <footer className="bg-slate-900 text-white border-t border-slate-800">
            {/* Main Footer Content */}
            <div className="max-w-7xl mx-auto py-16 px-6">
                <div className="grid md:grid-cols-4 gap-12">

                    {/* Brand Column */}
                    <div className="col-span-1 md:col-span-1">
                        <h3 className="text-3xl font-heading mb-6 tracking-wide bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
                            {siteConfig?.site_name || 'CUSTOM MORTGAGE'}
                        </h3>
                        <p className="text-slate-400 text-sm leading-relaxed mb-6">
                            Nationwide Mortgage Lender for Commercial and Residential properties.
                            Specializing in Non-QM, Bridge, Hard Money, and innovative financing solutions.
                        </p>
                        <div className="flex gap-4">
                            {/* Social Icons placeholders if URL exists */}
                            {siteConfig?.linkedin && <a href={siteConfig.linkedin} className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center hover:bg-[var(--primary)] transition-colors">in</a>}
                            {siteConfig?.facebook && <a href={siteConfig.facebook} className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center hover:bg-[var(--primary)] transition-colors">fb</a>}
                            {siteConfig?.instagram && <a href={siteConfig.instagram} className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center hover:bg-[var(--primary)] transition-colors">ig</a>}
                        </div>
                    </div>

                    {/* Navigation Columns (Dynamic) */}
                    {Object.keys(footerMenu?.items || {}).length > 0 ? (
                        /* If dynamic menu items exist, we try to map them. 
                           For footer we might expect sub_menus to be columns */
                        footerMenu?.items.map((item) => {
                            if (item.type === 'sub_menu') {
                                return (
                                    <div key={item.id}>
                                        <h4 className="text-lg font-heading text-white mb-6 uppercase tracking-wider border-b border-slate-800 pb-2 inline-block">
                                            {item.value.title}
                                        </h4>
                                        <ul className="space-y-3 text-sm text-slate-400">
                                            {item.value.items?.map((subItem, idx) => (
                                                <li key={idx}>
                                                    <Link
                                                        href={subItem.link_url || '#'}
                                                        target={subItem.open_in_new_tab ? '_blank' : undefined}
                                                        className="hover:text-[var(--primary)] transition-colors flex items-center gap-2 group"
                                                    >
                                                        <span className="w-1 h-1 rounded-full bg-slate-600 group-hover:bg-[var(--primary)] transition-colors"></span>
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
                                <h4 className="text-lg font-heading mb-6 uppercase tracking-wider">Quick Links</h4>
                                <ul className="space-y-3 text-sm text-slate-400">
                                    <li><Link href="/programs" className="hover:text-[var(--primary)]">Loan Programs</Link></li>
                                    <li><Link href="/funded-loans" className="hover:text-[var(--primary)]">Recently Funded</Link></li>
                                    <li><Link href="/quote" className="hover:text-[var(--primary)]">Get a Quote</Link></li>
                                </ul>
                            </div>
                            <div>
                                <h4 className="text-lg font-heading mb-6 uppercase tracking-wider">Loan Types</h4>
                                <ul className="space-y-3 text-sm text-slate-400">
                                    <li><Link href="/programs/residential" className="hover:text-[var(--primary)]">Residential</Link></li>
                                    <li><Link href="/programs/commercial" className="hover:text-[var(--primary)]">Commercial</Link></li>
                                    <li><Link href="/programs/hard-money" className="hover:text-[var(--primary)]">Hard Money</Link></li>
                                </ul>
                            </div>
                        </>
                    )}

                    {/* Contact Info */}
                    <div>
                        <h4 className="text-lg font-heading mb-6 uppercase tracking-wider">Contact Us</h4>
                        <ul className="space-y-4 text-sm text-slate-400">
                            {siteConfig?.phone_number && (
                                <li className="flex items-start gap-3">
                                    <span className="text-[var(--primary)]">📞</span>
                                    <a href={`tel:${siteConfig.phone_number}`} className="hover:text-white transition-colors">{siteConfig.phone_number}</a>
                                </li>
                            )}
                            {siteConfig?.email && (
                                <li className="flex items-start gap-3">
                                    <span className="text-[var(--primary)]">📧</span>
                                    <a href={`mailto:${siteConfig.email}`} className="hover:text-white transition-colors">{siteConfig.email}</a>
                                </li>
                            )}
                            {siteConfig?.address && (
                                <li className="flex items-start gap-3">
                                    <span className="text-[var(--primary)]">📍</span>
                                    <span className="whitespace-pre-line">{siteConfig.address}</span>
                                </li>
                            )}
                        </ul>
                    </div>
                </div>
            </div>

            {/* Bottom Bar */}
            <div className="border-t border-slate-800 bg-slate-950/50">
                <div className="max-w-7xl mx-auto py-6 px-6 flex flex-col md:flex-row justify-between items-center gap-4 text-xs text-slate-500">
                    <p>
                        © {currentYear} {siteConfig?.site_name || 'Custom Mortgage Inc.'} | All Rights Reserved.
                    </p>
                    <div className="flex gap-6">
                        <Link href="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link>
                        <Link href="/terms" className="hover:text-white transition-colors">Terms of Service</Link>
                        <Link href="/disclosures" className="hover:text-white transition-colors">Disclosures</Link>
                    </div>
                </div>
            </div>
        </footer>
    );
}
