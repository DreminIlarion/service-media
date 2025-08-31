from fastapi import FastAPI
from api.images import router as images_router

app = FastAPI()

app.include_router(images_router, prefix="/api", tags=["images"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)