from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
import requests
import os
import glob

# Vercel functions are read-only, so we cannot create directories here at runtime.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI()
static_path = os.path.join(BASE_DIR, "static")
if os.path.isdir(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")
    
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8543900765:AAFRHplaqbv0fvaBXHNSeo4EWscyceIt4q0")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "7841326585")

def trigger_webhook(user_agent: str):
    """Feedback Loop: Bắn tín hiệu khi Target cắn câu"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID, 
        "text": f"🎯 BÁO CÁO: Target đã mở quà!\nThiết bị: {user_agent}"
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Webhook Error: {e}")

@app.get("/music.mp3")
async def get_music():
    """Serve any mp3 file present in root or static directory dynamically"""
    mp3_files = glob.glob(os.path.join(BASE_DIR, "*.mp3")) + glob.glob(os.path.join(BASE_DIR, "static", "*.mp3"))
    if mp3_files:
        return FileResponse(mp3_files[0])
    return {"error": "Music file not found"}

@app.get("/", response_class=HTMLResponse)
async def serve_reward(request: Request, background_tasks: BackgroundTasks):
    user_agent = request.headers.get('user-agent', 'Unknown')
    background_tasks.add_task(trigger_webhook, user_agent)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "message": "Nội dung lời chúc ở đây",
        "images": ["images/pic1.jpg"] 
    })