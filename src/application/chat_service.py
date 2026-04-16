import datetime
from src.domain.repositories import IProductRepository, IChatRepository
from src.application.dtos import ChatMessageRequestDTO, ChatMessageResponseDTO
from src.domain.entities import ChatMessage, ChatContext
from src.domain.exceptions import ProductNotFoundError
from typing import List
from src.services.gemini_service import GeminiService

class ChatService:
    """
    Servicio de aplicación para manejar la lógica del chat con IA.
    Recibe IProductRepository, IChatRepository y ai_service (GeminiService).
    """

    def __init__(self, product_repository: IProductRepository, chat_repository: IChatRepository, ai_service: GeminiService):
        """
        Constructor para inyectar el repositorio de productos, repositorio de chat y el servicio de IA.
        
        Args:
            product_repository (IProductRepository): Repositorio de productos
            chat_repository (IChatRepository): Repositorio de mensajes de chat
            ai_service (GeminiService): Servicio de IA (GeminiService)
        """
        self.product_repository = product_repository
        self.chat_repository = chat_repository
        self.ai_service = ai_service

    async def process_message(self, request: ChatMessageRequestDTO) -> ChatMessageResponseDTO:
        """
        Procesa el mensaje del usuario, obtiene productos, contexto y genera una respuesta de IA.
        
        Args:
            request (ChatMessageRequestDTO): Mensaje de la solicitud del usuario
        
        Returns:
            ChatMessageResponseDTO: Respuesta generada por el asistente
        """
        try:
            # Obtener los productos del repositorio
            products = self.product_repository.get_all()

            # Obtener el historial de mensajes (últimos 6 mensajes)
            session_history = self.get_session_history(request.session_id, 6)
            chat_context = ChatContext(messages=session_history, max_messages=6)

            # Llamar al servicio de IA para generar la respuesta
            user_message = request.message
            ai_response = await self.ai_service.generate_response(user_message, products, chat_context)

            # Guardar mensaje del usuario en el repositorio
            user_message_entity = ChatMessage(
                session_id=request.session_id,
                role="user",
                message=user_message,
                timestamp=datetime.datetime.utcnow()
            )
            self.chat_repository.save_message(user_message_entity)

            # Guardar respuesta del asistente en el repositorio
            assistant_message_entity = ChatMessage(
                session_id=request.session_id,
                role="assistant",
                message=ai_response,
                timestamp=datetime.datetime.utcnow()
            )
            self.chat_repository.save_message(assistant_message_entity)

            # Retornar la respuesta en formato DTO
            response_dto = ChatMessageResponseDTO(
                session_id=request.session_id,
                user_message=user_message,
                assistant_message=ai_response,
                timestamp=datetime.datetime.utcnow()
            )

            return response_dto

        except ProductNotFoundError as e:
            # Manejo de excepciones, si no se encuentran productos
            raise ValueError("No se encontraron productos para generar la respuesta.") from e
        except Exception as e:
            # Cualquier otro error inesperado
            raise ValueError("Error al procesar el mensaje del usuario.") from e

    def get_session_history(self, session_id: str, limit: int = 6) -> List[ChatMessage]:
        """
        Obtiene el historial de mensajes de una sesión.
        
        Args:
            session_id (str): ID de la sesión de chat
            limit (int): Número de mensajes a obtener (por defecto 6)
        
        Returns:
            List[ChatMessage]: Lista de mensajes de la sesión
        """
        return self.chat_repository.get_session_history(session_id, limit)

    def clear_session_history(self, session_id: str) -> int:
        """
        Elimina todo el historial de mensajes de una sesión.
        
        Args:
            session_id (str): ID de la sesión de chat
        
        Returns:
            int: Número de mensajes eliminados
        """
        return self.chat_repository.delete_session_history(session_id)