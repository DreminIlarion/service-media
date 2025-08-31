from fastapi import APIRouter, UploadFile, File, HTTPException
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import os
from schemas.image import UploadResponse

router = APIRouter()


AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "ru")
S3_BUCKET = os.getenv("S3_BUCKET", "my-image-bucket")
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")  

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION,
    endpoint_url=S3_ENDPOINT_URL
)

@router.post("/upload", response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...)):
    """
    Загружает изображение в S3-совместимое хранилище.
    """
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        raise HTTPException(status_code=400, detail="Недопустимый тип файла изображения")
    
    try:
        s3_client.upload_fileobj(
            file.file,
            S3_BUCKET,
            file.filename,
            ExtraArgs={"ContentType": file.content_type}
        )
        return {"message": "Изображение успешно загружено", "filename": file.filename}
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="Ошибка доступа к S3: неверные ключи")
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"Ошибка S3: {str(e)}")

@router.get("/images/{filename}")
async def get_image(filename: str):
    """
    Получает временную ссылку для доступа к изображению в S3.
    """
    try:
        url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET, "Key": filename},
            ExpiresIn=3600
        )

        return {"url": url}
    except ClientError as e:
        if ClientError.response['Error']['Code'] == '404':
            raise HTTPException(status_code=404, detail="Изображение не найдено")
        raise HTTPException(status_code=500, detail=f"Ошибка S3: {str(e)}")