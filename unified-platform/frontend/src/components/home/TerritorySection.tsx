'use client';

import { useState } from 'react';
import { TERRITORY_DATA } from './TerritoryData';
import { ScrollReveal } from '../ui/ScrollReveal';

export default function TerritorySection() {
    const [searchTerm, setSearchTerm] = useState('');

    const filteredData = TERRITORY_DATA.filter((item) =>
        Object.values(item).some((val) =>
            val.toLowerCase().includes(searchTerm.toLowerCase())
        )
    );

    return (
        <section className="py-20 px-6 bg-white border-b border-gray-100">
            <div className="max-w-7xl mx-auto">
                <ScrollReveal>
                    <div className="text-center mb-12">
                        {/* Map Icon Placeholder to match screenshot style */}
                        <div className="mx-auto w-24 h-24 mb-6 relative">
                            <span className="text-6xl">🗺️</span>
                            <span className="absolute -bottom-2 -right-2 text-4xl">🔍</span>
                        </div>

                        <h2 className="text-4xl md:text-5xl font-black text-[#0f2933] uppercase tracking-tighter mb-4 font-heading">
                            Hard Money & Commercial Lending Territories
                        </h2>
                    </div>
                </ScrollReveal>

                {/* Search Bar - Sharp & Technical */}
                <ScrollReveal delay={100}>
                    <div className="mb-0 overflow-hidden">
                        <div className="bg-[#1daed4] p-0">
                            <div className="grid grid-cols-3 divide-x divide-white/20 text-white font-bold text-sm tracking-widest uppercase">
                                <div className="p-4 bg-[#1daed4]">State</div>
                                <div className="p-4 bg-[#1daed4]">City</div>
                                <div className="p-4 bg-[#1daed4]">County</div>
                            </div>
                        </div>
                    </div>
                </ScrollReveal>

                <ScrollReveal delay={200}>
                    <div className="my-8 flex justify-center">
                        <input
                            type="text"
                            placeholder="SEARCH TERRITORIES"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full max-w-md px-4 py-2 border-2 border-gray-400 rounded-lg text-center font-bold text-gray-600 focus:outline-none focus:border-[#1daed4] uppercase tracking-wide placeholder-gray-400 transition-colors"
                        />
                    </div>

                    <div className="border border-gray-200 shadow-sm">
                        {/* Table Header (Hidden visually but kept for structure if needed, or matched to screenshot where header is blue bar above search) 
                            Actually screenshot shows Blue Header -> Search Bar -> Data. 
                            Let's adjust: Blue Data Header -> Search -> Data Rows 
                        */}

                        <div className="divide-y divide-gray-100">
                            {filteredData.length > 0 ? (
                                filteredData.map((item, idx) => (
                                    <div
                                        key={idx}
                                        className="grid grid-cols-3 divide-x divide-gray-100 hover:bg-gray-50 transition-colors group"
                                    >
                                        <div className="p-4 text-sm font-bold text-gray-700 group-hover:text-[#1daed4] transition-colors">{item.state}</div>
                                        <div className="p-4 text-sm font-bold text-gray-600">{item.city}</div>
                                        <div className="p-4 text-sm font-bold text-gray-600">{item.county}</div>
                                    </div>
                                ))
                            ) : (
                                <div className="p-8 text-center text-gray-500 font-mono">
                                    NO TERRITORIES FOUND MATCHING "{searchTerm}"
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Pagination Placeholder (Visual only for now) */}
                    <div className="mt-6">
                        <div className="inline-flex border border-gray-300 rounded px-4 py-2 bg-white text-gray-600 font-bold">
                            1 <span className="ml-2 text-gray-400">▼</span>
                        </div>
                    </div>
                </ScrollReveal>
            </div>
        </section>
    );
}
