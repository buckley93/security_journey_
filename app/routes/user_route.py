from fastapi import Request, APIRouter, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database import SessionLocal
from starlette.middleware.sessions import SessionMiddleware
from app import app
import os
from app.services.user_service import UserServices
from sqlalchemy.ext.asyncio import AsyncSession

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))


async def get_db():
    async with SessionLocal() as db:
        yield db

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    if 'email' in request.session:
        return RedirectResponse(url="/product", status_code=302)
    if 'flash_messages' in request.session:
        flash_messages = request.session['flash_messages']
        del request.session['flash_messages']
    return templates.TemplateResponse("register.html", {"request": request, "title": "Home Page", "flash_messages": flash_messages if 'flash_messages' in locals() else None})

@router.post("/register")
async def create_user(request: Request, db: AsyncSession = Depends(get_db)):
    form = await request.form()
    email = form.get('email')
    if not email or not form.get('password'):
        return RedirectResponse(url="/", status_code=400)
    if 'email' in request.session:
        return RedirectResponse(url="/product", status_code=302)
    user_service = UserServices(db)
    new_user = await user_service.create_user({"email": email, "password": form.get('password')}, request)
    if new_user is None:
        return RedirectResponse(url="/", status_code=302)
    request.session['email'] = email
    return RedirectResponse(url="/product", status_code=302)

@router.post("/login")
async def login(request: Request, db: AsyncSession = Depends(get_db)):
    form = await request.form()
    email = form.get('email')
    if not email or not form.get('password'):
        return RedirectResponse(url="/", status_code=400)
    if 'email' in request.session:
        return RedirectResponse(url="/product", status_code=302)
    user_service = UserServices(db)

    user = await user_service.get_user_by_email(email, request)
    if user is None:
        return RedirectResponse(url="/", status_code=302)
    request.session['email'] = email
    return RedirectResponse(url="/product", status_code=302)

@router.post("/clear_email")
async def clear_email(request: Request):
    del request.session['email']
    return RedirectResponse(url="/product", status_code=302)