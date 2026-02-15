import requests
import json
from datetime import datetime

url = "http://127.0.0.1:8000/api/v1/ingest"
payload = {
    "content": """# System Cleanup & Handover Complete (2026-02-14)

## Actions Performed
1. **Frontend Purification**: Removed legacy components (Dashboard.tsx, MarkdownRenderer.tsx, etc.) and verified build.
2. **Backend Purification**: Removed legacy kernel source and temporary diagnostic scripts.
3. **Directory Optimization**: Executed `cleanup.ps1` to remove build artifacts (.next, __pycache__) and organize documentation into `docs/`.
4. **Soul Synchronization**: Downloaded and updated core protocol files (.cursorrules, SYSTEM_CONTEXT.md) from Cloud Drive.
5. **Growth Verification**: Confirmed 38 critical defect resolutions and schema alignment.

## System State
- **Backend**: FastAPI Live on Port 8000.
- **Frontend**: Next.js verified and build-ready on Port 3000.
- **Protocols**: Aligned on 'memories' table and UUID standards.

[STATUS] The LifeOS v3.5 is now in a high-purity, production-ready state.
""",
    "skipAi": True,
    "date": datetime.now().strftime("%Y-%m-%d")
}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    # Force UTF-8 encoding for printing
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print(f"Response: {json.dumps(response.json(), ensure_ascii=False)}")
except Exception as e:
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print(f"Failed to ingest memory: {e}")
