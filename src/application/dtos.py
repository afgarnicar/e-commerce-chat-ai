from pydantic import BaseModel, field_validator, model_validator
from pydantic import ConfigDict
from typing import Optional
from datetime import datetime


class ProductDTO(BaseModel):
    """
    DTO para transferir datos de productos.
    Pydantic V2 valida automáticamente los tipos.
    """
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str

    @field_validator('price')
    @classmethod
    def price_must_be_positive(cls, v: float) -> float:
        """Valida que el precio sea mayor a 0"""
        if v <= 0:
            raise ValueError('El precio debe ser mayor a 0')
        return v

    @field_validator('stock')
    @classmethod
    def stock_must_be_non_negative(cls, v: int) -> int:
        """Valida que el stock no sea negativo"""
        if v < 0:
            raise ValueError('El stock no puede ser negativo')
        return v


class ChatMessageRequestDTO(BaseModel):
    """DTO para recibir mensajes del usuario"""
    session_id: str
    message: str

    @field_validator('message')
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        """Valida que el mensaje no esté vacío"""
        if not v.strip():
            raise ValueError('El mensaje no puede estar vacío')
        return v

    @field_validator('session_id')
    @classmethod
    def session_id_not_empty(cls, v: str) -> str:
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
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    message: str
    timestamp: datetime