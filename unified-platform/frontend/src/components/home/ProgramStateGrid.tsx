'use client';

import { useState } from 'react';
import { PROGRAM_AVAILABILITY_DATA } from './ProgramStateData';
import { ScrollReveal } from '../ui/ScrollReveal';

export default function ProgramStateGrid() {
    const [searchTerm, setSearchTerm] = useState('');

    const filteredData = PROGRAM_AVAILABILITY_DATA.filter((item) =>
        item.state.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <section className="py-20 px-6 bg-gray-50 border-b border-gray-200">
            <div className="max-w-7xl mx-auto">
                <ScrollReveal>
                    <div className="text-center mb-12">
                        {/* Map Icon Placeholder */}
                        <div className="mx-auto w-24 h-24 mb-6 relative">
                            <span className="text-6xl">🗺️</span>
                            <span className="absolute -bottom-2 -right-2 text-4xl">📍</span>
                        </div>

                        <h2 className="text-4xl md:text-5xl font-black text-[#0f2933] uppercase tracking-tighter mb-4 font-heading">
                            All Programs Types By State
                        </h2>
                    </div>
                </ScrollReveal>

                <ScrollReveal delay={100}>
                    {/* Search Bar */}
                    <div className="my-8 flex justify-center">
                        <input
                            type="text"
                            placeholder="SEARCH TERRITORIES"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full max-w-md px-4 py-2 border-2 border-gray-400 rounded-lg text-center font-bold text-gray-600 focus:outline-none focus:border-[#1daed4] uppercase tracking-wide placeholder-gray-400 transition-colors"
                        />
                    </div>

                    <div className="overflow-x-auto shadow-sm border border-gray-200 bg-white">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="bg-[#1daed4] text-white uppercase text-xs tracking-wider">
                                    <th className="p-4 font-bold border-r border-white/20 w-1/5">State</th>
                                    <th className="p-4 font-bold border-r border-white/20 w-1/5">Commercial</th>
                                    <th className="p-4 font-bold border-r border-white/20 w-1/5">Hard Money</th>
                                    <th className="p-4 font-bold border-r border-white/20 w-1/5">Business Purpose</th>
                                    <th className="p-4 font-bold w-1/5">Conventional</th>
                                </tr>
                            </thead>
                            <tbody className="text-sm font-bold text-gray-700">
                                {filteredData.map((row, idx) => (
                                    <tr key={row.state} className="border-b border-gray-100 hover:bg-gray-50 transition-colors group">
                                        <td className="p-4 border-r border-gray-100 group-hover:text-[#1daed4]">{row.state}</td>
                                        <td className="p-4 border-r border-gray-100">
                                            {row.commercial ? 'AVAILABLE' : ''}
                                        </td>
                                        <td className="p-4 border-r border-gray-100">
                                            {row.hardMoney ? 'AVAILABLE' : ''}
                                        </td>
                                        <td className="p-4 border-r border-gray-100">
                                            {row.businessPurpose ? 'AVAILABLE' : ''}
                                        </td>
                                        <td className="p-4">
                                            {row.conventional ? 'AVAILABLE' : ''}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                        {filteredData.length === 0 && (
                            <div className="p-8 text-center text-gray-500 font-mono">
                                NO STATES FOUND MATCHING "{searchTerm}"
                            </div>
                        )}
                    </div>

                    {/* Pagination Placeholder */}
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
