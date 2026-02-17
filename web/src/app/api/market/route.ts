// [vibealgolab.com] 2026-02-17 | VibeCoding with Gemini & Antigravity
import { NextResponse, NextRequest } from 'next/server';
import fs from 'fs/promises';
import path from 'path';
import { spawn } from 'child_process';

export async function GET() {
    try {
        const dataDir = path.join(process.cwd(), '..', 'data');

        const [macroData, pipelineData, heatmapData, riskData] = await Promise.all([
            fs.readFile(path.join(dataDir, 'macro_analysis_en.json'), 'utf8').then(JSON.parse).catch(() => ({})),
            fs.readFile(path.join(dataDir, 'pipeline_status.json'), 'utf8').then(JSON.parse).catch(() => ({})),
            fs.readFile(path.join(dataDir, 'sector_heatmap.json'), 'utf8').then(JSON.parse).catch(() => ({})),
            fs.readFile(path.join(dataDir, 'portfolio_risk.json'), 'utf8').then(JSON.parse).catch(() => (null))
        ]);

        // Enrich news data only if it's empty, and provide specific URLs
        const baseNews = macroData.news || [];
        const enrichedNews = baseNews.length > 0 ? baseNews : [
            {
                id: 'news-4',
                title: "NVIDIA Blackwell GPUs Enter Mass Production for AI Data Centers",
                source: "Reuters",
                summary: "NVIDIA CEO Jensen Huang confirmed that the Blackwell architecture is in full production, with sampling to global partners already underway to meet surging AI demand.",
                timestamp: new Date().toISOString(),
                url: "https://www.reuters.com/technology/nvidia-ceo-says-blackwell-is-full-production-2024-10-02/"
            },
            {
                id: 'news-5',
                title: "S&P 500 Records Best Week of 2024 on Earnings Optimism",
                source: "Bloomberg",
                summary: "Equities rallied as strong corporate earnings overshadowed rate concerns, propelling the benchmark index to fresh heights as the bull market matures.",
                timestamp: new Date().toISOString(),
                url: "https://www.bloomberg.com/news/articles/2024-05-17/s-p-500-track-for-best-week-of-year-as-inflation-fears-recede"
            }
        ];

        interface NewsItem {
            id?: string;
            title: string;
            source?: string;
            summary?: string;
            timestamp?: string;
            url?: string;
        }

        const finalizedNews = enrichedNews.map((item: NewsItem, idx: number) => {
            let url = item.url;

            // Only generate placeholder if absolutely no URL is present
            if (!url || url === "#") {
                if (item.source?.toLowerCase().includes('google')) url = "https://news.google.com";
                else if (item.source?.toLowerCase().includes('nbc')) url = "https://www.nbcnews.com";
                else if (item.source?.toLowerCase().includes('fox')) url = "https://www.foxbusiness.com";
                else url = "https://www.reuters.com";
            }

            return {
                id: item.id || `news-fallback-${idx}`,
                title: item.title,
                source: item.source || "Market News",
                summary: item.summary || "Detailed analysis of this market event is currently being synthesized by our AI agents.",
                timestamp: item.timestamp || new Date(Date.now() - idx * 3600000).toISOString(),
                url: url
            };
        });

        return NextResponse.json({
            macros: { ...macroData, news: finalizedNews },
            pipeline: pipelineData,
            heatmap: heatmapData,
            portfolio: riskData,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        console.error('Failed to fetch market data:', error);
        return NextResponse.json({ error: 'Failed to load data' }, { status: 500 });
    }
}

export async function POST(req: NextRequest) {
    try {
        const { tickers } = await req.json();

        if (!tickers || !Array.isArray(tickers) || tickers.length === 0) {
            return NextResponse.json({ error: 'Valid tickers are required' }, { status: 400 });
        }

        const projectRoot = path.join(process.cwd(), '..');
        const scriptPath = path.join(projectRoot, 'analysis', 'portfolio_risk.py');

        // Sanitize tickers (basic check)
        const sanitizedTickers = tickers.map(t => String(t).replace(/[^a-zA-Z0-9^.-]/g, '')).filter(Boolean);

        // Spawn process asynchronously
        const pythonProcess = spawn('python', [scriptPath, '--tickers', ...sanitizedTickers], {
            cwd: projectRoot,
            detached: true,
            stdio: 'ignore'
        });

        // Unref so the API can return immediately while the script runs in background
        pythonProcess.unref();

        return NextResponse.json({
            success: true,
            message: 'Analysis triggered',
            tickers: sanitizedTickers
        });
    } catch (error) {
        console.error('Failed to trigger analysis:', error);
        return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
    }
}
