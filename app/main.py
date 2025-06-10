from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.api.v1 import admin as admin_router
from app.api.v1 import auth as auth_router
from app.api.v1 import courses as courses_router
from app.database.session import engine
from app.models import user as user_model
from app.models import course as course_model
from app.models import lecture as lecture_model
from app.models import user_course as user_course_model

# Create all tables
user_model.Base.metadata.create_all(bind=engine)
course_model.Base.metadata.create_all(bind=engine)
lecture_model.Base.metadata.create_all(bind=engine)
user_course_model.Base.metadata.create_all(bind=engine)

# Initialize app
app = FastAPI(
    title="Finanizr Admin API",
    version="1.0.0"
)

# CORS (optional but recommended)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://www.finanastrology.com",
        "https://finanastrology.com",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Type",
        "Origin",
        "Referer",
        "User-Agent",
        "Authorization",
        "X-Requested-With",
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Methods",
        "Access-Control-Allow-Credentials"
    ],
    expose_headers=["*"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Include routes
app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(admin_router.router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(courses_router.router, prefix="/api/v1", tags=["Courses"])

# Add Bearer token support in Swagger UI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
