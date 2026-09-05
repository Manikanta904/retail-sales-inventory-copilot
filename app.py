import uvicorn
from fastapi import FastAPI
from backend.api.routes import router

app = FastAPI(
    title="Retail: Sales and Inventory Copilot",
    description="Backend API for Retail Sales and Inventory Copilot",
    version="0.1.0",
)

# Include API Router
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
