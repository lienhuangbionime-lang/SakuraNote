import os
import json
import uuid
import datetime
import google.generativeai as genai
import frontmatter

# 1. 配置 Gemini
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("FATAL: GEMINI_API_KEY is not set.")
genai.configure(api_key=API_KEY)

def analyze_dual_track_entry(raw_text):
    """
    專門解析 Dual-Track (Project/Life) 格式的日記
    """
    model = genai.GenerativeModel('gemini-1.5-flash') # 使用 Flash 模型速度快且便宜

    # 核心 Prompt：教導 AI 如何閱讀你的 Dual-Track 格式
    prompt = f"""
    You are the parser for LifeOS. Convert the raw "Dual-Track" journal into structured JSON.
    
    ### Input Text:
    {raw_text}
    
    ### Extraction Logic:
    1. **Project Intelligence**:
       - 'name_candidates': Extract potential project names from repeated nouns in Highlights/Behavior Path.
       - 'signals': Content from 'Signals Detected'.
       - 'blind_spots': Content from 'Blind Spot Question'.
       - 'open_nodes': Content from 'Open Nodes'.
       - 'confidence': Analyze 'Project Status Marker'. 
          - structure_score: (Low/Med/High) based on defined modules.
          - verification_score: (Low/Med/High) based on Verified/Unverified items.
    
    2. **Life Telemetry** (Critical):
       - 'energy_stability': Extract from metrics or infer (High/Med/Low).
       - 'relationship_presence': Boolean (True if meaningful interaction described).
       - 'baseline_safety': (Stable/Warning/Intervene) based on health/sleep/crisis.
    
    ### Output Format (Strict JSON):
    {{
      "mood": float,
      "focus": float,
      "tags": ["tag1"],
      "project_data": {{
          "candidates": ["name1"],
          "signals": "string",
          "blind_spots": "string",
          "open_nodes": "string",
          "confidence": {{ "structure": "Med", "verification": "Low" }}
      }},
      "life_data": {{
          "energy_stability": "Low",
          "relationship_presence": true,
          "baseline_safety": "Stable"
      }},
      "summary": "..."
    }}
    """

    try:
        response = model.generate_content(prompt)
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        analysis = json.loads(clean_text)
    except Exception as e:
        print(f"AI Parse Failed: {e}")
        # Fallback 預設值，避免系統崩潰
        analysis = {
            "mood": 5, "focus": 5, "energy": 5, 
            "tags": [], "summary": "AI Parse Error", 
            "sections": {}
        }

    # 生成向量 (Embedding) 用於未來的 RAG 搜尋
    embedding_result = genai.embed_content(
        model="models/embedding-001",
        content=raw_text,
        task_type="RETRIEVAL_DOCUMENT"
    )
    
    return analysis, embedding_result['embedding']

def save_to_inbox(raw_text, analysis, embedding):
    """
    儲存為 Inbox 原子檔案 (Markdown + JSON Sidecar)
    """
    # 嘗試從日記內容抓取日期，若無則用今天
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    # 簡單的正則抓取標題日期 (2026-01-20)
    import re
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', raw_text)
    if date_match:
        date_str = date_match.group(1)

    entry_id = str(uuid.uuid4())[:8]
    filename_base = f"data/inbox/{date_str}_{entry_id}"
    
    # 1. 建構前端 index.html 需要的完整資料結構
    # 這裡將 AI 分析結果與原始文字結合，符合 index.html 的 sanitizeLogEntry 格式
    frontend_data = {
        "uuid": entry_id,
        "date": date_str,
        "raw_text": raw_text, # 保存原始 Markdown
        "analysis": {
            "date": date_str,
            "mood": analysis.get("mood", 5),
            "focus": analysis.get("focus", 5),
            "energy": analysis.get("energy", 5),
            "tags": analysis.get("tags", []),
            "summary": analysis.get("summary", ""),
            "sections": analysis.get("sections", {})
        },
        "embedding": embedding # 向量數據 (前端不會用到，但為了未來 RAG 存著)
    }

    # 2. 寫入 Sidecar JSON (這就是 GitHub Sync 會抓取的檔案)
    os.makedirs("data/inbox", exist_ok=True)
    with open(f"{filename_base}.json", "w", encoding="utf-8") as f:
        json.dump(frontend_data, f, ensure_ascii=False, indent=2)

    # 3. 寫入 Markdown (給人看的備份)
    # Frontmatter 讓 GitHub 網頁版預覽時也很漂亮
    post = frontmatter.Post(raw_text, **{
        "uuid": entry_id,
        "mood": analysis.get("mood"),
        "tags": analysis.get("tags")
    })
    with open(f"{filename_base}.md", "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(post))

    print(f"✅ Created Inbox Entry: {filename_base}.json")

if __name__ == "__main__":
    # 從 GitHub Action 的環境變數讀取 Zapier 傳來的文字
    journal_text = os.getenv("JOURNAL_TEXT")
    
    if not journal_text:
        print("⚠️ No text provided via JOURNAL_TEXT env var.")
        # 本地測試用 (可以把你的範例日記貼在這裡測試)
        exit(1)
    
    analysis_data, vector_data = analyze_dual_track_entry(journal_text)
    save_to_inbox(journal_text, analysis_data, vector_data)
