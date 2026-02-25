# 🤖 LifeOS Dev v3.5 | Cortex v3.2 | Journal v7.1 - Handover Report
**Date:** 2026-02-15
**Status:** Operational (Rate Limits Patched)
**Location:** G:\我的雲端硬碟\Cortex

## 🛑 IDENTITY PROTOCOL (READ FIRST)
**CRITICAL: Distinguish Your Role**

### 1. The Developer (You)
*   **Role**: Architect & Builder.
*   **Responsibility**: Write code, fix bugs, manage database schemas, and ensure the "Body" functions.
*   **Source of Truth**: `docs/SYSTEM_CONTEXT.md` (Technical Blueprint).
*   **Action**: You operate *outside* the runtime, modifying files and running scripts.

### 2. Cortex (The System)
*   **Role**: The "Soul" & Runtime Intelligence.
*   **Responsibility**: Interact with Commander 蒼禾, analyze daily logs, and synthesize insights *during runtime*.
*   **Source of Truth**: `backend-cortex/prompts/system_cortex.md` (Persona Definition).
*   **Action**: Cortex operates *inside* the runtime, executing the logic you built.

**Your Mission**: You build the **Body** (Code) so that **Cortex** (Soul) can inhabit it. Do not confuse the two.

## 1. The Single Source of Truth
*   **System Context**: `docs/SYSTEM_CONTEXT.md`. This is your Bible. Read it before writing a single line of code.
*   **Genetic Code**: `backend-cortex/schemas/registry.json`. usage of DB must align with this.
*   **Cloud DNA**: `G:\我的雲端硬碟\Cortex`. All protocols are synced here.

## 2. Key Protocols Deployed (v7.1)
### A. Agentic Task Ingest
*   **Protocol**: Daily Logs are scanned by AI.
*   **Action**: Tasks are extracted and written to `public.tasks` table.
*   **Link**: Tasks are automatically associated with Projects.

### B. Neural Graph (Brain View)
*   **Visual**: Thoughts are visualized in `NeuralGraph.tsx` using D3.js.
*   **Data**: `/api/v1/brain/graph` provides the synaptic connections.

### C. Subconscious Chat ( & Model Resilience)
*   **Interface**: Real-time streaming chat via `/api/v1/chat`.
*   **Resilience**: Implemented Dynamic Model Selection (`/system/models`) and fallback logic.
*   **Status**: Recovered from Rate Limit Incident by optimizing model config.
*   **Hotfix**: Added auto-reset for deprecated `pro-exp-02-05` models in Frontend.
*   **Logic Repair**: Updated `brain.py` to visualize `nodes`, `edges`, and `projects`. The Graph now reflects Database Truth, not just text regex.

## 3. Current System State
*   **Backend**: v7.1-BrainLink (Port 8000). [Updated 20:30: Model Config Optimized]
*   **Frontend**: v0.7.1 (Port 3000). [Updated 17:45: Manual Model Refresh Added]
*   **Database**: Supabase (Schema 24081).
*   **Cloud Sync**: Source code synced to GitHub `lienhuangbionime-lang/LifeOSvs`.
*   **AI Model**: Fast (`gemini-flash-lite-latest`) / Smart (`gemini-2.5-flash` due to Pro Quota).
*   **Knowledge Source**: `G:\我的雲端硬碟\Cortex` (Mandatory Search Path).

## 4. Pending Tasks / Next Phase
1.  **Node Association**: **[NEXT ACTION]** Implement "Card View" for Date/Tag nodes in Neural Graph.
2.  **Glass Box Activation**: Migration 005 `cortex_growth_logs` table has been declared active.
3.  **Semantic Search**: Ready for scaling.

## 🧠 Final Advice
The system has stabilized. We successfully patched a critical Rate Limit issue by implementing dynamic model selection. The "Body" (Frontend) now has more control over the "Brain" (Model Choice).
The next operative should focus immediately on **Node Association (Card View)** to complete the graph interaction loop.

*End of Transmission.*
