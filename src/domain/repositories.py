from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import Product, ChatMessage


class IProductRepository(ABC):
    """
    Interface que define el contrato para acceder a productos.
    Las implementaciones concretas estarán en la capa de infraestructura.
    """

    @abstractmethod
    def get_all(self) -> List[Product]:
        """
        Obtiene todos los productos disponibles.
        Retorna una lista de todos los productos en el inventario.
        """
        pass

    @abstractmethod
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """
        Obtiene un producto por su ID.
        Si el producto no existe, retorna None.
        """
        pass

    @abstractmethod
    def get_by_brand(self, brand: str) -> List[Product]:
        """
        Obtiene productos de una marca específica.
        Retorna todos los productos que pertenecen a la marca proporcionada.
        """
        pass

    @abstractmethod
    def get_by_category(self, category: str) -> List[Product]:
        """
        Obtiene productos de una categoría específica.
        Retorna todos los productos que pertenecen a la categoría proporcionada.
        """
        pass

    @abstractmethod
    def save(self, product: Product) -> Product:
        """
        Guarda o actualiza un producto en la base de datos.
        Si el producto tiene ID, se actualiza. Si no tiene ID, se crea uno nuevo.
        """
        pass

    @abstractmethod
    def delete(self, product_id: int) -> bool:
        """
        Elimina un producto de la base de datos por su ID.
        Si el producto existe, se elimina y retorna True. Si no existe, retorna False.
        """
        pass


class IChatRepository(ABC):
    """
    Interface para gestionar el historial de conversaciones.
    """

    @abstractmethod
    def save_message(self, message: ChatMessage) -> ChatMessage:
        """
        Guarda un mensaje en el historial.
        Retorna el mensaje guardado con su ID asignado.
        """
        pass

    @abstractmethod
    def get_session_history(self, session_id: str, limit: Optional[int] = None) -> List[ChatMessage]:
        """
        Obtiene el historial de una sesión.
        Si limit está definido, retorna solo los últimos N mensajes en orden cronológico.
        """
        pass

    @abstractmethod
    def delete_session_history(self, session_id: str) -> int:
        """
        Elimina todo el historial de una sesión.
        Retorna la cantidad de mensajes eliminados.
        """
        pass

    @abstractmethod
    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessage]:
        """
        Obtiene los últimos N mensajes de una sesión en orden cronológico.
        Crucial para mantener el contexto conversacional.
        """
        pass