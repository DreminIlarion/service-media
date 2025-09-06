from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID, uuid4
from datetime import datetime
import logging
from models import FileMetadataOrm
from schemas import FileMetadataCreate
from fastapi import HTTPException, UploadFile
import filetype
from config import s3_client, S3_BUCKET
from pathlib import Path

logger = logging.getLogger(__name__)

class FileService:
    @staticmethod
    def create_file_metadata(db: Session, file_data: FileMetadataCreate) -> FileMetadataOrm:
        """Создает запись с метаданными файла в БД."""
        try:
            db_file = FileMetadataOrm(
                id=uuid4(),
                file_name=file_data.file_name,
                key=file_data.key,
                bucket=file_data.bucket,
                size=file_data.size,
                format=file_data.format,
                file_type=file_data.file_type,
                uploaded_date=datetime.utcnow()
            )
            db.add(db_file)
            db.commit()
            db.refresh(db_file)
            return db_file
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Ошибка базы данных при сохранении метаданных файла: {e}")
            raise HTTPException(status_code=500, detail="Ошибка базы данных")
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при сохранении метаданных файла: {e}")
            raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

    @staticmethod
    def get_files_by_bucket(db: Session, bucket: str) -> List[FileMetadataOrm]:
        """Получает все файлы в указанном бакете."""
        try:
            return db.query(FileMetadataOrm).filter(FileMetadataOrm.bucket == bucket).all()
        except Exception as e:
            logger.error(f"Ошибка при получении файлов по бакету {bucket}: {e}")
            raise HTTPException(status_code=500, detail="Ошибка при получении файлов")

    @staticmethod
    def get_file_by_id(db: Session, file_id: UUID) -> Optional[FileMetadataOrm]:
        """Получает файл по идентификатору."""
        try:
            return db.query(FileMetadataOrm).filter(FileMetadataOrm.id == file_id).first()
        except Exception as e:
            logger.error(f"Ошибка при получении файла по ID {file_id}: {e}")
            raise HTTPException(status_code=500, detail="Ошибка при получении файла")

    @staticmethod
    def delete_file_metadata(db: Session, file_id: str) -> bool:
        """Удаляет метаданные файла из БД."""
        try:
            file_id_uuid = UUID(file_id)
            db_file = db.query(FileMetadataOrm).filter(FileMetadataOrm.id == file_id_uuid).first()
            if not db_file:
                return False
            db.delete(db_file)
            db.commit()
            return True
        except ValueError:
            logger.error(f"Неверный формат UUID: {file_id}")
            raise HTTPException(status_code=400, detail="Неверный формат идентификатора")
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Ошибка базы данных при удалении: {e}")
            raise HTTPException(status_code=500, detail="Ошибка базы данных")
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при удалении: {e}")
            raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

    @staticmethod
    def get_file_metadata(file: UploadFile) -> Tuple[int, str, str]:
        """Получение метаданных файла."""
        content = file.file.read()
        file_size = len(content)
        file_info = filetype.guess(content)
        content_type = file_info.mime if file_info else file.content_type or "application/octet-stream"
        file_format = file_info.extension if file_info else Path(file.filename).suffix[1:] or "bin"
        file.file.seek(0)  # Сбрасываем указатель файла
        return file_size, content_type, file_format

    @staticmethod
    def delete_file_from_s3(file_key: str) -> bool:
        """Удаляет файл из S3 хранилища."""
        try:
            s3_client.delete_object(Bucket=S3_BUCKET, Key=file_key)
            return True
        except Exception as e:
            logger.error(f"Ошибка при удалении файла из S3: {e}")
            return False