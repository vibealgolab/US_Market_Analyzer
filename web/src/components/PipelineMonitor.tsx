// [vibealgolab.com] 2026-02-17 | VibeCoding with Gemini & Antigravity
"use client";

import React from 'react';
import { Activity, Clock } from 'lucide-react';

export default function PipelineMonitor({ data }: { data: any }) {
    if (!data) return null;

    const progressStr = data.progress || "0%";
    let percentage = 0;

    // Handle [1/2] ratio format
    const ratioMatch = progressStr.match(/\[(\d+)\/(\d+)\]/);
    if (ratioMatch) {
        percentage = (parseInt(ratioMatch[1]) / parseInt(ratioMatch[2])) * 100;
    } else {
        // Handle "50%" percentage format
        const percentMatch = progressStr.match(/(\d+)%/);
        if (percentMatch) {
            percentage = parseInt(percentMatch[1]);
        }
    }

    const isCompleted = percentage === 100 || data.current_task === "Completed" || data.current_task === "Idle";

    return (
        <div className="w-full p-5 rounded-2xl bg-zinc-900 border border-zinc-800 overflow-hidden relative">
            <div className="flex items-center justify-between mb-4 relative z-10">
                <div className="flex items-center gap-2">
                    <Activity className={`w-5 h-5 ${isCompleted ? 'text-emerald-500' : 'text-indigo-500 animate-pulse'}`} />
                    <h3 className="text-sm font-bold text-zinc-100 uppercase tracking-widest">Pipeline Status</h3>
                </div>
                <div className="flex items-center gap-1.5 text-xs text-zinc-500 font-mono">
                    <Clock className="w-3 h-3" />
                    <span>{new Date(data.timestamp).toLocaleTimeString()}</span>
                </div>
            </div>

            <div className="relative z-10">
                <div className="flex justify-between items-end mb-2">
                    <span className="text-lg font-medium text-zinc-300 truncate max-w-[70%]">
                        {data.current_task || "Idle"}
                    </span>
                    <span className="text-2xl font-black text-white italic">{percentage.toFixed(0)}%</span>
                </div>

                <div className="h-2 w-full bg-zinc-800 rounded-full overflow-hidden">
                    <div
                        className={`h-full transition-all duration-1000 ease-out ${isCompleted ? 'bg-emerald-500' : 'bg-linear-to-r from-indigo-500 to-cyan-400'}`}
                        style={{ width: `${percentage}%` }}
                    />
                </div>

                {data.details && (
                    <p className="mt-3 text-xs text-zinc-500 font-medium">
                        → {data.details}
                    </p>
                )}
            </div>

            {/* Decorative gradient background */}
            {!isCompleted && (
                <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/10 blur-3xl -mr-16 -mt-16 rounded-full" />
            )}
        </div>
    );
}
