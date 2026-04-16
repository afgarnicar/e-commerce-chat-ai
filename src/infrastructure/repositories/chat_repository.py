from sqlalchemy.orm import Session
from src.domain.repositories import IChatRepository
from src.infrastructure.db.models import ChatMemoryModel
from src.domain.entities import ChatMessage
from typing import List

class SQLChatRepository(IChatRepository):
    def __init__(self, db: Session):
        self.db = db

    def save_message(self, message: ChatMessage) -> ChatMessage:
        """Guarda un mensaje en el historial de chat."""
        message_model = self._entity_to_model(message)
        self.db.add(message_model)
        self.db.commit()
        self.db.refresh(message_model)
        return self._model_to_entity(message_model)

    def get_session_history(self, session_id: str, limit: int = 6) -> List[ChatMessage]:
        """Obtiene el historial completo de una sesión de chat."""
        message_models = (
            self.db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .order_by(ChatMemoryModel.timestamp.desc())
            .limit(limit)
            .all()
        )
        return [self._model_to_entity(model) for model in message_models]

    def delete_session_history(self, session_id: str) -> int:
        """Elimina el historial de una sesión de chat."""
        deleted_count = (
            self.db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .delete()
        )
        self.db.commit()
        return deleted_count

    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessage]:
        """Obtiene los últimos N mensajes de una sesión de chat."""
        message_models = (
            self.db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .order_by(ChatMemoryModel.timestamp.desc())
            .limit(count)
            .all()
        )
        messages = [self._model_to_entity(model) for model in message_models]
        messages.reverse()  # Orden cronológico
        return messages

    def _model_to_entity(self, model: ChatMemoryModel) -> ChatMessage:
        """Convierte un modelo ORM a una entidad del dominio."""
        return ChatMessage(
            id=model.id,          # ← faltaba este campo
            session_id=model.session_id,
            role=model.role,
            message=model.message,
            timestamp=model.timestamp
        )

    def _entity_to_model(self, entity: ChatMessage) -> ChatMemoryModel:
        """Convierte una entidad del dominio a un modelo ORM."""
        return ChatMemoryModel(
            session_id=entity.session_id,
            role=entity.role,
            message=entity.message,
            timestamp=entity.timestamp
        )