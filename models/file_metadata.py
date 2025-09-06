from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from database import Base

class FileMetadataOrm(Base):
    __tablename__ = "file_metadata"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    key: Mapped[str] = mapped_column(String(255), nullable=False)
    bucket: Mapped[str] = mapped_column(String(100), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)  
    format: Mapped[str] = mapped_column(String(10), nullable=False)
    file_type: Mapped[str] = mapped_column(String(100), nullable=False)
    uploaded_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)