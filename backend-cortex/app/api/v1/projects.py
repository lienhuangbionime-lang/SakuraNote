from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
from datetime import datetime

from app.core.database import supabase
from app.models.domain import Project
from app.models.schemas import ProjectCreate, ProjectUpdate, ProjectMergeRequest

router = APIRouter()

@router.get("/", response_model=List[Project])
async def get_projects():
    """List all projects."""
    res = supabase.table("projects").select("*").order("updated_at", desc=True).execute()
    return res.data

@router.post("/", response_model=Project)
async def create_project(project: ProjectCreate):
    """Create a new project."""
    data = project.model_dump(exclude_none=True)
    # Supabase will handle id, created_at, updated_at
    res = supabase.table("projects").insert(data).execute()
    if not res.data:
        raise HTTPException(status_code=500, detail="Failed to create project")
    return res.data[0]

@router.patch("/{project_id}", response_model=Project)
async def update_project(project_id: str, project: ProjectUpdate):
    """Update a project."""
    data = project.model_dump(exclude_none=True)
    data["updated_at"] = datetime.utcnow().isoformat()
    
    res = supabase.table("projects").update(data).eq("id", project_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Project not found")
    return res.data[0]

@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """Delete a project."""
    res = supabase.table("projects").delete().eq("id", project_id).execute()
    return {"success": True, "message": "Project deleted"}

@router.post("/{project_id}/merge")
async def merge_project(project_id: str, merge_req: ProjectMergeRequest):
    """Merge this project into another project.
    
    1. Update all LogEntries with tags from this project to the target project's tags.
    2. Delete this project.
    """
    # 1. Get Source Project
    source_res = supabase.table("projects").select("*").eq("id", project_id).execute()
    if not source_res.data:
        raise HTTPException(status_code=404, detail="Source project not found")
    source_project = source_res.data[0]
    
    # 2. Get Target Project
    target_res = supabase.table("projects").select("*").eq("id", merge_req.target_project_id).execute()
    if not target_res.data:
        raise HTTPException(status_code=404, detail="Target project not found")
    target_project = target_res.data[0]
    
    # 3. Enhanced Merge Logic:
    # - Merge Tags: Add source tags to target tags (deduplicated)
    # - Merge Description: Append source description to target
    # - Delete Source Project
    
    source_tags = set(source_project.get("tags") or [])
    target_tags = set(target_project.get("tags") or [])
    merged_tags = list(source_tags.union(target_tags))
    
    source_desc = source_project.get("description") or ""
    target_desc = target_project.get("description") or ""
    new_desc = target_desc
    if source_desc:
        new_desc += f"\n\n[Merged from {source_project['name']}]\n{source_desc}"

    # Update Target
    supabase.table("projects").update({
        "tags": merged_tags,
        "description": new_desc,
        "updated_at": datetime.utcnow().isoformat()
    }).eq("id", target_project['id']).execute()
    
    # Delete Source
    supabase.table("projects").delete().eq("id", project_id).execute()
    
    return {"success": True, "message": f"Merged {source_project['name']} into {target_project['name']}"}
