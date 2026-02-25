'use client';

import { AlertTriangle, Power } from 'lucide-react';

export default function GlobalError({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    return (
        <html lang="en">
            <body className="bg-slate-950 text-slate-100 overflow-hidden">
                <div className="flex flex-col items-center justify-center min-h-screen p-6 relative overflow-hidden">

                    {/* Background Noise */}
                    <div className="absolute inset-0 opacity-10 pointer-events-none" style={{ backgroundImage: 'url("data:image/svg+xml,%3Csvg viewBox=\'0 0 200 200\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cfilter id=\'noiseFilter\'%3E%3CfeTurbulence type=\'fractalNoise\' baseFrequency=\'0.65\' numOctaves=\'3\' stitchTiles=\'stitch\'/%3E%3C/filter%3E%3Crect width=\'100%25\' height=\'100%25\' filter=\'url(%23noiseFilter)\'/%3E%3C/svg%3E")' }} />

                    <div className="relative z-10 text-center max-w-lg">
                        <AlertTriangle className="w-20 h-20 text-rose-500 mx-auto mb-6 animate-pulse" />
                        <h1 className="text-4xl font-black text-white mb-2 tracking-tighter">CRITICAL FAILURE</h1>
                        <p className="text-rose-400 font-mono text-xs uppercase tracking-widest mb-8">System Core Dumped</p>

                        <div className="bg-slate-900/50 backdrop-blur border border-rose-500/30 p-6 rounded-2xl mb-8 text-left">
                            <code className="text-rose-300 text-xs font-mono break-all">
                                {error.message}
                            </code>
                        </div>

                        <button
                            onClick={() => reset()}
                            className="group relative px-8 py-3 bg-rose-600 hover:bg-rose-500 text-white rounded-xl font-bold transition-all hover:scale-105 active:scale-95 flex items-center gap-2 mx-auto"
                        >
                            <Power className="w-5 h-5" />
                            <span>FORCE RESTART</span>
                            <div className="absolute inset-0 rounded-xl ring-2 ring-rose-400 opacity-0 group-hover:animate-ping" />
                        </button>
                    </div>
                </div>
            </body>
        </html>
    );
}
