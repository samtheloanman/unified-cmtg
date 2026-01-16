import Link from 'next/link';

export default function Footer() {
    return (
        <footer className="bg-[#636363] text-white">
            {/* Main Footer */}
            <div className="max-w-7xl mx-auto py-12 px-6">
                <div className="grid md:grid-cols-4 gap-8">
                    {/* Company Info */}
                    <div>
                        <h3 className="text-2xl font-bold mb-4" style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}>
                            CUSTOM MORTGAGE
                        </h3>
                        <p className="text-gray-300 text-sm mb-4">
                            Nationwide Mortgage Lender for Commercial and Residential properties.
                            Bridge, Hard Money, and Stated Income available.
                        </p>
                        <p className="text-[#1daed4] font-bold text-lg">
                            <a href="tel:8779765669">(877) 976-5669</a>
                        </p>
                    </div>

                    {/* Quick Links */}
                    <div>
                        <h4 className="text-lg font-bold mb-4" style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}>
                            Quick Links
                        </h4>
                        <ul className="space-y-2 text-gray-300 text-sm">
                            <li><Link href="/programs" className="hover:text-[#1daed4] transition-colors">Loan Programs</Link></li>
                            <li><Link href="/funded-loans" className="hover:text-[#1daed4] transition-colors">Recently Funded</Link></li>
                            <li><Link href="/blog" className="hover:text-[#1daed4] transition-colors">Blog & News</Link></li>
                            <li><Link href="/quote" className="hover:text-[#1daed4] transition-colors">Get a Quote</Link></li>
                            <li><a href="https://custommortgage.floify.com/" target="_blank" rel="noopener noreferrer" className="hover:text-[#1daed4] transition-colors">Apply Online</a></li>
                        </ul>
                    </div>

                    {/* Loan Types */}
                    <div>
                        <h4 className="text-lg font-bold mb-4" style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}>
                            Loan Types
                        </h4>
                        <ul className="space-y-2 text-gray-300 text-sm">
                            <li><Link href="/programs" className="hover:text-[#1daed4] transition-colors">Residential Loans</Link></li>
                            <li><Link href="/programs" className="hover:text-[#1daed4] transition-colors">Commercial Loans</Link></li>
                            <li><Link href="/programs" className="hover:text-[#1daed4] transition-colors">Hard Money Loans</Link></li>
                            <li><Link href="/programs" className="hover:text-[#1daed4] transition-colors">Stated Income / NonQM</Link></li>
                            <li><Link href="/programs" className="hover:text-[#1daed4] transition-colors">Fix & Flip</Link></li>
                        </ul>
                    </div>

                    {/* Contact */}
                    <div>
                        <h4 className="text-lg font-bold mb-4" style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}>
                            Contact Us
                        </h4>
                        <ul className="space-y-3 text-gray-300 text-sm">
                            <li className="flex items-start gap-2">
                                <span>📞</span>
                                <a href="tel:8779765669" className="hover:text-[#1daed4] transition-colors">(877) 976-5669</a>
                            </li>
                            <li className="flex items-start gap-2">
                                <span>📧</span>
                                <a href="mailto:info@c-mtg.com" className="hover:text-[#1daed4] transition-colors">info@c-mtg.com</a>
                            </li>
                            <li className="flex items-start gap-2">
                                <span>📍</span>
                                <span>16501 Ventura Blvd, STE 400<br />Encino, CA 91436</span>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>

            {/* Bottom Bar */}
            <div className="border-t border-gray-500">
                <div className="max-w-7xl mx-auto py-6 px-6 flex flex-col md:flex-row justify-between items-center gap-4">
                    <p className="text-gray-400 text-sm text-center md:text-left">
                        © {new Date().getFullYear()} Custom Mortgage Inc. | NMLS# 1583580 | DRE# 02122172
                    </p>
                    <div className="flex gap-6 text-sm text-gray-400">
                        <Link href="/blog" className="hover:text-[#1daed4] transition-colors">Privacy Policy</Link>
                        <Link href="/blog" className="hover:text-[#1daed4] transition-colors">Terms of Service</Link>
                        <Link href="/blog" className="hover:text-[#1daed4] transition-colors">Disclosures</Link>
                    </div>
                </div>
            </div>
        </footer>
    );
}
