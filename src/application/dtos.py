from pydantic import BaseModel, validator
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class ProductDTO(BaseModel):
    """
    DTO para transferir datos de productos.
    Pydantic valida automáticamente los tipos.
    """
    id: Optional[int] = None
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str
    
    @validator('price')
    def price_must_be_positive(cls, v):
        """Valida que el precio sea mayor a 0"""
        if v <= 0:
            raise ValueError('El precio debe ser mayor a 0')
        return v
    
    @validator('stock')
    def stock_must_be_non_negative(cls, v):
        """Valida que el stock no sea negativo"""
        if v < 0:
            raise ValueError('El stock no puede ser negativo')
        return v
    
    class Config:
        from_attributes = True  # Permite crear desde objetos ORM

class ChatMessageRequestDTO(BaseModel):
    """DTO para recibir mensajes del usuario"""
    session_id: str
    message: str
    
    @validator('message')
    def message_not_empty(cls, v):
        """Valida que el mensaje no esté vacío"""
        if not v.strip():
            raise ValueError('El mensaje no puede estar vacío')
        return v
    
    @validator('session_id')
    def session_id_not_empty(cls, v):
        """Valida que session_id no esté vacío"""
        if not v.strip():
            raise ValueError('El ID de sesión no puede estar vacío')
        return v

class ChatMessageResponseDTO(BaseModel):
    """DTO para enviar respuestas del chat"""
    session_id: str
    user_message: str
    assistant_message: str
    timestamp: datetime

class ChatHistoryDTO(BaseModel):
    """DTO para mostrar historial de chat"""
    id: int
    role: str
    message: str
    timestamp: datetime
    
    class Config:
        from_attributes = True
