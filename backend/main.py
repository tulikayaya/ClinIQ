from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import chat, retrieve, convert, segment, features, images, upload

app = FastAPI(title="ClinIQ API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router,     prefix="/chat",     tags=["chat"])
app.include_router(retrieve.router, prefix="/retrieve", tags=["retrieve"])
app.include_router(convert.router,  prefix="/convert",  tags=["convert"])
app.include_router(segment.router,  prefix="/segment",  tags=["segment"])
app.include_router(features.router, prefix="/features", tags=["features"])
app.include_router(images.router,   prefix="/images",   tags=["images"])
app.include_router(upload.router,   prefix="/upload",   tags=["upload"])


@app.get("/health")
def health():
    return {"status": "ok"}
