from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database.session import Base

class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_order=True, primary_key=True, index=True)
    jti = Column(String(64), unique=True, index=True, nullable=False)
    token_type = Column(String(20), nullable=False)  # 'access' or 'refresh'
    revoked_at = Column(DateTime, default=datetime.utcnow)
