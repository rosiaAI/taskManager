from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500))
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Связь с пользователем
    owner = relationship("User", back_populates="tasks")