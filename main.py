from fastapi import FastAPI
from api.files import router as images_router
from database import engine
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(images_router, prefix="/api/files", tags=["files"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)