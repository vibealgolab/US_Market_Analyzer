// [vibealgolab.com] 2026-02-17 | VibeCoding with Gemini & Antigravity
"use client";

import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface IndicatorProps {
    label: string;
    value: number;
    change: number;
}

const IndicatorCard = ({ label, value, change }: IndicatorProps) => {
    const isPositive = change > 0;
    const isNegative = change < 0;

    return (
        <div className="flex flex-col p-4 rounded-xl border border-zinc-200 bg-white/50 backdrop-blur-md dark:border-zinc-800 dark:bg-zinc-900/50 transition-all hover:ring-1 hover:ring-indigo-500">
            <span className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-1">{label}</span>
            <div className="flex items-end justify-between">
                <span className="text-xl font-bold text-zinc-900 dark:text-zinc-50">{value.toLocaleString()}</span>
                <div className={`flex items-center text-sm font-medium ${isPositive ? 'text-emerald-500' : isNegative ? 'text-rose-500' : 'text-zinc-400'}`}>
                    {isPositive ? <TrendingUp size={14} className="mr-1" /> : isNegative ? <TrendingDown size={14} className="mr-1" /> : <Minus size={14} className="mr-1" />}
                    {Math.abs(change).toFixed(2)}%
                </div>
            </div>
        </div>
    );
};

export default function MarketIndicators({ data }: { data: any }) {
    if (!data || !data.macro_indicators) return null;

    const indicators = data.macro_indicators;

    return (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 w-full">
            {Object.entries(indicators).map(([key, info]: [string, any]) => (
                <IndicatorCard
                    key={key}
                    label={key.replace('_', ' ')}
                    value={info.value}
                    change={info.change_1d}
                />
            ))}
        </div>
    );
}
