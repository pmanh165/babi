# PROJECT BRIEF: PERSONALIZED ENGAGEMENT LOOP (N=1)

## 1. OBJECTIVE & BEHAVIORAL LOGIC
* **Business Outcome:** Tạo ra trải nghiệm tặng quà cá nhân hóa, đo lường được khoảnh khắc "Transfer" (người nhận mở quà).
* **Behavioral Model (Fogg & COM-B):**
    * **Cue (Trigger):** Hình ảnh QR Art ẩn trong bó hoa (Kích thích thị giác/Motivation).
    * **Routine (Behavior):** Quét mã bằng smartphone.
    * **Reward (Feedback):** Landing page với hiệu ứng Floating Animation và BGM (Background Music).
    * **Admin Feedback Loop:** Webhook bắn notification JSON payload về Telegram của Jayden ngay khi DOM load.

## 2. ARCHITECTURE & TECH STACK
* **Strategy:** Hybrid Deployment (Chỉ automate Tracking/Reward, manual khâu Visual Cue để tránh Over-engineering).
* **Backend:** Python 3.x + FastAPI (Handle routing & Async Webhook).
* **Frontend:** Vanilla HTML/CSS/JS (No framework, optimize for load speed).
* **Hosting:** Render.com hoặc Railway.app (Free tier, auto-deploy via GitHub).
* **Generative AI:** Hugging Face QR Code ControlNet (Web UI, manual generation).

## 3. DIRECTORY STRUCTURE
Setup cấu trúc này trên Antigravity IDE (không dùng khoảng trắng trong tên thư mục):

/project_for_gf
├── .venv/                  # Virtual Environment (Git ignored)
├── .gitignore              # Ignore .venv/ và __pycache__/
├── requirements.txt        # Dependencies
├── main.py                 # Backend API Endpoint & Webhook
├── static/
│   ├── music.mp3           # Audio file (< 5MB)
│   └── images/
│       └── pic1.jpg        # Ảnh hiển thị (< 200KB/ảnh)
└── templates/
    └── index.html          # Frontend UI

---

## 4. EXECUTION PLAN (THE BUILD)

### PHASE 1: Environment Setup (Strict Adherence)
Triệt tiêu các lỗi Identity Conflict (Git) và Path Parsing (Zsh). Mở Terminal và gõ:
1. `mkdir project_for_gf && cd project_for_gf`
2. `python3 -m venv .venv`
3. `source .venv/bin/activate` (Bắt buộc phải thấy prefix `(.venv)`).
4. `echo "fastapi\nuvicorn\njinja2\nrequests" > requirements.txt`
5. `pip install -r requirements.txt`
6. Reset Git credential (nếu xài Mac): 
   `git credential-osxkeychain erase` -> `host=github.com` -> `protocol=https` -> [Enter 2 lần].

### PHASE 2: Core Implementation

**1. File `main.py` (The Engine):**
```python
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID_HERE")

def trigger_webhook(user_agent: str):
    """Feedback Loop: Bắn tín hiệu khi Target cắn câu"""
    url = f"[https://api.telegram.org/bot](https://api.telegram.org/bot){TELEGRAM_BOT_TOKEN}/sendMessage"
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
        "images": ["pic1.jpg"] 
    })