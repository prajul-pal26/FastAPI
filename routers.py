from fastapi import UploadFile
import pandas as pd
from fastapi import APIRouter
import io
import uuid
from typing import Optional
from fastapi import Depends, File, UploadFile, Form, HTTPException
from datetime import datetime, timedelta
import redis,os
import json
from typing import Optional

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)



router = APIRouter()

def get_datetime(
    Event_Actual_time: str = Form(..., description="Format: 2025-09-04 15:30:10"),):
    try:
        # Parse the naive datetime
        dt = datetime.strptime(Event_Actual_time, "%Y-%m-%d %H:%M:%S")
        return dt
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid datetime or timedelta format: {str(e)}")



def chunk_dataframe(df, chunk_size):
    for i in range(0, len(df), chunk_size):
        yield df.iloc[i:i + chunk_size]


@router.post("/add_sms_leads")
async def add_sms_leads(file: UploadFile = File(...),Event_Actual_time: datetime = Depends(get_datetime),chunk_size: int = Form(100, description="Number of leads per chunk"),interval_seconds: int = Form(0, description="Seconds between chunks (set 0 for same time)"),message_time: int = Form(0, description="hours before the actual event time")):
    contents = await file.read()

    df = pd.read_csv(io.StringIO(contents.decode('utf-8'))) 
    df = df.fillna('').astype(str)
    if df.empty:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    upload_id = f"upload_{uuid.uuid4().hex[:8]}"
    file_name = file.filename

    redis_key = f"sms_upload:{upload_id}"
    redis_client.hset(redis_key, mapping={
        "file_name": file_name,
        "msg1": "",
        "msg2": "",
        "Actual_event_time":Event_Actual_time.isoformat()

    })

    for idx, chunk in enumerate(chunk_dataframe(df, chunk_size)):
        chunk_time = Event_Actual_time + timedelta(seconds=interval_seconds * idx) - timedelta(hours=message_time)
        chunk_key = f"{chunk_time.isoformat()}/{len(chunk)}"
        chunk_data = json.dumps(chunk.to_dict(orient="records"))
        redis_client.hset(redis_key, chunk_key, chunk_data)

    data = redis_client.hgetall(redis_key)
    scheduled_leads_summary = [
        {"scheduled_time": dt.split('/')[0], "lead_count": len(json.loads(data[dt]))}
        for dt in data if dt not in ("file_name", "msg1", "msg2","Actual_event_time")
    ]

    return {
        "total_leads": len(df),
        "chunk_size": chunk_size,
        "Actual_event_time":Event_Actual_time.isoformat(),
        "total_chunks": len(scheduled_leads_summary),
        "interval_minutes": interval_seconds,
        "message1": redis_client.hget(redis_key, "msg1"),
        "message2": redis_client.hget(redis_key, "msg2"),
        "scheduled_leads_summary": scheduled_leads_summary  
    }

@router.get("/view_sms_leads")
async def view_sms_leads(actual_time: Optional[str] = None):
    keys = redis_client.keys("sms_upload:*")
    if not keys:
        raise HTTPException(status_code=404, detail="No leads have been uploaded yet.")

    uploads_info = []

    for redis_key in keys:
        upload_id = redis_key.split(":")[1]
        data = redis_client.hgetall(redis_key)
        if actual_time and data.get("Actual_event_time") != actual_time:
            continue
        scheduled_info = []

        for field in data.keys():
            if field in ["file_name", "msg1", "msg2","Actual_event_time"]:
                continue

            try:
                leads = json.loads(data[field])
                lead_count = len(leads) if isinstance(leads, list) else 0
            except Exception:
                lead_count = 0  # If corrupted or not a list
            timestamp_str, original_size_str = field.split("/")
            original_size = int(original_size_str)  

            scheduled_info.append({
                "timestamp": timestamp_str,
                "lead_sent_count": f"{original_size-lead_count}/{original_size}"
            })

        uploads_info.append({
            "upload_id": upload_id,
            "file_name": data.get("file_name", ""),
            "Actual_event_time":data.get("Actual_event_time", ""),
            "total_chunks": len(scheduled_info),
            "message1": data.get("msg1", ""),
            "message2": data.get("msg2", ""),
            "scheduled_times": scheduled_info
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
    redis_key = f"sms_upload:{upload_id}"
    if not redis_client.exists(redis_key):
        raise HTTPException(status_code=404, detail="Upload ID not found.")

    changes = []

    if delete_msg1:
        redis_client.hset(redis_key, "msg1", "")
        changes.append("msg1 deleted")
    elif new_msg1 is not None:
        redis_client.hset(redis_key, "msg1", new_msg1)
        changes.append("msg1 updated")

    if delete_msg2:
        redis_client.hset(redis_key, "msg2", "")
        changes.append("msg2 deleted")
    elif new_msg2 is not None:
        redis_client.hset(redis_key, "msg2", new_msg2)
        changes.append("msg2 updated")

    if not changes:
        return {
            "upload_id": upload_id,
            "message": "No updates or deletions were applied.",
            "msg1": redis_client.hget(redis_key, "msg1"),
            "msg2": redis_client.hget(redis_key, "msg2")
        }

    return {
        "upload_id": upload_id,
        "message": "Changes applied successfully.",
        "changes": changes,
        "msg1": redis_client.hget(redis_key, "msg1"),
        "msg2": redis_client.hget(redis_key, "msg2")
    }


@router.post("/send_sms_leads")
async def send_sms_leads():
    keys = redis_client.keys("sms_upload:*")
    if not keys:
        raise HTTPException(status_code=404, detail="No leads found in Redis.")

    summary_report = []

    for redis_key in keys:
        data = redis_client.hgetall(redis_key)
        upload_id = redis_key.split(":")[1]
        msg1 = data.get("msg1", "")
        msg2 = data.get("msg2", "")

        sent_chunks = []

        for field in data:
            if field in ["file_name", "msg1", "msg2","Actual_event_time"]:
                continue  # Skip meta fields like file name and messages

            try:
                leads = json.loads(data[field])
            except Exception as e:
                continue  # Skip corrupt chunks
            for lead in leads[:]:
                phone = lead.get("phone") or lead.get("mobile") or lead.get("number") or "unknown"
                message = f"{msg1} {msg2}".strip()

                print(f"Sending to {phone}: {message}")
                leads.remove(lead)   # for check the remove logic

                redis_client.hset(redis_key, field, json.dumps(leads))   # refresh the list of leads after removing the lead after send huim the message 
              

            sent_chunks.append({
                "scheduled_time": field,
                "lead_count": len(leads)
            })

        summary_report.append({
            "upload_id": upload_id,
            "file_name": data.get("file_name", ""),
            "message1": msg1,
            "message2": msg2,
            "total_chunks_sent": len(sent_chunks),
            "details": sent_chunks
        })

    return {
        "status": "success",
        "total_uploads_processed": len(summary_report),
        "report": summary_report
    }

@router.delete("/delete_sms_leads")
async def delete_sms_leads(identifier: str = Form(...)):
    deleted_uploads = []

    keys = redis_client.keys("sms_upload:*")
    for key in keys:
        upload_id = key.split(":")[1]
        file_name = redis_client.hget(key, "file_name")

        if identifier == upload_id or identifier == file_name:
            redis_client.delete(key)
            deleted_uploads.append(upload_id)

    if not deleted_uploads:
        raise HTTPException(status_code=404, detail=f"No uploads found for identifier '{identifier}'")

    return {
        "deleted_uploads": deleted_uploads,
        "message": f"Deleted {len(deleted_uploads)} upload(s) matching identifier '{identifier}'"
    }