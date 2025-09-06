from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

class FileMetadataBase(BaseModel):
    file_name: str = Field(..., description="Имя файла")
    key: str = Field(..., description="Ключ в S3")
    bucket: str = Field(..., description="Имя бакета")
    size: int = Field(..., description="Размер файла в байтах")
    format: str = Field(..., description="Расширение файла")
    file_type: str = Field(..., description="MIME тип файла")

class FileMetadataCreate(FileMetadataBase):
    pass

class FileMetadata(FileMetadataBase):
    id: UUID
    uploaded_date: datetime
    
    class Config:
        from_attributes = True

class UploadResponse(BaseModel):
    message: str
    filename: str

class UrlImage(BaseModel):
    url: str

class FileWithMetadataResponse(BaseModel):
    id: UUID
    filename: str
    size: int
    format: str
    type: str
    uploaded_date: datetime
    url: Optional[str] = None
