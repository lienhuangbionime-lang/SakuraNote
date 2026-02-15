'use client';

import React, { useState, useEffect } from 'react';
import { Menu, X, PenTool, Layers, List as ListIcon, Activity, Settings, LayoutTemplate, Zap, Clock, TrendingUp, Quote, Trash2, Clipboard, Link as LinkIcon } from 'lucide-react';

// Components
import { CaptureView } from '@/components/CaptureView';
import { NeuralGraph } from '@/components/NeuralGraph';
import { HistoryView } from '@/components/HistoryView';
import { SettingsView } from '@/components/SettingsView';
import { CardStackDashboard } from '@/components/CardStackDashboard';
import { Dock } from '@/components/Dock';
import { CommandPalette } from '@/components/CommandPalette';
import { ConfirmModal, ContextModal } from '@/components/Modals';
import { CreateProjectModal } from '@/components/CreateProjectModal';
import { ProjectBoard } from '@/components/ProjectBoard';
import { EntryDetailModal } from '@/components/EntryDetailModal';

export default function Home() {
  // 1. State Definition
  const [logs, setLogs] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<'capture' | 'graph' | 'list' | 'settings' | 'dashboard' | 'project'>('capture');
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isMounted, setIsMounted] = useState(false);
  const [isCmdOpen, setIsCmdOpen] = useState(false);
  const [isCreateProjectOpen, setIsCreateProjectOpen] = useState(false);

  // Modal States
  const [selectedEntry, setSelectedEntry] = useState<any>(null);
  const [contextNode, setContextNode] = useState<any>(null);
  const [confirmState, setConfirmState] = useState({ isOpen: false, title: '', message: '', action: null as any });

  // Mount effect
  useEffect(() => {
    setIsMounted(true);

    const loadMemories = async () => {
      try {
        const { cortex } = await import('@/lib/api/client');
        const rawLogs = await cortex.getRecentMemories(50);

        const mappedLogs = rawLogs.map((log: any) => ({
          ...log,
          note: log.content || '',
          metrics: {
            mood: log.mood || 5,
            focus: log.focus || 5,
            energy: log.energy || 5
          },
          habits: log.habits || {},
          tags: log.tags || log.meta?.tags || [],
          graphSeeds: log.meta?.graphSeeds || undefined
        }));

        setLogs(mappedLogs);
      } catch (e) {
        console.error("Failed to load memories", e);
      }
    };

    loadMemories();
  }, []);

  const requestDelete = (date: string) => {
    setConfirmState({
      isOpen: true,
      title: '刪除紀錄',
      message: `確定要刪除 ${date} 的紀錄嗎？`,
      action: () => {
        setLogs(prev => prev.filter(l => l.date !== date));
        setSelectedEntry(null);
        setConfirmState(prev => ({ ...prev, isOpen: false }));
      }
    });
  };

  // --- Render Helpers ---
  if (!isMounted) return <div className="h-screen bg-slate-950 flex flex-col gap-4 items-center justify-center font-mono"><div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div><div className="text-slate-400 text-xs tracking-widest uppercase">Initializing Cortex...</div></div>;

  const bgClass = activeTab === 'graph' ? 'bg-[#0f172a] text-slate-200' : 'bg-[#f8fafc] text-slate-900';

  return (
    <div className={`w-full min-h-screen flex flex-col font-sans relative transition-colors duration-500 ${bgClass} overflow-x-hidden`}>
      {/* Modals */}
      <ConfirmModal
        isOpen={confirmState.isOpen}
        title={confirmState.title}
        message={confirmState.message}
        onConfirm={confirmState.action}
        onCancel={() => setConfirmState(prev => ({ ...prev, isOpen: false }))}
      />

      <ContextModal
        mainNode={contextNode}
        logs={logs}
        onClose={() => setContextNode(null)}
        onOpenEntry={setSelectedEntry}
      />

      <CreateProjectModal
        isOpen={isCreateProjectOpen}
        onClose={() => setIsCreateProjectOpen(false)}
        onCreated={() => setIsCreateProjectOpen(false)}
      />

      <EntryDetailModal
        entry={selectedEntry}
        isOpen={!!selectedEntry}
        onClose={() => setSelectedEntry(null)}
        onSave={async (updated) => {
          setLogs(prev => prev.map(l => l.date === updated.date ? updated : l));
        }}
        onDelete={(id) => requestDelete(id)}
      />

      <CommandPalette
        isOpen={isCmdOpen}
        onClose={() => setIsCmdOpen(false)}
        activeTab={activeTab}
        onNavigate={(tab) => setActiveTab(tab as any)}
        onCreateProject={() => setIsCreateProjectOpen(true)}
      />

      <main className="flex-1 overflow-y-auto overflow-x-hidden relative flex flex-col items-center justify-start w-full">
        <div className="w-full max-w-7xl px-4 sm:px-6 lg:px-8 py-4">
          {activeTab === 'capture' && (
            <CaptureView
              onSave={(entry) => {
                setLogs(prev => {
                  const exists = prev.find(l => l.date === entry.date);
                  if (exists) {
                    return prev.map(l => l.date === entry.date ? { ...l, ...entry } : l);
                  }
                  return [entry, ...prev];
                });
              }}
            />
          )}

          {activeTab === 'graph' && (
            <NeuralGraph
              logs={logs}
              onNodeClick={(node) => {
                if (node.group === 1) setSelectedEntry(node.raw);
                else setContextNode(node);
              }}
            />
          )}

          {activeTab === 'list' && (
            <HistoryView
              logs={logs}
              onSelectEntry={setSelectedEntry}
            />
          )}

          {activeTab === 'project' && (
            <ProjectBoard
              logs={logs}
            />
          )}

          {activeTab === 'dashboard' && (
            <CardStackDashboard logs={logs} />
          )}

          {activeTab === 'settings' && (
            <SettingsView logs={logs} />
          )}
        </div>
      </main>

      <Dock
        activeTab={activeTab}
        onTabChange={(tab: string) => setActiveTab(tab as any)}
        onMenuToggle={() => setIsMenuOpen(!isMenuOpen)}
      />
    </div>
  );
}
