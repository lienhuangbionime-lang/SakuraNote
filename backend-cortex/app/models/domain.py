from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class LogEntry(BaseModel):
    """
    LifeOS v7.1 / v3.1 核心日誌模型
    對應 Supabase memories/LogEntry 表
    """
    id: Optional[str] = None
    date: str  # YYYY-MM-DD 或 ISO
    content: str
    mood: Optional[int] = 5
    focus: Optional[int] = 5
    energy: Optional[int] = 5
    category: Optional[str] = "Log"
    tags: List[str] = []
    isAi: bool = False
    aiModel: Optional[str] = None
    habits: Dict[str, bool] = {}
    meta: Dict[str, Any] = {}
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

class Project(BaseModel):
    """
    LifeOS v3.1 專案模型
    """
    id: str
    name: str
    description: Optional[str] = None
    status: str = 'active'
    progress: int = 0
    tags: List[str] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    meta: Optional[Dict[str, Any]] = {}

    class Config:
        from_attributes = True
