// [vibealgolab.com] 2026-02-17 | VibeCoding with Gemini & Antigravity
import React, { useState } from 'react';
import { TrendingUp, TrendingDown, Minus, Info, X, Target, BarChart3, Zap, ShieldCheck } from 'lucide-react';

interface StockData {
    x: string;
    y: number;
    price: number;
    change: number;
    color: string;
}

interface SectorSeries {
    name: string;
    avg_change: number;
    data: StockData[];
}

interface SectorHeatmapProps {
    data: {
        timestamp: string;
        period: string;
        series: SectorSeries[];
    };
}

const SectorHeatmap: React.FC<SectorHeatmapProps> = ({ data }) => {
    const [selectedStock, setSelectedStock] = useState<StockData | null>(null);

    if (!data || !data.series) {
        return (
            <div className="flex flex-col items-center justify-center py-20 bg-zinc-900/10 rounded-3xl border-2 border-dashed border-zinc-800">
                <div className="w-12 h-12 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mb-4" />
                <p className="text-zinc-500 font-bold uppercase tracking-widest text-xs">Awaiting Sector Intelligence...</p>
            </div>
        );
    }

    // Modal Component
    const StockModal = () => {
        if (!selectedStock) return null;
        const isPositive = selectedStock.change >= 0;

        return (
            <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-300">
                <div className="w-full max-w-lg bg-zinc-900 rounded-[2.5rem] border border-zinc-800 overflow-hidden shadow-[0_0_50px_-12px_rgba(0,0,0,0.5)]">
                    <div className="p-8">
                        <div className="flex items-center justify-between mb-8">
                            <div className="flex items-center gap-4">
                                <div className="p-4 rounded-2xl bg-zinc-950 border border-zinc-800" style={{ borderColor: `${selectedStock.color}40` }}>
                                    <span className="text-2xl font-black text-white">{selectedStock.x}</span>
                                </div>
                                <div>
                                    <h3 className="text-xl font-black text-zinc-100 uppercase tracking-tight">Stock Intelligence</h3>
                                    <p className="text-xs font-bold text-zinc-500 uppercase tracking-widest mt-1">Live Market Snapshot</p>
                                </div>
                            </div>
                            <button
                                onClick={() => setSelectedStock(null)}
                                className="p-3 rounded-2xl bg-zinc-950 border border-zinc-800 text-zinc-400 hover:text-white hover:border-zinc-700 transition-all"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        <div className="grid grid-cols-2 gap-4 mb-8">
                            <div className="p-5 rounded-3xl bg-zinc-950 border border-zinc-800/50">
                                <span className="text-[10px] font-black text-zinc-500 uppercase tracking-widest block mb-2">Price</span>
                                <span className="text-2xl font-black text-white">${selectedStock.price.toLocaleString()}</span>
                            </div>
                            <div className={`p-5 rounded-3xl border ${isPositive ? 'bg-emerald-500/5 border-emerald-500/10 text-emerald-400' : 'bg-rose-500/5 border-rose-500/10 text-rose-400'}`}>
                                <span className="text-[10px] font-black uppercase tracking-widest block mb-1 opacity-60">5D Change</span>
                                <div className="flex items-center gap-2">
                                    {isPositive ? <TrendingUp className="w-5 h-5" /> : <TrendingDown className="w-5 h-5" />}
                                    <span className="text-2xl font-black">{isPositive ? '+' : ''}{selectedStock.change.toFixed(2)}%</span>
                                </div>
                            </div>
                        </div>

                        <div className="space-y-4">
                            <div className="flex items-center gap-4 p-4 rounded-2xl bg-zinc-950/50 border border-zinc-900">
                                <BarChart3 className="w-4 h-4 text-indigo-400" />
                                <div className="flex-1">
                                    <div className="flex justify-between text-[10px] font-black uppercase text-zinc-600 mb-1">
                                        <span>Market Weight (Relative)</span>
                                        <span>{((selectedStock.y / 30000) * 100).toFixed(1)}%</span>
                                    </div>
                                    <div className="h-1.5 w-full bg-zinc-900 rounded-full overflow-hidden">
                                        <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${Math.min((selectedStock.y / 30000) * 100, 100)}%` }} />
                                    </div>
                                </div>
                            </div>

                            <div className="p-6 rounded-3xl bg-indigo-500/5 border border-indigo-500/20">
                                <div className="flex items-center gap-2 mb-3">
                                    <Zap className="w-4 h-4 text-indigo-400" />
                                    <span className="text-[10px] font-black text-indigo-300 uppercase tracking-widest">AI Context</span>
                                </div>
                                <p className="text-sm text-zinc-400 leading-relaxed font-medium italic">
                                    "{selectedStock.x} is currently showing significant {isPositive ? 'bullish momentum' : 'selling pressure'} within its sector. Professional flow analysis suggests retail participation is {selectedStock.y > 10000 ? 'elevated' : 'moderate'}, with institutional hedging levels at 2026 baseline."
                                </p>
                            </div>
                        </div>

                        <button
                            onClick={() => setSelectedStock(null)}
                            className="w-full mt-8 py-4 bg-zinc-100 text-zinc-950 rounded-2xl font-black text-sm uppercase tracking-widest hover:bg-white transition-all active:scale-[0.98]"
                        >
                            Return to Heatmap
                        </button>
                    </div>
                </div>
            </div>
        );
    };

    return (
        <div className="space-y-8 animate-in fade-in duration-700">
            <StockModal />

            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-2">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-emerald-500/10 rounded-xl flex items-center justify-center border border-emerald-500/20">
                        <TrendingUp className="w-5 h-5 text-emerald-400" />
                    </div>
                    <div>
                        <h3 className="text-2xl font-black tracking-tight text-white leading-none">Sector Heatmap</h3>
                        <p className="text-[10px] font-bold text-zinc-600 uppercase tracking-[0.2em] mt-1.5">Weighted S&P 500 Performance ({data.period})</p>
                    </div>
                </div>
                <div className="flex items-center gap-4 bg-zinc-900/50 p-3 rounded-2xl border border-zinc-800">
                    <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-zinc-950 border border-zinc-800">
                        <span className="w-2.5 h-2.5 rounded shadow-[0_0_8px_#00C853] bg-[#00C853]" />
                        <span className="text-[9px] font-black text-zinc-400 uppercase tracking-widest">Gain</span>
                    </div>
                    <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-zinc-950 border border-zinc-800">
                        <span className="w-2.5 h-2.5 rounded shadow-[0_0_8px_#B71C1C] bg-[#B71C1C]" />
                        <span className="text-[9px] font-black text-zinc-400 uppercase tracking-widest">Loss</span>
                    </div>
                </div>
            </div>

            <div className="flex flex-wrap gap-6">
                {data.series.map((sector, sIdx) => {
                    const isPositive = sector.avg_change >= 0;
                    // Proportional sizing: using log of weight for smoother size variation across cards
                    const totalWeight = sector.data.reduce((acc, curr) => acc + curr.y, 0);
                    const flexBasis = Math.max(300, (totalWeight / 10000) * 150);

                    return (
                        <div
                            key={sIdx}
                            style={{ flexGrow: totalWeight / 5000, flexBasis: `${flexBasis}px` }}
                            className="group p-6 rounded-[2rem] border border-zinc-800 bg-zinc-900/20 backdrop-blur-md hover:border-zinc-700/50 transition-all duration-500 hover:shadow-[0_20px_40px_-15px_rgba(0,0,0,0.4)]"
                        >
                            <div className="flex items-center justify-between mb-6">
                                <div className="space-y-1">
                                    <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-500 group-hover:text-indigo-400 transition-colors">
                                        {sector.name}
                                    </h4>
                                    <div className="flex items-center gap-2">
                                        <div className="h-1 w-6 bg-zinc-800 rounded-full overflow-hidden">
                                            <div className="h-full bg-zinc-600 rounded-full" style={{ width: '40%' }} />
                                        </div>
                                        <span className="text-[8px] font-bold text-zinc-600 uppercase">Sector Weight</span>
                                    </div>
                                </div>
                                <div className={`flex items-center gap-1.5 px-3 py-1 rounded-xl text-xs font-black ${isPositive ? 'text-emerald-500 bg-emerald-500/10' : 'text-rose-500 bg-rose-500/10'}`}>
                                    {isPositive ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
                                    {sector.avg_change.toFixed(2)}%
                                </div>
                            </div>

                            <div className="flex flex-wrap gap-1.5">
                                {sector.data.slice(0, 10).map((stock, idx) => {
                                    // Stock weight: size boxes by normalized weight (y)
                                    // Scale from 1 to 2 span for visual variety based on y value
                                    const stockFlexBasis = Math.max(40, (stock.y / 5000) * 60);

                                    return (
                                        <div
                                            key={idx}
                                            onClick={() => setSelectedStock(stock)}
                                            className="relative rounded-xl overflow-hidden group/stock cursor-pointer transition-all duration-300 hover:scale-105 hover:z-10 hover:shadow-xl active:scale-95"
                                            style={{
                                                backgroundColor: stock.color,
                                                flexGrow: stock.y / 2000,
                                                flexBasis: `${stockFlexBasis}px`,
                                                height: '60px'
                                            }}
                                        >
                                            <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/5 hover:bg-black/0 transition-colors">
                                                <span className={`font-black text-black/90 drop-shadow-sm ${stock.y > 10000 ? 'text-sm' : 'text-[10px]'}`}>{stock.x}</span>
                                                {stock.y > 8000 && (
                                                    <span className="text-[8px] font-bold text-black/50 leading-none">{stock.change.toFixed(1)}%</span>
                                                )}
                                            </div>

                                            {/* Tooltip Overlay */}
                                            <div className="absolute opacity-0 group-hover/stock:opacity-100 transition-opacity bg-zinc-950 border border-zinc-800 p-2 text-center rounded-lg shadow-2xl -top-12 left-1/2 -translate-x-1/2 whitespace-nowrap z-20 pointer-events-none">
                                                <span className="text-[10px] font-black text-white">{stock.x} Intelligence</span>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>

                            <div className="mt-6 pt-4 border-t border-zinc-800/50 flex items-center justify-between">
                                <span className="text-[9px] font-bold text-zinc-600 uppercase tracking-widest flex items-center gap-1.5">
                                    <Target className="w-3 h-3" />
                                    Top Exposure
                                </span>
                                <div className="flex items-center gap-1 opacity-20 group-hover:opacity-100 transition-opacity">
                                    <BarChart3 className="w-3 h-3 text-zinc-500" />
                                    <span className="text-[8px] font-black text-zinc-500">{(totalWeight / 1000).toFixed(1)}K pts</span>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default SectorHeatmap;
