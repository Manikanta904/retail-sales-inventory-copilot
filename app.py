import uvicorn
from fastapi import FastAPI

app = FastAPI(
    title="Retail: Sales and Inventory Copilot",
    description="Backend API for Retail Sales and Inventory Copilot",
    version="0.1.0",
)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Service is healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
