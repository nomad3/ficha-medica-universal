from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Primero crear la instancia de app
app = FastAPI(title="API Ficha Médica Nutricional")

# Luego agregar el middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... resto del código de rutas ... 