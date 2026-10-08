import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.config.database import init_db
from app.routes.client_routes import router as client_router
from app.routes.admin_routes import router as admin_router
from app.routes.view_routes import router as view_router

# Inicializar Base de Datos SQLite
init_db()

app = FastAPI(
    title="Sistema de Fidelización Physical-Digital",
    description="Solución MVC para tarjetas de fidelización con NFC/QR, PWA y Antifraude de 12 horas",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Montar directorios estáticos
app.mount("/views", StaticFiles(directory=os.path.join(BASE_DIR, "app", "views")), name="views")
app.mount("/public", StaticFiles(directory=os.path.join(BASE_DIR, "public")), name="public")

# Registrar Enrutadores MVC
app.include_router(client_router)
app.include_router(admin_router)
app.include_router(view_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)
