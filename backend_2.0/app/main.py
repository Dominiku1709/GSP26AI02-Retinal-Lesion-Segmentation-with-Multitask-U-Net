# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import logging

# Configure logging to see GPU initialization messages
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Internal imports - using relative dots because they are in the same package
from .api.endpoints import router as api_router
from .database import engine
from . import models

# 1. Create the Database tables on startup
# This is the "Magic" line that creates oct_app.db and your tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="OCT Analysis Backend")

# 2. Configure CORS
# This allows your Frontend guy to talk to your Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev, allow all. For prod, use ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Create storage directory if it doesn't exist
if not os.path.exists("storage"):
    os.makedirs("storage")

# 4. Mount the storage folder so images are accessible via URL
# Example: http://127.0.0.1:8000/images/test.png
app.mount("/images", StaticFiles(directory="storage"), name="images")

# 5. Include your API routes
app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "OCT Analysis API is running. Go to /docs for Swagger."}