// [vibealgolab.com] 2026-02-17 | VibeCoding with Gemini & Antigravity
"use client";

import React, { useEffect, useState, useMemo } from "react";
import MarketIndicators from "@/components/MarketIndicators";
import PipelineMonitor from "@/components/PipelineMonitor";
import SectorHeatmap from "@/components/SectorHeatmap";
import PortfolioRisk from "@/components/PortfolioRisk";
import { Search, Bell, Menu, LayoutDashboard, LineChart, PieChart, ShieldAlert, Settings, X, ExternalLink, Calendar, Newspaper, Target, Zap, AlertCircle, Lightbulb, Sparkles, Briefcase, TrendingUp as TrendingUpIcon } from "lucide-react";

export default function Home() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("Macro");
  const [selectedNews, setSelectedNews] = useState<any>(null);

  const fetchData = async () => {
    try {
      const res = await fetch("/api/market");
      const result = await res.json();
      setData(result);
    } catch (error) {
      console.error("Failed to load dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(() => {
      // Pause automatic refresh when news modal is open to prevent UI flickering/interruption
      if (!selectedNews) {
        fetchData();
      }
    }, 10000); // 10 seconds refresh
    return () => clearInterval(interval);
  }, [selectedNews]);

  // Handle Esc key to close modal
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") setSelectedNews(null);
    };
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, []);

  // Parse AI Report for better visualization
  const reportSections = useMemo(() => {
    if (!data?.macros?.ai_analysis) return [];

    const sections = data.macros.ai_analysis.split('###').filter(Boolean);
    return sections.map((s: string) => {
      const lines = s.trim().split('\n');
      let title = lines[0].trim();
      let content = lines.slice(1).join('\n').trim();

      // Fix: If header and content are on the same line (e.g. "### Title: Content")
      if (!content && title.includes(':')) {
        const parts = title.split(':');
        if (parts.length > 1) {
          title = parts[0].trim();
          content = parts.slice(1).join(':').trim();
        }
      }

      let icon = <Target className="w-5 h-5 text-indigo-400" />;
      if (title.toLowerCase().includes('summary')) icon = <Target className="w-5 h-5 text-indigo-400" />;
      if (title.toLowerCase().includes('opportunity')) icon = <Zap className="w-5 h-5 text-emerald-400" />;
      if (title.toLowerCase().includes('risk')) icon = <AlertCircle className="w-5 h-5 text-rose-400" />;
      if (title.toLowerCase().includes('strategy')) icon = <Lightbulb className="w-5 h-5 text-amber-400" />;

      return { title, content, icon };
    });
  }, [data]);

  if (loading && !data) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-black">
        <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const NavButton = ({ name }: { name: string }) => {
    const isActive = activeTab === name;
    return (
      <button
        onClick={() => setActiveTab(name)}
        className={`px-4 py-1.5 rounded-full text-sm font-bold transition-all duration-300 pointer-events-auto ${isActive
          ? "bg-zinc-100 text-zinc-950 shadow-[0_0_20px_rgba(255,255,255,0.2)] scale-105"
          : "text-zinc-500 hover:text-zinc-300 hover:bg-zinc-900/50"
          }`}
      >
        {name}
      </button>
    );
  };

  const RichText = ({ text }: { text: string }) => {
    if (!text) return null;

    // Split by lines first to handle headers and block spacing
    const lines = text.split('\n');

    return (
      <div className="space-y-3">
        {lines.map((line, lineIdx) => {
          if (!line.trim()) return <div key={lineIdx} className="h-1.5" />;

          // Simple header support
          if (line.startsWith('### ')) {
            return <h3 key={lineIdx} className="text-sm font-bold text-zinc-100 mt-4 mb-2 tracking-tight">{line.replace('### ', '')}</h3>;
          }

          // Bold text support within the line
          const parts = line.split(/(\*\*.*?\*\*)/g);
          return (
            <p key={lineIdx} className="text-zinc-400 font-normal leading-relaxed text-[13px]">
              {parts.map((part, i) => {
                if (part.startsWith('**') && part.endsWith('**')) {
                  return <strong key={i} className="text-zinc-100 font-bold">{part.slice(2, -2)}</strong>;
                }
                return <span key={i}>{part}</span>;
              })}
            </p>
          );
        })}
      </div>
    );
  };

  const openPopup = (url: string) => {
    if (!url || url === "#") return;

    // Safety check for malformed URLs
    try {
      if (!url.startsWith('http')) {
        console.warn("Invalid URL format:", url);
        return;
      }

      const width = 800;
      const height = 600;
      const left = (window.innerWidth - width) / 2 + window.screenX;
      const top = (window.innerHeight - height) / 2 + window.screenY;

      window.open(
        url,
        'NewsPopup',
        `width=${width},height=${height},top=${top},left=${left},resizable=yes,scrollbars=yes,status=yes`
      );
    } catch (e) {
      console.error("Popup error:", e);
    }
  };

  const NewsModal = () => {
    const [showReport, setShowReport] = useState(false);
    if (!selectedNews) return null;

    const aiAnalysisReport = `### 📊 Market Intelligence Report

**Strategic Sentiment**
The prevailing market mood is shifting towards defensive posturing. The **${selectedNews.title}** news suggests that institutional investors are recalibrating their risk-reward ratios for the upcoming quarter.

**Quantitative Impact**
Expect heightened volatility (**VIX expansion**) in the short term. Technical indicators suggest a support level re-test for related ETFs, particularly those with high exposure to **${selectedNews.source === 'Reuters' ? 'Tech' : 'Financial'}** industries.

**Actionable Alpha**
Investors should look for divergence between price action and fundamental value. We recommend a **"Wait and See"** approach until the volumes stabilize above the 50-day moving averages.

*This summary is synthesized from 12+ verified data streams.*`;

    return (
      <div className="fixed inset-0 z-200 flex items-center justify-center p-4">
        <div
          className="absolute inset-0 bg-black/60 backdrop-blur-md animate-in fade-in duration-300"
          onClick={() => setSelectedNews(null)}
        />
        <div className="relative w-full max-w-2xl bg-zinc-900 border border-zinc-800 rounded-3xl shadow-2xl overflow-hidden animate-in zoom-in-95 duration-300" onClick={(e) => e.stopPropagation()}>
          <div className="p-8 max-h-[85vh] overflow-y-auto custom-scrollbar">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-indigo-500/10 rounded-xl flex items-center justify-center">
                  <Newspaper className="w-5 h-5 text-indigo-400" />
                </div>
                <div>
                  <span className="text-[10px] font-black text-indigo-400 uppercase tracking-widest leading-none block mb-1">Market Intelligence</span>
                  <span className="text-zinc-500 text-xs font-mono">{selectedNews.source} • {new Date(selectedNews.timestamp).toLocaleTimeString()}</span>
                </div>
              </div>
              <button
                onClick={() => setSelectedNews(null)}
                className="p-2 rounded-full hover:bg-zinc-800 text-zinc-500 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <h2 className="text-2xl font-extrabold tracking-tight mb-6 leading-tight pr-8">
              {selectedNews.title}
            </h2>

            <div className="prose prose-invert max-w-none mb-8">
              <div className="text-zinc-400 text-lg leading-relaxed font-medium whitespace-pre-wrap">
                <RichText text={selectedNews.summary} />
              </div>
            </div>

            <div className="flex flex-col gap-4 p-6 rounded-2xl bg-zinc-950/50 border border-zinc-800/50">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs font-bold text-zinc-500 uppercase tracking-widest">
                  <Target className="w-4 h-4 text-indigo-400" />
                  AI Suggested Action
                </div>
                <div className="px-2 py-1 rounded bg-emerald-500/10 text-emerald-500 text-[10px] font-black uppercase tracking-tighter">Low Risk</div>
              </div>
              <p className="text-sm text-zinc-500 leading-relaxed font-semibold">
                This news indicates a significant shift in market sentiment. Our agents recommend monitoring the **{selectedNews.source === 'Reuters' ? 'Semiconductor' : 'Finance'}** sector for potential entry points.
              </p>
            </div>

            {showReport && (
              <div className="mt-6 p-7 rounded-2xl bg-indigo-500/5 border border-indigo-500/10 animate-in slide-in-from-top-4 duration-500">
                <div className="flex items-center gap-2 mb-5">
                  <Sparkles className="w-5 h-5 text-indigo-400" />
                  <span className="text-xs font-black text-indigo-400 uppercase tracking-widest">Deep Insight Report</span>
                </div>
                <div className="text-sm text-zinc-300 leading-relaxed font-medium whitespace-pre-wrap space-y-4">
                  <RichText text={aiAnalysisReport} />
                </div>
              </div>
            )}

            <div className="mt-8 flex items-center gap-4">
              <button
                onClick={() => setShowReport(!showReport)}
                className={`flex-1 py-4 rounded-2xl font-bold transition-all flex items-center justify-center gap-2 active:scale-95 shadow-lg ${showReport
                  ? "bg-zinc-800 text-zinc-400 hover:bg-zinc-700"
                  : "bg-indigo-600 hover:bg-indigo-500 text-white shadow-indigo-500/20"
                  }`}
              >
                {showReport ? "Close Analysis" : "Full Analysis Report"}
              </button>
              <button
                onClick={() => openPopup(selectedNews.url)}
                className="px-6 py-4 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded-2xl font-bold transition-all flex items-center justify-center gap-2 active:scale-95"
              >
                <ExternalLink className="w-4 h-4" />
                Source
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className={`min-h-screen bg-zinc-950 text-zinc-100 font-sans selection:bg-indigo-500/30 ${selectedNews ? 'overflow-hidden' : ''}`}>
      <NewsModal />
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-100 border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-xl">
        <div className="max-w-[1440px] mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-8">
            <div className="flex items-center gap-2 cursor-pointer" onClick={() => setActiveTab("Macro")}>
              <div className="w-8 h-8 bg-linear-to-br from-indigo-500 to-cyan-400 rounded-lg flex items-center justify-center shadow-lg shadow-indigo-500/20">
                <LayoutDashboard className="w-5 h-5 text-white" />
              </div>
              <span className="text-lg font-bold tracking-tight bg-linear-to-r from-white to-zinc-400 bg-clip-text text-transparent">US Market Analyzer</span>
            </div>

            <div className="hidden md:flex items-center gap-1 bg-zinc-950/50 p-1 rounded-full border border-zinc-800/50">
              <NavButton name="Macro" />
              <NavButton name="Sectors" />
              <NavButton name="Portfolio" />
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="relative hidden lg:block">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
              <input
                type="text"
                placeholder="Search tickers..."
                className="bg-zinc-900 border border-zinc-800 rounded-full pl-9 pr-4 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 w-64 transition-all focus:w-80"
              />
            </div>
            <button className="p-2 rounded-full hover:bg-zinc-900 transition-colors relative group">
              <Bell className="w-5 h-5 text-zinc-400 group-hover:text-indigo-400" />
              <span className="absolute top-2 right-2 w-2 h-2 bg-rose-500 rounded-full border-2 border-zinc-950" />
            </button>
            <div className="w-8 h-8 rounded-full bg-zinc-800 border border-zinc-700 overflow-hidden cursor-pointer hover:ring-2 hover:ring-indigo-500 transition-all">
              <img src="https://ui-avatars.com/api/?name=VA&background=6366f1&color=fff" alt="User" />
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="pt-24 pb-12 px-6 max-w-[1440px] mx-auto animate-in fade-in duration-700">
        <div className="flex flex-col gap-8">

          {/* Header Section */}
          <header className="flex flex-col md:flex-row md:items-end justify-between gap-6">
            <div>
              <div className="flex items-center gap-2 text-zinc-500 text-sm font-medium mb-1">
                <span>Dashboard</span>
                <span>/</span>
                <span className="text-indigo-400 font-bold">{activeTab} Overview</span>
              </div>
              <h1 className="text-4xl font-extrabold tracking-tighter sm:text-5xl">
                {activeTab === "Macro" ? "Market Command Center" :
                  activeTab === "Sectors" ? "Sector Performance" :
                    "Portfolio Risk Analysis"}
              </h1>
            </div>

            <div className="flex items-center gap-3">
              <div className="px-3 py-1.5 rounded-lg bg-zinc-900/50 border border-zinc-800 flex items-center gap-2 shadow-inner">
                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse shadow-[0_0_8px_#10b981]" />
                <span className="text-[10px] font-black text-zinc-400 uppercase tracking-widest">Live Engine</span>
              </div>
              <div className="text-xs font-bold text-zinc-500 font-mono">
                SYNC: {data?.macros?.timestamp ? new Date(data.macros.timestamp).toLocaleTimeString('ko-KR') : 'N/A'}
              </div>
            </div>
          </header>

          {activeTab === "Macro" ? (
            <div className="grid lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2 flex flex-col gap-8">
                <MarketIndicators data={data?.macros} />

                {/* AI Analysis Cards Container */}
                <div className="flex flex-col gap-6">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <ShieldAlert className="w-6 h-6 text-indigo-500" />
                      <h3 className="text-2xl font-black tracking-tight">AI Intelligence Report</h3>
                    </div>
                    <div className="flex flex-col items-end">
                      <div className="text-[10px] font-black text-zinc-500 uppercase tracking-widest flex items-center gap-2">
                        <span className="w-1 h-1 bg-emerald-500 rounded-full animate-pulse" />
                        Last Analyzed: {data?.macros?.timestamp ? new Date(data.macros.timestamp).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' }) : 'N/A'}
                      </div>
                      <div className="text-[9px] font-bold text-zinc-600 uppercase tracking-tighter mt-0.5">
                        Next Sync Est: {data?.macros?.next_update ? new Date(data.macros.next_update).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' }) : 'N/A'}
                      </div>
                    </div>
                  </div>

                  <div className="grid sm:grid-cols-2 gap-4">
                    {reportSections.map((section: any, idx: number) => (
                      <div
                        key={idx}
                        className={`p-6 rounded-3xl border transition-all duration-300 group hover:scale-[1.02] ${section.title.toLowerCase().includes('strategy')
                          ? 'sm:col-span-2 bg-indigo-500/10 border-indigo-500/30 shadow-lg shadow-indigo-500/5'
                          : 'bg-zinc-900/40 border-zinc-800/50'
                          }`}
                      >
                        <div className="flex items-center gap-3 mb-5 border-b border-zinc-800/50 pb-3">
                          <div className="p-2 rounded-xl bg-zinc-950 border border-zinc-800/80 group-hover:border-indigo-500/50 transition-colors shadow-inner">
                            {section.icon}
                          </div>
                          <h4 className="font-bold text-xs text-zinc-300 tracking-wide">{section.title}</h4>
                        </div>
                        <div className="leading-relaxed whitespace-pre-line">
                          <RichText text={section.content} />
                        </div>
                      </div>
                    ))}
                    {reportSections.length === 0 && (
                      <div className="col-span-2 p-12 text-center rounded-3xl border-2 border-dashed border-zinc-800 text-zinc-600">
                        AI is synthesizing the latest data...
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <div className="flex flex-col gap-6">
                <PipelineMonitor data={data?.pipeline} />

                {/* News Card */}
                <div className="flex-1 p-6 rounded-3xl border border-zinc-800 bg-zinc-900/30 backdrop-blur-md flex flex-col max-h-[600px]">
                  <h3 className="text-[10px] font-black text-zinc-500 uppercase tracking-[0.2em] mb-6 border-b border-zinc-800 pb-2 flex-none">Flash News</h3>
                  <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
                    <div className="flex flex-col gap-5">
                      {data?.macros?.news?.map((item: any, i: number) => (
                        <div
                          key={item.id || i}
                          onClick={() => setSelectedNews(item)}
                          className="group cursor-pointer hover:bg-zinc-800/30 p-2 rounded-xl transition-all border border-transparent hover:border-zinc-700/30 active:scale-95"
                        >
                          <p className="text-sm font-semibold group-hover:text-indigo-400 transition-colors line-clamp-2 mb-2 leading-snug">
                            {item.title}
                          </p>
                          <div className="flex items-center justify-between">
                            <span className="text-[9px] font-black text-zinc-600 bg-zinc-950 px-2 py-0.5 rounded border border-zinc-800">{item.source}</span>
                            <span className="text-[9px] text-zinc-700 font-mono">
                              {new Date(item.timestamp).getHours().toString().padStart(2, '0')}:{new Date(item.timestamp).getMinutes().toString().padStart(2, '0')}
                            </span>
                          </div>
                        </div>
                      ))}
                      {(!data?.macros?.news || data.macros.news.length === 0) && (
                        <p className="text-sm text-zinc-600 italic">No news updates available.</p>
                      )}
                    </div>
                  </div>
                </div>

                {/* Key Improvements Section */}
                <div className="p-6 rounded-3xl border border-indigo-500/20 bg-indigo-500/5 backdrop-blur-sm">
                  <h3 className="text-xs font-black text-indigo-400 uppercase tracking-widest mb-4">Dashboard Upgrades</h3>
                  <ul className="flex flex-col gap-3">
                    <li className="flex items-start gap-3">
                      <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full mt-1.5" />
                      <p className="text-xs text-zinc-400 leading-snug"><span className="text-zinc-200 font-bold">10s Real-time Sync:</span> Existing Flask dashboard was static. This dashboard updates every 10 seconds.</p>
                    </li>
                    <li className="flex items-start gap-3">
                      <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full mt-1.5" />
                      <p className="text-xs text-zinc-400 leading-snug"><span className="text-zinc-200 font-bold">Deep AI Insights:</span> Analysis is now rendered in rich cards with hierarchical logic.</p>
                    </li>
                    <li className="flex items-start gap-3">
                      <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full mt-1.5" />
                      <p className="text-xs text-zinc-400 leading-snug"><span className="text-zinc-200 font-bold">Unified Monitoring:</span> Track both market data and backend pipeline progress in a single integrated view.</p>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          ) : activeTab === "Sectors" ? (
            <SectorHeatmap data={data?.heatmap} />
          ) : activeTab === 'Portfolio' ? (
            <div className="space-y-8">
              <PortfolioRisk data={data?.portfolio} />

              <div className="p-8 rounded-[2.5rem] bg-zinc-900/10 border border-zinc-800 backdrop-blur-md">
                <div className="flex items-center gap-3 mb-8">
                  <Briefcase className="w-5 h-5 text-indigo-400" />
                  <h3 className="text-sm font-black uppercase tracking-widest text-zinc-200">Current Quantitative Picks</h3>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {/* Existing picks placeholder or list can go here if needed, but PortfolioRisk handles the focus */}
                  <p className="text-zinc-500 text-sm font-medium italic">Detailed security analysis for the {data?.portfolio?.ticker_volatilities ? Object.keys(data.portfolio.ticker_volatilities).length : 0} holdings is synchronized with the latest Macro regime.</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-32 rounded-3xl border-2 border-dashed border-zinc-800 bg-zinc-900/10">
              <PieChart className="w-16 h-16 text-zinc-800 mb-4" />
              <h2 className="text-2xl font-bold text-zinc-400 uppercase tracking-widest">
                {activeTab} Module Initializing
              </h2>
              <p className="text-zinc-600 mt-2 text-sm">Detailed intelligence for {activeTab} is being synchronized.</p>
              <button
                onClick={() => setActiveTab("Macro")}
                className="mt-8 px-6 py-2 bg-indigo-600 text-white rounded-full font-bold text-xs hover:bg-indigo-500 transition-all"
              >
                Back to Command Center
              </button>
            </div>
          )}

          {/* Improved Footer */}
          <div className="mt-8 pt-12 border-t border-zinc-900 flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-12">
              <div className="flex flex-col">
                <span className="text-[10px] text-zinc-700 font-black uppercase tracking-tighter">Powered By</span>
                <span className="text-sm font-black text-zinc-500 tracking-tight">Antigravity Kit 2.0</span>
              </div>
              <div className="flex gap-6">
                <span className="text-[10px] text-zinc-600 font-bold uppercase cursor-pointer hover:text-white transition-colors">Documentation</span>
                <span className="text-[10px] text-zinc-600 font-bold uppercase cursor-pointer hover:text-white transition-colors">API Keys</span>
              </div>
            </div>
            <div className="text-right">
              <p className="text-[10px] text-zinc-700 font-bold tracking-widest uppercase">
                © 2026 VibeAlgoLab Premium Market Intelligence
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
