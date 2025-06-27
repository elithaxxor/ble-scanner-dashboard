from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import config

router = APIRouter()
templates = Jinja2Templates(directory="web/templates")


@router.get("/ping")
async def ping():
    return {"status": "ok"}


@router.get("/config", response_class=HTMLResponse)
async def get_config(request: Request):
    return templates.TemplateResponse(
        "config.html",
        {"request": request, "config": config},
    )


@router.post("/config")
async def set_config(
    request: Request,
    scan_interval: int = Form(...),
    discord: str = Form(""),
    telegram_token: str = Form(""),
    telegram_chat: str = Form(""),
):
    config.SCAN_INTERVAL = int(scan_interval)
    config.DISCORD_WEBHOOK_URL = discord
    config.TELEGRAM_BOT_TOKEN = telegram_token
    config.TELEGRAM_CHAT_ID = telegram_chat
    return RedirectResponse(url="/config", status_code=303)

