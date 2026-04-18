from datetime import datetime, timezone
from typing import List

from src.application.dtos import ChatHistoryDTO, ChatMessageRequestDTO, ChatMessageResponseDTO
from src.domain.entities import ChatContext, ChatMessage
from src.domain.exceptions import ChatServiceError
from src.domain.repositories import IChatRepository, IProductRepository
from src.infrastructure.llm_providers.gemini_service import GeminiService


class ChatService:
    """
    Servicio de aplicación para gestionar el chat con IA.

    Este servicio coordina:
    - Repositorio de productos
    - Repositorio de historial de chat
    - Servicio de IA (Gemini)

    Su responsabilidad principal es construir el contexto conversacional,
    solicitar una respuesta al modelo y persistir la conversación.
    """

    def __init__(
        self,
        product_repository: IProductRepository,
        chat_repository: IChatRepository,
        ai_service: GeminiService,
    ) -> None:
        """
        Inicializa el servicio de chat con sus dependencias.

        Args:
            product_repository (IProductRepository): Repositorio de productos.
            chat_repository (IChatRepository): Repositorio de mensajes de chat.
            ai_service (GeminiService): Servicio de IA para generar respuestas.
        """
        self.product_repository = product_repository
        self.chat_repository = chat_repository
        self.ai_service = ai_service

    async def process_message(
        self,
        request: ChatMessageRequestDTO,
    ) -> ChatMessageResponseDTO:
        """
        Procesa un mensaje del usuario y genera una respuesta usando IA.

        Flujo:
        1. Obtiene todos los productos
        2. Recupera historial reciente
        3. Construye el contexto conversacional
        4. Solicita respuesta al servicio Gemini
        5. Guarda mensaje del usuario
        6. Guarda respuesta del asistente
        7. Retorna DTO de respuesta

        Args:
            request (ChatMessageRequestDTO): Mensaje entrante del usuario.

        Returns:
            ChatMessageResponseDTO: Respuesta final del asistente.

        Raises:
            ChatServiceError: Si ocurre un error durante el proceso.
        """
        try:
            products = self.product_repository.get_all()

            session_history = self.chat_repository.get_recent_messages(
                request.session_id,
                6,
            )
            chat_context = ChatContext(messages=session_history, max_messages=6)

            user_message = request.message
            assistant_response = await self.ai_service.generate_response(
                user_message=user_message,
                products=products,
                context=chat_context,
            )

            current_timestamp = datetime.now(timezone.utc)

            user_message_entity = ChatMessage(
                id=None,
                session_id=request.session_id,
                role="user",
                message=user_message,
                timestamp=current_timestamp,
            )
            self.chat_repository.save_message(user_message_entity)

            assistant_message_entity = ChatMessage(
                id=None,
                session_id=request.session_id,
                role="assistant",
                message=assistant_response,
                timestamp=current_timestamp,
            )
            self.chat_repository.save_message(assistant_message_entity)

            return ChatMessageResponseDTO(
                session_id=request.session_id,
                user_message=user_message,
                assistant_message=assistant_response,
                timestamp=current_timestamp,
            )

        except Exception as exc:
            raise ChatServiceError(
                f"Error al procesar el mensaje del chat: {exc}"
            ) from exc

    def get_session_history(
        self,
        session_id: str,
        limit: int = 10,
    ) -> List[ChatHistoryDTO]:
        """
        Obtiene el historial de una sesión de chat.

        Args:
            session_id (str): Identificador de la sesión.
            limit (int, optional): Número máximo de mensajes a recuperar.
                Defaults to 10.

        Returns:
            List[ChatHistoryDTO]: Historial formateado como DTOs.
        """
        messages = self.chat_repository.get_session_history(session_id, limit)

        return [
            ChatHistoryDTO(
                id=message.id,
                role=message.role,
                message=message.message,
                timestamp=message.timestamp,
            )
            for message in messages
        ]

    def clear_session_history(self, session_id: str) -> int:
        """
        Elimina todo el historial de una sesión.

        Args:
            session_id (str): Identificador de la sesión.

        Returns:
            int: Cantidad de mensajes eliminados.
        """
        return self.chat_repository.delete_session_history(session_id)