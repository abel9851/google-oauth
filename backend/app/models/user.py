from app.db.database import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    google_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    picture = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    # OAuth specific fields
    encrypted_refresh_token = Column(Text, nullable=True)
    refresh_token_iv = Column(
        String, nullable=True
    )  # Initialization vector for AES-GCM
    refresh_token_tag = Column(String, nullable=True)  # Authentication tag for AES-GCM
    refresh_token_expires_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
