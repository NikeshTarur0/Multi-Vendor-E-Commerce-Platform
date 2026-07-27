import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.config import settings
from app.middleware.timing import setup_middlewares
from app.database.session import engine, Base, SessionLocal
from app.utils.seed_data import seed_database

# API Routers
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.vendors import router as vendors_router
from app.api.products import router as products_router
from app.api.orders import router as orders_router
from app.api.coupons import router as coupons_router
from app.api.wishlist import router as wishlist_router
from app.api.reviews import router as reviews_router
from app.api.admin import router as admin_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Multi-Vendor E-Commerce Platform API with JWT Auth, Vendor Storefronts, Cart & Order Splitting, Coupons, Reviews, Wishlist, and Mock Payments.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Setup Middlewares
setup_middlewares(app)

# Include Routers under /api
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(vendors_router, prefix="/api")
app.include_router(products_router, prefix="/api")
app.include_router(orders_router, prefix="/api")
app.include_router(coupons_router, prefix="/api")
app.include_router(wishlist_router, prefix="/api")
app.include_router(reviews_router, prefix="/api")
app.include_router(admin_router, prefix="/api")

# Static files setup
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.on_event("startup")
def startup_event():
    # Ensure database schema is created
    Base.metadata.create_all(bind=engine)
    # Seed initial demo data
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

@app.get("/")
def read_root():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Multi-Vendor E-Commerce Platform API is running. Visit /docs for OpenAPI documentation."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
