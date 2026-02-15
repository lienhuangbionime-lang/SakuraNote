'use client';

import { useEffect } from 'react';
import { AlertCircle, RotateCcw } from 'lucide-react';

export default function Error({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    useEffect(() => {
        // Log the error to an error reporting service
        console.error("Next.js App Error:", error);
    }, [error]);

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-slate-50 text-slate-900 p-6">
            <div className="bg-white p-8 rounded-3xl shadow-xl border border-slate-200 text-center max-w-md w-full">
                <div className="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-6">
                    <AlertCircle className="w-8 h-8 text-red-500" />
                </div>
                <h2 className="text-2xl font-black text-slate-800 mb-2">System Malfunction</h2>
                <p className="text-slate-500 mb-6 text-sm leading-relaxed font-mono bg-slate-50 p-3 rounded-xl overflow-auto max-h-32 border border-slate-100">
                    {error.message || "Unknown Error"}
                </p>
                <button
                    onClick={() => reset()}
                    className="w-full px-6 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-colors font-bold flex items-center justify-center gap-2"
                >
                    <RotateCcw size={18} /> Reboot Module
                </button>
            </div>
        </div>
    );
}
