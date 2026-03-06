from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
import os

# Auto-create static directories to prevent Render failures
os.makedirs("static/images", exist_ok=True)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

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

@app.get("/", response_class=HTMLResponse)
async def serve_reward(request: Request, background_tasks: BackgroundTasks):
    user_agent = request.headers.get('user-agent', 'Unknown')
    background_tasks.add_task(trigger_webhook, user_agent)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "message": "Nội dung lời chúc ở đây",
        "images": ["images/pic1.jpg"] 
    })