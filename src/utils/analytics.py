import pandas as pd
from collections import Counter

def safe_get_dict(obj, default=None):
    """防禦性取得字典，若為 NaN/Float 則返回空字典"""
    if default is None:
        default = {}
    if isinstance(obj, dict):
        return obj
    return default

def generate_system_state(df):
    """
    統一的系統狀態計算邏輯 (The Analytics Core)
    """
    if df.empty:
        return {
            "active_projects": [],
            "idea_seeds": [],
            "system_status": {"mode": "BUILD", "reason": "No Data"}
        }

    # 確保是日期倒序
    df_sorted = df.sort_values(by='date', ascending=False)
    recent_df = df_sorted.head(30)
    
    # 1. Gardener Logic (專案索引)
    all_tags = []
    for _, row in recent_df.iterrows():
        # [Fix] 使用 safe_get_dict 防禦 float/nan
        analysis = safe_get_dict(row.get('ai_analysis'))
        
        # 取得 tags，並防禦 row.get('tags') 可能回傳 float 的情況
        tags_from_ai = analysis.get('tags')
        tags_from_row = row.get('tags')
        
        # 確保 tags 是 list
        if not isinstance(tags_from_ai, list): tags_from_ai = []
        if not isinstance(tags_from_row, list): tags_from_row = []
        
        # 合併
        tags = tags_from_ai or tags_from_row
        
        if isinstance(tags, list):
            all_tags.extend([str(t).replace('#', '') for t in tags])
    
    tag_counts = Counter(all_tags)
    active_projects = [tag for tag, count in tag_counts.items() if count >= 3]

    # 2. Idea Generator (想法萃取)
    ideas = []
    for _, row in recent_df.iterrows():
        analysis = safe_get_dict(row.get('ai_analysis'))
        p_data = safe_get_dict(analysis.get('project_data'))
        
        has_signal = bool(p_data.get('signals'))
        has_blind_spot = bool(p_data.get('blind_spots'))
        has_open_node = bool(p_data.get('open_nodes'))

        if has_signal and has_blind_spot and has_open_node:
            signal_txt = str(p_data.get('signals', ''))[:20]
            node_txt = str(p_data.get('open_nodes', ''))[:20]
            ideas.append({
                "date": row['date'].strftime('%Y-%m-%d') if pd.notnull(row['date']) else "Unknown",
                "core_concept": f"{signal_txt}... + {node_txt}..."
            })

    # 3. Governor Logic (降速機制)
    last_2_days = df_sorted.head(2)
    throttle_mode = "BUILD"
    reason = "All Systems Nominal"
    
    for _, row in last_2_days.iterrows():
        analysis = safe_get_dict(row.get('ai_analysis'))
        life = safe_get_dict(analysis.get('life_data'))
        
        safety = life.get('baseline_safety')
        energy = life.get('energy_stability')

        if safety == 'Intervene' or energy == 'Low':
            throttle_mode = "MAINTENANCE"
            date_str = row['date'].strftime('%Y-%m-%d') if pd.notnull(row['date']) else "Unknown"
            reason = f"Safety Protocol Triggered on {date_str}"
            break
            
    return {
        "active_projects": active_projects,
        "idea_seeds": ideas,
        "system_status": {
            "mode": throttle_mode,
            "reason": reason
        }
    }
