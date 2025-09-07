from fastapi import UploadFile
from sms_config import DateTimeValidator
import pandas as pd
from fastapi import APIRouter
from typing import Union
import io
import uuid
from typing import Optional
from fastapi import Depends, File, UploadFile, Form, HTTPException
from datetime import datetime, timezone, timedelta

router = APIRouter()




def get_datetime(
    datetime_str: str = Form(..., description="Format: YYYY-MM-DD HH:MM:SS"),):
    try:
        # Parse the naive datetime
        dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        return dt
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid datetime or timedelta format: {str(e)}")
stored_chunks_dict = {}


def chunk_dataframe(df, chunk_size):
    for i in range(0, len(df), chunk_size):
        yield df.iloc[i:i + chunk_size]


@router.post("/add_sms_leads")
async def add_sms_leads(file: UploadFile = File(...),schedule_datetime: datetime = Depends(get_datetime),chunk_size: int = Form(100, description="Number of leads per chunk"),interval_minutes: int = Form(0, description="Minutes between chunks (set 0 for same time)")):
    contents = await file.read()

    df = pd.read_csv(io.StringIO(contents.decode('utf-8'))) 
    df = df.fillna('').astype(str)
    if df.empty:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    upload_id = f"upload_{uuid.uuid4().hex[:8]}"
    file_name = file.filename

    stored_chunks_dict[upload_id] = {
        "file_name": file_name,
        "msg1":'',
        "msg2":'',
        "chunks": {}
    }

    # Populate dictionary with chunks
    for idx, chunk in enumerate(chunk_dataframe(df, chunk_size)):
        chunk_time = schedule_datetime + timedelta(seconds=interval_minutes * idx)
        key = chunk_time.isoformat()
        stored_chunks_dict[upload_id]["chunks"][key]= chunk.to_dict(orient="records")
    
    scheduled_leads_summary = [
        {"scheduled_time": dt, "lead_count": len(leads)}
        for dt, leads in stored_chunks_dict[upload_id]["chunks"].items()
    ]

    return {
        "total_leads": len(df),
        "chunk_size": chunk_size,
        "total_chunks": len(scheduled_leads_summary),
        "interval_minutes": interval_minutes,
        "message1":stored_chunks_dict[upload_id]['msg1'],
        "message2":stored_chunks_dict[upload_id]['msg2'],
        "scheduled_leads_summary": scheduled_leads_summary  
    }

@router.get("/view_sms_leads")
async def view_sms_leads():
    if not stored_chunks_dict:
        raise HTTPException(status_code=404, detail="No leads have been uploaded yet.")
    
    uploads_info = []
    for upload_id, entry in stored_chunks_dict.items():
        uploads_info.append({
            "upload_id": upload_id,
            "file_name": entry["file_name"],
            "total_chunks": len(entry["chunks"]),
            "message1":entry['msg1'],
            "message2":entry['msg2'],
            "scheduled_times": list(entry["chunks"].keys())
        })
    return uploads_info

@router.post("/manage_sms_messages")
async def manage_sms_messages(
    upload_id: str = Form(..., description="Select an upload_id to update or delete messages."),
    new_msg1: Optional[str] = Form(None, description="New content for msg1. Leave blank to skip."),
    new_msg2: Optional[str] = Form(None, description="New content for msg2. Leave blank to skip."),
    delete_msg1: bool = Form(False, description="Delete msg1 instead of updating."),
    delete_msg2: bool = Form(False, description="Delete msg2 instead of updating."),
):
    # Validate upload_id
    if upload_id not in stored_chunks_dict:
        raise HTTPException(status_code=404, detail="Upload ID not found.")

    changes = []

    if delete_msg1:
        stored_chunks_dict[upload_id]["msg1"] = ''
        changes.append("msg1 deleted")
    elif new_msg1 is not None:
        stored_chunks_dict[upload_id]["msg1"] = new_msg1
        changes.append("msg1 updated")

    if delete_msg2:
        stored_chunks_dict[upload_id]["msg2"] = ''
        changes.append("msg2 deleted")
    elif new_msg2 is not None:
        stored_chunks_dict[upload_id]["msg2"] = new_msg2
        changes.append("msg2 updated")

    if not changes:
        return {
            "upload_id": upload_id,
            "message": "No updates or deletions were applied.",
            "msg1": stored_chunks_dict[upload_id]["msg1"],
            "msg2": stored_chunks_dict[upload_id]["msg2"]
        }

    return {
        "upload_id": upload_id,
        "message": "Changes applied successfully.",
        "changes": changes,
        "msg1": stored_chunks_dict[upload_id]["msg1"],
        "msg2": stored_chunks_dict[upload_id]["msg2"]
    }




@router.delete("/delete_sms_leads")
async def delete_sms_leads(identifier: str = Form(..., description="upload_id or file name")):
    deleted_uploads = []

    for upload_id in list(stored_chunks_dict.keys()):
        entry = stored_chunks_dict[upload_id]

        if upload_id == identifier or entry.get("file_name") == identifier:
            del stored_chunks_dict[upload_id]
            deleted_uploads.append(upload_id)

    if not deleted_uploads:
        raise HTTPException(status_code=404, detail=f"No uploads found for identifier '{identifier}'")

    return {
        "deleted_uploads": deleted_uploads,
        "message": f"Deleted {len(deleted_uploads)} upload(s) matching identifier '{identifier}'"
    }
