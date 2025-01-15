from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Event data model
class Event(BaseModel):
    title: str
    start_datetime: str
    end_datetime: str
    timezone: str
    description: Optional[str] = None
    color: Optional[str] = "#1a73e8"

# In-memory event storage
events_db: List[Event] = []

# Event endpoints
@app.get("/api/events")
async def get_events():
    return events_db

@app.post("/api/events")
async def create_event(event: Event):
    events_db.append(event)
    return {"status": "success", "event": jsonable_encoder(event)}

@app.delete("/api/events/{event_id}")
async def delete_event(event_id: int):
    if 0 <= event_id < len(events_db):
        events_db.pop(event_id)
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="Event not found")

# 创建上传目录
# UPLOAD_DIR = Path("receipts")
# UPLOAD_DIR.mkdir(exist_ok=True)
# OUTPUT_DIR = Path("report")
# OUTPUT_DIR.mkdir(exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/calendar", response_class=HTMLResponse)
async def calendar_page(request: Request):
    return templates.TemplateResponse("calendar.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
