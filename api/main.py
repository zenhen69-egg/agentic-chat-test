from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers.chat import router as chat_router

app = FastAPI(title="Agentic Chat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "https://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
