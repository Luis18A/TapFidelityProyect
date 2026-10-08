from fastapi import APIRouter
from fastapi.responses import FileResponse
import os

router = APIRouter(tags=["Views"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@router.get("/")
@router.get("/client")
@router.get("/tap")
def client_pwa_view():
    return FileResponse(os.path.join(BASE_DIR, "views", "client", "index.html"))

@router.get("/admin")
def admin_login_view():
    return FileResponse(os.path.join(BASE_DIR, "views", "admin", "login.html"))

@router.get("/admin/dashboard")
def admin_dashboard_view():
    return FileResponse(os.path.join(BASE_DIR, "views", "admin", "dashboard.html"))
