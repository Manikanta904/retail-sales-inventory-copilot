import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.api.routes import router

app = FastAPI(
    title="Retail: Sales and Inventory Copilot",
    description="Backend API for Retail Sales and Inventory Copilot",
    version="0.1.0",
)

# Include API Router
app.include_router(router)

# Mount production frontend build static files if frontend/dist exists
frontend_dist = os.path.join(os.path.dirname(__file__), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

