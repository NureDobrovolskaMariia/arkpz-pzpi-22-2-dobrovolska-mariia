from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class UserIncubator(Base):
    __tablename__ = 'user_incubator'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    incubator_id = Column(Integer, ForeignKey("incubators.incubator_id"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="user_incubators")
    incubator = relationship("Incubator", back_populates="user_incubators")
