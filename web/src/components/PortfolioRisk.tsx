// [vibealgolab.com] 2026-02-17 | VibeCoding with Gemini & Antigravity
import React, { useState, useEffect } from 'react';
import { ShieldAlert, TrendingDown, Gauge, BarChart3, AlertTriangle, ShieldCheck, Plus, X, Play, RefreshCw, Layers } from 'lucide-react';

interface RiskData {
    timestamp: string;
    portfolio_volatility_pct: number;
    high_correlations: Array<{
        tickers: string[];
        correlation: number;
    }>;
    diversification_status: string;
    ticker_volatilities: Record<string, number>;
    correlation_matrix: Record<string, Record<string, number>>;
}

export default function PortfolioRisk({ data }: { data: RiskData }) {
    const [customTickers, setCustomTickers] = useState<string[]>([]);
    const [newTicker, setNewTicker] = useState("");
    const [isAnalyzing, setIsAnalyzing] = useState(false);

    // Sync initial tickers from data if available
    useEffect(() => {
        if (data?.correlation_matrix && customTickers.length === 0) {
            setCustomTickers(Object.keys(data.correlation_matrix));
        }
    }, [data]);

    if (!data) return (
        <div className="p-20 flex flex-col items-center justify-center bg-zinc-900/10 rounded-[3rem] border-2 border-dashed border-zinc-800">
            <RefreshCw className="w-12 h-12 text-zinc-800 animate-spin mb-4" />
            <p className="text-zinc-500 font-bold uppercase tracking-widest text-xs">Waiting for Risk Intel...</p>
        </div>
    );

    const tickers = Object.keys(data.correlation_matrix);
    const isConcentrated = data.diversification_status === "Concentrated";

    const handleAddTicker = (e: React.FormEvent) => {
        e.preventDefault();
        const ticker = newTicker.trim().toUpperCase();
        if (ticker && !customTickers.includes(ticker)) {
            setCustomTickers([...customTickers, ticker]);
        }
        setNewTicker("");
    };

    const removeTicker = (ticker: string) => {
        setCustomTickers(customTickers.filter(t => t !== ticker));
    };

    const runAnalysis = async () => {
        if (customTickers.length === 0) return;
        setIsAnalyzing(true);
        try {
            const resp = await fetch('/api/market', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tickers: customTickers })
            });
            if (resp.ok) {
                // The pipeline status will update automatically via parent polling
                console.log("Analysis triggered successfully");
            }
        } catch (error) {
            console.error("Failed to trigger analysis", error);
        } finally {
            setTimeout(() => setIsAnalyzing(false), 2000);
        }
    };

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            {/* Interactive Ticker Manager */}
            <div className="p-8 rounded-[2.5rem] bg-zinc-950 border border-zinc-900 shadow-2xl">
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 mb-8">
                    <div>
                        <div className="flex items-center gap-3 mb-2">
                            <Layers className="w-5 h-5 text-indigo-400" />
                            <h3 className="text-xl font-black text-white uppercase tracking-tight">Portfolio Customization</h3>
                        </div>
                        <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Add or remove tickers to simulate custom risk profiles</p>
                    </div>

                    <div className="flex items-center gap-4">
                        <form onSubmit={handleAddTicker} className="relative flex-1 lg:w-64">
                            <input
                                type="text"
                                value={newTicker}
                                onChange={(e) => setNewTicker(e.target.value)}
                                placeholder="ENTER TICKER..."
                                className="w-full h-12 pl-4 pr-12 rounded-2xl bg-zinc-900 border border-zinc-800 text-xs font-black text-white focus:outline-none focus:border-indigo-500 transition-all placeholder:text-zinc-700"
                            />
                            <button type="submit" className="absolute right-2 top-2 w-8 h-8 bg-zinc-800 rounded-xl flex items-center justify-center hover:bg-zinc-700 transition-colors">
                                <Plus className="w-4 h-4 text-white" />
                            </button>
                        </form>

                        <button
                            onClick={runAnalysis}
                            disabled={isAnalyzing || customTickers.length === 0}
                            className={`h-12 px-6 rounded-2xl font-black text-[10px] uppercase tracking-widest flex items-center gap-3 transition-all ${isAnalyzing ? 'bg-zinc-800 text-zinc-500 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-500/20 active:scale-95'}`}
                        >
                            {isAnalyzing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-current" />}
                            {isAnalyzing ? 'Processing...' : 'Run Risk Analysis'}
                        </button>
                    </div>
                </div>

                <div className="flex flex-wrap gap-2">
                    {customTickers.map(t => (
                        <div key={t} className="group flex items-center gap-2 px-4 py-2 bg-zinc-900 border border-zinc-800 rounded-xl hover:border-zinc-700 transition-all">
                            <span className="text-xs font-black text-zinc-100">{t}</span>
                            <button
                                onClick={() => removeTicker(t)}
                                className="opacity-40 group-hover:opacity-100 hover:text-rose-500 transition-all"
                            >
                                <X className="w-3 h-3" />
                            </button>
                        </div>
                    ))}
                    {customTickers.length === 0 && (
                        <p className="text-sm font-medium text-zinc-600 italic">No tickers selected. Add symbols above to begin analysis.</p>
                    )}
                </div>
            </div>

            {/* Header / Scorecard */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="md:col-span-2 p-8 rounded-[2.5rem] bg-zinc-900/30 border border-zinc-800 backdrop-blur-md relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:opacity-20 transition-opacity">
                        <Gauge className="w-32 h-32 text-indigo-500" />
                    </div>

                    <div className="relative z-10">
                        <div className="flex items-center gap-3 mb-6">
                            <div className="w-10 h-10 bg-indigo-500/10 rounded-xl flex items-center justify-center border border-indigo-500/20">
                                <TrendingDown className="w-5 h-5 text-indigo-400" />
                            </div>
                            <h3 className="text-xl font-black tracking-tight text-white uppercase">Volatility Intelligence</h3>
                        </div>

                        <div className="flex items-end gap-6">
                            <div>
                                <span className="text-7xl font-black text-white tracking-tighter">
                                    {data.portfolio_volatility_pct}%
                                </span>
                                <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-[0.2em] mt-2">Annualized Portfolio Risk</p>
                            </div>
                            <div className="mb-4">
                                <span className={`px-4 py-2 rounded-2xl text-xs font-black uppercase tracking-widest ${isConcentrated ? 'bg-rose-500/10 text-rose-500' : 'bg-emerald-500/10 text-emerald-500'}`}>
                                    {data.diversification_status}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="p-8 rounded-[2.5rem] bg-zinc-900/30 border border-zinc-800 backdrop-blur-md flex flex-col justify-between">
                    <div>
                        <div className="flex items-center gap-3 mb-6">
                            <ShieldAlert className={`w-5 h-5 ${isConcentrated ? 'text-rose-500' : 'text-emerald-500'}`} />
                            <h4 className="text-xs font-black uppercase tracking-widest text-zinc-400">Risk Assessment</h4>
                        </div>
                        <p className="text-sm font-medium text-zinc-300 leading-relaxed italic">
                            {isConcentrated
                                ? "Portfolio shows high concentration. Consider rotating into non-correlated assets to improve Sharpe ratio."
                                : "Diversification profile is optimal. Current picks show resilient cross-correlation levels for 2026 volatility regimes."
                            }
                        </p>
                    </div>
                    <div className="mt-8 pt-6 border-t border-zinc-800 flex items-center justify-between">
                        <span className="text-[10px] font-black text-zinc-600 uppercase">System Status</span>
                        {isConcentrated ? <AlertTriangle className="w-4 h-4 text-rose-500" /> : <ShieldCheck className="w-4 h-4 text-emerald-500" />}
                    </div>
                </div>
            </div>

            {/* Correlation Matrix */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="p-8 rounded-[2.5rem] bg-zinc-900/10 border border-zinc-800/50">
                    <div className="flex items-center gap-3 mb-8">
                        <BarChart3 className="w-5 h-5 text-indigo-400" />
                        <h3 className="text-sm font-black uppercase tracking-widest text-zinc-200">Correlation Heatmap</h3>
                    </div>

                    <div className="overflow-x-auto">
                        <table className="w-full border-separate border-spacing-1">
                            <thead>
                                <tr>
                                    <th className="w-12 h-12"></th>
                                    {tickers.map(t => (
                                        <th key={t} className="w-12 h-12 text-[10px] font-black text-zinc-600 uppercase">{t}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {tickers.map(rowTicker => (
                                    <tr key={rowTicker}>
                                        <td className="w-12 h-12 text-[10px] font-black text-zinc-600 uppercase text-right pr-2">{rowTicker}</td>
                                        {tickers.map(colTicker => {
                                            const val = data.correlation_matrix[rowTicker][colTicker];
                                            const opacity = Math.abs(val);
                                            // More vibrant colors for better visibility
                                            const color = val > 0
                                                ? `rgba(99, 102, 241, ${Math.max(opacity, 0.1)})` // Indigo
                                                : `rgba(244, 63, 94, ${Math.max(opacity, 0.1)})`; // Rose

                                            return (
                                                <td
                                                    key={colTicker}
                                                    className="relative w-12 h-12 rounded-lg transition-transform hover:scale-110 hover:z-10 cursor-pointer group"
                                                    style={{ backgroundColor: color }}
                                                >
                                                    <span className={`flex items-center justify-center text-[10px] font-bold ${Math.abs(val) > 0.5 ? 'text-white' : 'text-zinc-500'}`}>
                                                        {val === 1 ? '—' : val.toFixed(2)}
                                                    </span>

                                                    {/* Custom Tooltip */}
                                                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 p-3 bg-zinc-950 border border-zinc-800 rounded-xl shadow-2xl opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-50">
                                                        <div className="flex items-center justify-between mb-1">
                                                            <div className="flex items-center gap-2">
                                                                <span className="text-xs font-black text-zinc-100">{rowTicker}</span>
                                                                <span className="text-[10px] text-zinc-500">vs</span>
                                                                <span className="text-xs font-black text-zinc-100">{colTicker}</span>
                                                            </div>
                                                        </div>
                                                        <div className="flex items-center justify-between">
                                                            <span className="text-[10px] font-bold text-zinc-500 uppercase">Correlation</span>
                                                            <span className={`text-sm font-black ${val > 0.7 ? 'text-indigo-400' : val < -0.3 ? 'text-rose-400' : 'text-zinc-300'}`}>
                                                                {val.toFixed(2)}
                                                            </span>
                                                        </div>
                                                        <p className="text-[9px] text-zinc-600 mt-2 leading-tight">
                                                            {val > 0.7 ? "Strong Positive Correlation. Prices tend to move together." :
                                                                val < -0.3 ? "Negative Correlation. Potential diversification benefit." :
                                                                    "Low Correlation. Independent price movements."}
                                                        </p>
                                                    </div>
                                                </td>
                                            );
                                        })}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Specific Risk Breakdown */}
                <div className="space-y-6">
                    <div className="p-8 rounded-[2.5rem] bg-zinc-950 border border-zinc-900">
                        <h4 className="text-[10px] font-black uppercase tracking-widest text-zinc-500 mb-6">High Correlation Alerts</h4>
                        <div className="space-y-3">
                            {data.high_correlations.length > 0 ? (
                                data.high_correlations.map((pair, idx) => (
                                    <div key={idx} className="flex items-center justify-between p-4 rounded-2xl bg-rose-500/5 border border-rose-500/10">
                                        <div className="flex items-center gap-3">
                                            <span className="text-xs font-black text-zinc-100">{pair.tickers[0]}</span>
                                            <div className="w-8 h-px bg-rose-500/30" />
                                            <span className="text-xs font-black text-zinc-100">{pair.tickers[1]}</span>
                                        </div>
                                        <span className="text-xs font-black text-rose-500">{pair.correlation}</span>
                                    </div>
                                ))
                            ) : (
                                <p className="text-xs font-bold text-zinc-600 italic">No significant concentration clusters detected.</p>
                            )}
                        </div>
                    </div>

                    <div className="p-8 rounded-[2.5rem] bg-zinc-900/20 border border-zinc-800">
                        <h4 className="text-[10px] font-black uppercase tracking-widest text-zinc-500 mb-6">Ticker Specific Volatility</h4>
                        <div className="space-y-4">
                            {Object.entries(data.ticker_volatilities)
                                .sort(([, a], [, b]) => b - a)
                                .map(([ticker, vol]) => (
                                    <div key={ticker} className="space-y-2">
                                        <div className="flex justify-between items-end">
                                            <span className="text-xs font-black text-zinc-200">{ticker}</span>
                                            <span className="text-[10px] font-bold text-zinc-500">{(vol * 100).toFixed(1)}% Vol</span>
                                        </div>
                                        <div className="h-1.5 w-full bg-zinc-950 rounded-full overflow-hidden">
                                            <div
                                                className="h-full bg-indigo-500/50 rounded-full"
                                                style={{ width: `${Math.min(vol * 200, 100)}%` }}
                                            />
                                        </div>
                                    </div>
                                ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
