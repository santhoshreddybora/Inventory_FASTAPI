from fastapi import FastAPI
from app.databases import Base, engine  # make sure these are correctly imported
from contextlib import asynccontextmanager
from app import models
from app.routers import products,orders,webhook
from sqlalchemy import inspect
import uvicorn
import os
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup code: Create all tables
    inspect_tables=inspect(engine)
    # Base.metadata.drop_all(bind=engine)
    if not inspect_tables.get_table_names():
        print("Creating tables...")
        # Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
    yield  # This will pause here while the app is running
    print("Shutting down...")

# Assign the lifespan context manager to the FastAPI app
app = FastAPI(title="Inventory Management API",lifespan=lifespan)

app.include_router(products.router)
app.include_router(orders.router)
app.include_router(webhook.router)
# Your routes can go here
@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI app!"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Render provides PORT dynamically
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)