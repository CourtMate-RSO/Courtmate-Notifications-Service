from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.config import get_settings
from app.routes import router as notifications_router
from app.scheduler import start_scheduler, shutdown_scheduler
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()

NOTIFICATIONS_PREFIX = f"/api/{settings.api_version}/notifications"

if settings.env=="prod":
    # Create FastAPI application
    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        description=settings.api_description,
        openapi_url=None,
        docs_url=None,
        redoc_url=None,
        
    )
else:
    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        description=settings.api_description,
        openapi_url=f"{NOTIFICATIONS_PREFIX}/openapi.json",
        docs_url=f"{NOTIFICATIONS_PREFIX}/docs",
        redoc_url=f"{NOTIFICATIONS_PREFIX}/redoc",
        
    )

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(notifications_router, prefix=NOTIFICATIONS_PREFIX)


# Startup event to start the scheduler
@app.on_event("startup")
async def startup_event():
    """Start the background scheduler on application startup"""
    logger.info("Starting notification service...")
    start_scheduler()
    logger.info("Scheduler initialized")


# Shutdown event to stop the scheduler
@app.on_event("shutdown")
async def shutdown_event():
    """Stop the background scheduler on application shutdown"""
    logger.info("Shutting down notification service...")
    shutdown_scheduler()
    logger.info("Scheduler stopped")


# Custom exception handler for validation errors (UUID parsing, etc.)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors (like invalid UUID format) and return 400 instead of 422.
    This makes the API more consistent with REST conventions.
    """
    errors = exc.errors()
    
    # Check if it's a UUID validation error in path parameters
    for error in errors:
        if error.get("type") == "uuid_parsing" and "path" in error.get("loc", []):
            # Return 400 Bad Request for invalid UUID in path
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "detail": f"Invalid UUID format: {error.get('input', 'unknown')}"
                }
            )
    
    # For other validation errors, return 422 (default behavior)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": errors}
    )


logger.info(f"Notification Service started in {settings.env} mode")
logger.info(f"API available at: {NOTIFICATIONS_PREFIX}")


@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "service": "Notification Service",
        "version": settings.api_version,
        "status": "running"
    }


@app.get("/health", tags=["health"])
async def health():
    """Health check endpoint"""

    return {
        "status": "healthy",
        "service": "notification-service"
    }
