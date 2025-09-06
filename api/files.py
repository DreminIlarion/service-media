import logging
from typing import Dict
from uuid import UUID
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Path as FastAPIPath, status
from sqlalchemy.orm import Session
from botocore.exceptions import NoCredentialsError, ClientError
from database import get_db
from schemas import UploadResponse, FileWithMetadataResponse, FileMetadataCreate
from services import FileService
from config import s3_client, S3_BUCKET


logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Загружает файл в S3 хранилище и сохраняет метаданные в БД.
    """
    try:
        file_size = file.size
        content_type = file.content_type or "application/octet-stream"
        file_format = file.filename.split('.')[-1] if '.' in file.filename else ""

        s3_client.upload_fileobj(
            file.file,
            S3_BUCKET,
            file.filename,
            ExtraArgs={"ContentType": content_type}
        )

        file_metadata = FileMetadataCreate(
            file_name=file.filename,
            key=file.filename,
            bucket=S3_BUCKET,
            size=file_size,
            format=file_format,
            file_type=content_type
        )

        FileService.create_file_metadata(db, file_metadata)

        return {
            "message": "Файл успешно загружен",
            "filename": file.filename
        }

    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="Ошибка доступа к S3: неверные ключи")
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"Ошибка S3: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка: {str(e)}")

@router.get("/", response_model=Dict[str, FileWithMetadataResponse])
def get_all_files_with_metadata(db: Session = Depends(get_db)):
    """
    Возвращает все файлы.
    """
    try:
        files = FileService.get_files_by_bucket(db, S3_BUCKET)

        result = {}
        for file in files:
            try:
                url = s3_client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": S3_BUCKET, "Key": file.file_name},
                    ExpiresIn=3600
                )
                url = url.replace("http://minio:9000/", "http://localhost:9000/")
            except ClientError:
                url = None

            result[str(file.id)] = FileWithMetadataResponse(
                id=file.id,
                filename=file.file_name,
                size=file.size,
                format=file.format,
                type=file.file_type,
                uploaded_date=file.uploaded_date,
                url=url
            )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении файлов: {str(e)}")

@router.get("/{file_id}", response_model=FileWithMetadataResponse)
def get_file_by_id(file_id: UUID = FastAPIPath(..., description="UUID файла"), db: Session = Depends(get_db)):
    """
    Возвращает файл по ID.
    """
    try:
        file = FileService.get_file_by_id(db, str(file_id))

        if not file:
            raise HTTPException(status_code=404, detail="Файл не найден")

        try:
            url = s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": S3_BUCKET, "Key": file.file_name},
                ExpiresIn=3600
            )
            url = url.replace("http://minio:9000/", "http://localhost:9000/")
        except ClientError:
            url = None

        return FileWithMetadataResponse(
            id=file.id,
            filename=file.file_name,
            size=file.size,
            format=file.format,
            type=file.file_type,
            uploaded_date=file.uploaded_date,
            url=url
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении файла: {str(e)}")

@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file_by_id(file_id: UUID = FastAPIPath(..., description="UUID файла"), db: Session = Depends(get_db)):
    """
    Удалить файл по ID.
    Удаляет как метаданные из БД, так и файл из S3 хранилища.
    """
    try:
        file = FileService.get_file_by_id(db, str(file_id))

        if not file:
            raise HTTPException(status_code=404, detail="Файл не найден")

        # Удаляем из S3
        s3_success = FileService.delete_file_from_s3(file.key)
        if not s3_success:
            logger.warning(f"Не удалось удалить файл из S3: {file.key}")

        # Удаляем метаданные из БД
        db_success = FileService.delete_file_metadata(db, str(file_id))
        if not db_success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при удалении метаданных файла"
            )
        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении файла: {str(e)}"
        )