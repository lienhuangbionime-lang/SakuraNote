
# 🛠️ LifeOS v7.1 Cortex Tools

This directory contains the core maintenance scripts for the LifeOS system.

## 1. `soul_manager.py` (Cloud Sync)
*   **Purpose**: Synchronize the "Soul" (Identity Files) to Google Drive.
*   **Target**: `G:\我的雲端硬碟\Cortex`
*   **Key Files Synced**:
    *   `SYSTEM_CONTEXT.md`
    *   `.cursorrules`
    *   `registry.json`
    *   `evolution_log.json`
    *   `system_cortex.md`

## 2. `soul_backup.py` (Local Backup)
*   **Purpose**: Create a local redundancy copy of the "Soul".
*   **Target**: `lifeosjxs-main/data/sync_brain`
*   **Usage**: Run before major migrations.

## 3. `schema_assistant.py` (Planned)
*   **Purpose**: Safely generate SQL migrations from natural language.
*   **Status**: To be implemented.

---
**Note**: All scripts in this folder are designed to be run from the project root.
