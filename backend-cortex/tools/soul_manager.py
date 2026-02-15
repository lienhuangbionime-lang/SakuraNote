# LifeOS Soul Manager (Reorganized Version)
# Handling identity sync across AI operatives.
import os
import json
import datetime
import shutil
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv

# Verification Header: ✅ [2026-02-14] Soul Protocol Verified & Synced.
# 設定區
BASE_DIR = r"c:\Users\benga\Desktop\lifeosjxs-main"
SYNC_DIR = os.path.join(BASE_DIR, "data", "sync_brain")
TOKEN_FILE = os.path.join(BASE_DIR, "config", "token.json") 
CLIENT_SECRET_FILE = os.path.join(BASE_DIR, "config", "client_secret.json")

# 核心靈魂檔案清單 (Reorganized Paths)
SOUL_FILES = {
    ".cursorrules": os.path.join(BASE_DIR, "config", ".cursorrules"),
    "SYSTEM_CONTEXT.md": os.path.join(BASE_DIR, "docs", "for-ai", "SYSTEM_CONTEXT.md"),
    "registry.json": os.path.join(BASE_DIR, "src", "backend", "schemas", "registry.json"),
    "evolution_log.json": os.path.join(BASE_DIR, "src", "backend", "schemas", "evolution_log.json"),
    "system_daily.md": os.path.join(BASE_DIR, "src", "backend", "prompts", "system_daily.md"),
    "system_cortex.md": os.path.join(BASE_DIR, "src", "backend", "prompts", "system_cortex.md"),
    "soul_manager.py": os.path.join(BASE_DIR, "src", "backend", "tools", "soul_manager.py"),
}

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_gdrive_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRET_FILE):
                print(f"[ERROR] {CLIENT_SECRET_FILE} not found. Please provide Desktop Client Secret JSON.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)

def upload_to_gdrive(service, file_path, folder_id):
    file_name = os.path.basename(file_path)
    query = f"name = '{file_name}' and '{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, fields="files(id)").execute()
    files = results.get('files', [])

    media = MediaFileUpload(file_path, resumable=False)
    
    if files:
        file_id = files[0]['id']
        service.files().update(fileId=file_id, media_body=media).execute()
        return f"Updated: {file_name}"
    else:
        file_metadata = {'name': file_name, 'parents': [folder_id]}
        service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return f"Created: {file_name}"

def main():
    env_path = os.path.join(BASE_DIR, "src", "backend", ".env")
    load_dotenv(env_path)
    
    print(f"--- LifeOS Soul Sync (Reorganized) {datetime.datetime.now()} ---")
    
    # 1. 本地備份
    if not os.path.exists(SYNC_DIR):
        os.makedirs(SYNC_DIR)
    for name, path in SOUL_FILES.items():
        if os.path.exists(path):
            shutil.copy2(path, os.path.join(SYNC_DIR, name))
            print(f"[Local OK] {name}")
        else:
            print(f"[Local MISS] {name} at {path}")

    # 2. 雲端同步
    folder_id = os.getenv("GDRIVE_FOLDER_ID")
    if not folder_id:
        print("[WARN] GDRIVE_FOLDER_ID not found in .env.")
        return

    try:
        service = get_gdrive_service()
        if not service:
            return

        print(f"[Cloud] Syncing to Folder: {folder_id}...")
        for name in SOUL_FILES.keys():
            local_path = os.path.join(SYNC_DIR, name)
            if os.path.exists(local_path):
                try:
                    msg = upload_to_gdrive(service, local_path, folder_id)
                    print(f"[Cloud OK] {msg}")
                except Exception as e:
                    print(f"[Cloud Error] {name}: {e}")
    except Exception as e:
        print(f"[Auth Error] {e}")

    print("--- LifeOS Identity Secured via Reorganized Structure ---")

if __name__ == "__main__":
    main()
