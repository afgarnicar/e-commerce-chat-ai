from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.infrastructure.db.database import Base

class ProductModel(Base):
    """
    Modelo ORM para la tabla 'products'.
    """
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    brand = Column(String(100))
    category = Column(String(100))
    size = Column(String(20))
    color = Column(String(50))
    price = Column(Float)
    stock = Column(Integer)
    description = Column(Text)

    def __repr__(self):
        return f"<Product(name={self.name}, brand={self.brand}, price={self.price})>"

class ChatMemoryModel(Base):
    """
    Modelo ORM para la tabla 'chat_memory'.
    """
    __tablename__ = 'chat_memory'

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    role = Column(String(20))
    message = Column(Text)
    timestamp = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<ChatMessage(session_id={self.session_id}, role={self.role})>"