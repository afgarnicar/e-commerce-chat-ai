from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class Product:
    """
    Entidad que representa un producto en el e-commerce.
    Contiene la lógica de negocio relacionada con productos.
    """
    id: Optional[int]  # ID puede ser None para productos no guardados en la base de datos
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str
    
    def __post_init__(self):
        """Validaciones que se ejecutan después de crear el objeto.
        TODO: Implementar validaciones:
        - price debe ser mayor a 0
        - stock no puede ser negativo
        - name no puede estar vacío
        Lanza ValueError si alguna validación falla
        """
        if self.price <= 0:
            raise ValueError(f"El precio debe ser mayor a 0. Valor proporcionado: {self.price}")
        
        if self.stock < 0:
            raise ValueError(f"El stock no puede ser negativo. Valor proporcionado: {self.stock}")
        
        if not self.name.strip():
            raise ValueError("El nombre del producto no puede estar vacío.")
    
    def is_available(self) -> bool:
        """
        TODO: Retorna True si el producto tiene stock disponible
        """
        return self.stock > 0
    
    def reduce_stock(self, quantity: int) -> None:
        """
        TODO: Reduce el stock del producto
        - Valida que quantity sea positivo
        - Valida que haya suficiente stock
        - Lanza ValueError si no se puede reducir
        """
        if quantity <= 0:
            raise ValueError(f"La cantidad a reducir debe ser positiva. Valor proporcionado: {quantity}")
        
        if quantity > self.stock:
            raise ValueError(f"No hay suficiente stock. Stock actual: {self.stock}, cantidad solicitada: {quantity}")
        
        self.stock -= quantity
    
    def increase_stock(self, quantity: int) -> None:
        """
        TODO: Aumenta el stock del producto
        - Valida que quantity sea positivo
        """
        if quantity <= 0:
            raise ValueError(f"La cantidad a aumentar debe ser positiva. Valor proporcionado: {quantity}")
        
        self.stock += quantity

@dataclass
class ChatMessage:
    """
    Entidad que representa un mensaje en el chat.
"""
    id: Optional[int]
    session_id: str
    role: str  # 'user' o 'assistant'
    message: str
    timestamp: datetime

    def __post_init__(self):
        """
        TODO: Implementar validaciones:
        - role debe ser 'user' o 'assistant'
        - message no puede estar vacío
        - session_id no puede estar vacío
        """
        if self.role not in ['user', 'assistant']:
            raise ValueError(f"El rol debe ser 'user' o 'assistant'. Valor proporcionado: {self.role}")
        
        if not self.message.strip():
            raise ValueError("El mensaje no puede estar vacío.")
        
        if not self.session_id.strip():
            raise ValueError("El session_id no puede estar vacío.")
    
    def is_from_user(self) -> bool:
        """
        TODO: Retorna True si el mensaje es del usuario
        """
        return self.role == 'user'
    
    def is_from_assistant(self) -> bool:
        """
        TODO: Retorna True si el mensaje es del asistente
        """
        return self.role == 'assistant'
    
@dataclass
class ChatContext:
    """
    Value Object que encapsula el contexto de una conversación.
    Mantiene los mensajes recientes para dar coherencia al chat.
    """
    messages: list[ChatMessage]
    max_messages: int = 6
    
    def get_recent_messages(self) -> List[ChatMessage]:
        """
        TODO: Retorna los últimos N mensajes (max_messages)
        Pista: Usa slicing de Python messages[-self.max_messages:]
        """
        return self.messages[-self.max_messages:]
    
    def format_for_prompt(self) -> str:
        """
        TODO: Formatea los mensajes para incluirlos en el prompt de IA
        Formato esperado:
        "Usuario: mensaje del usuario
        Asistente: respuesta del asistente
        Usuario: otro mensaje
        ..."
        
        Pista: Itera sobre get_recent_messages() y construye el string
        """
        formatted_messages = []
        
        for message in self.get_recent_messages():
            role = "Usuario" if message.is_from_user() else "Asistente"
            formatted_messages.append(f"{role}: {message.message}")
        
        return "\n".join(formatted_messages)
