"""
Cortex Sync Tool - Automatic Google Drive Synchronization
Purpose: Ensure Google Drive Cortex folder is always the latest version
Usage: Run after any modification to critical files
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import json

# ==========================================
# SYNC CONFIGURATION (HARDCODED RULES)
# ==========================================

# Source: Local development directory
SOURCE_ROOT = Path(r"c:\Users\benga\Desktop\lifeosjxs-main\backend-cortex")

# Destination: Google Drive (SINGLE SOURCE OF TRUTH)
DEST_ROOT = Path(r"G:\我的雲端硬碟\Cortex")

# Critical files that MUST be synced
SYNC_RULES = {
    "SYSTEM_CONTEXT.md": "SYSTEM_CONTEXT.md",
    "evolution_log.json": "evolution_log.json",
    ".cursorrules": ".cursorrules",
    "requirements.txt": "code_backup/requirements.txt",
    "app/workers/twse_scanner.py": "code_backup/twse_scanner.py",
    "app/core/gemini.py": "code_backup/gemini.py",
    "app/core/database.py": "code_backup/database.py",
    "app/api/v1/chat.py": "code_backup/chat.py",
    "app/api/v1/ingest.py": "code_backup/ingest.py",
    "main.py": "code_backup/main.py",
}

# Directories to sync recursively
SYNC_DIRS = {
    "prompts": "prompts",
    "schemas": "schemas",
    "migrations": "migrations",
    "tools": "tools",
}


# ==========================================
# SYNC ENGINE
# ==========================================

class CortexSync:
    def __init__(self):
        self.synced_files = []
        self.errors = []
        
    def ensure_dest_dir(self, dest_path: Path):
        """Ensure destination directory exists"""
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
    def sync_file(self, source_rel: str, dest_rel: str):
        """Sync a single file"""
        source = SOURCE_ROOT / source_rel
        dest = DEST_ROOT / dest_rel
        
        if not source.exists():
            self.errors.append(f"[WARN] Source not found: {source_rel}")
            return
        
        try:
            self.ensure_dest_dir(dest)
            shutil.copy2(source, dest)
            self.synced_files.append(dest_rel)
            print(f"[OK] Synced: {source_rel} -> {dest_rel}")
        except Exception as e:
            self.errors.append(f"[ERROR] Failed to sync {source_rel}: {e}")
            
    def sync_directory(self, source_rel: str, dest_rel: str):
        """Sync entire directory recursively"""
        source = SOURCE_ROOT / source_rel
        dest = DEST_ROOT / dest_rel
        
        if not source.exists():
            self.errors.append(f"[WARN] Source directory not found: {source_rel}")
            return
        
        try:
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(source, dest)
            print(f"[OK] Synced directory: {source_rel} -> {dest_rel}")
        except Exception as e:
            self.errors.append(f"[ERROR] Failed to sync directory {source_rel}: {e}")
            
    def run(self):
        """Execute full sync"""
        print("=" * 60)
        print("Cortex Sync Tool - Starting Synchronization")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 1. Sync individual files
        print("\n[1/2] Syncing critical files...")
        for source_rel, dest_rel in SYNC_RULES.items():
            self.sync_file(source_rel, dest_rel)
        
        # 2. Sync directories
        print("\n[2/2] Syncing directories...")
        for source_rel, dest_rel in SYNC_DIRS.items():
            self.sync_directory(source_rel, dest_rel)
        
        # 3. Generate sync report
        print("\n" + "=" * 60)
        print("Sync Report")
        print("=" * 60)
        print(f"[OK] Files synced: {len(self.synced_files)}")
        
        if self.errors:
            print(f"[WARN] Errors encountered: {len(self.errors)}")
            for error in self.errors:
                print(f"  - {error}")
        else:
            print("[OK] No errors")
        
        # 4. Update sync metadata
        self.write_sync_metadata()
        
        print("\n[OK] Sync complete. Google Drive Cortex folder is now the latest version.")
        print("=" * 60)
        
    def write_sync_metadata(self):
        """Write sync metadata to Google Drive"""
        metadata = {
            "last_sync": datetime.now().isoformat(),
            "synced_files": self.synced_files,
            "errors": self.errors,
            "source": str(SOURCE_ROOT),
            "destination": str(DEST_ROOT)
        }
        
        metadata_path = DEST_ROOT / ".sync_metadata.json"
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            print(f"[OK] Sync metadata written to {metadata_path}")
        except Exception as e:
            print(f"[WARN] Failed to write sync metadata: {e}")


# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":
    sync = CortexSync()
    sync.run()
