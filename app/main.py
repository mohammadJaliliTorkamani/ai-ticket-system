from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.logger import logger
from app.db.mongodb import db
from app.routes import auth_routes

app = FastAPI(title="Welcome to AI Ticket Backend!")
app.include_router(auth_routes.router)


@app.get("/health")
async def health_check():
    collections = await db.list_collection_names()
    return {
        "status": "OK",
        "collections": collections
    }


# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error on {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
