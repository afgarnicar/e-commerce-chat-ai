import unittest
from unittest.mock import MagicMock
from src.infrastructure.repositories.chat_repository import SQLChatRepository
from src.domain.entities import ChatMessage
from src.infrastructure.db.models import ChatMemoryModel
from sqlalchemy.orm import Session
import datetime


class TestSQLChatRepository(unittest.TestCase):
    """Pruebas para el repositorio de chat SQL"""

    def setUp(self):
        """Configura el entorno antes de cada prueba"""
        self.db_mock = MagicMock(spec=Session)
        self.chat_repository = SQLChatRepository(self.db_mock)

    def _make_message(self, id=1):
        return ChatMessage(
            id=id,
            session_id="session1",
            role="user",
            message="Hola",
            timestamp=datetime.datetime.now(datetime.UTC)
        )

    def _make_model(self, id=1):
        return ChatMemoryModel(
            id=id,
            session_id="session1",
            role="user",
            message="Hola",
            timestamp=datetime.datetime.now(datetime.UTC)
        )

    def test_save_message(self):
        """Prueba para guardar un mensaje"""
        message = self._make_message()

        self.db_mock.add.return_value = None
        self.db_mock.commit.return_value = None

        # refresh no hace nada realmente en el mock, pero el modelo ya tiene id
        def set_id(model):
            model.id = 1
        self.db_mock.refresh.side_effect = set_id

        saved_message = self.chat_repository.save_message(message)

        # Verificar que se llamó a `add`
        self.db_mock.add.assert_called_once()

        # El mensaje guardado debe tener id
        self.assertIsNotNone(saved_message.id)

    def test_get_session_history(self):
        """Prueba para obtener el historial de una sesión"""
        self.db_mock.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
            self._make_model()
        ]

        history = self.chat_repository.get_session_history("session1", limit=6)

        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].message, "Hola")

    def test_clear_session_history(self):
        """Prueba para limpiar el historial de una sesión"""
        self.db_mock.query.return_value.filter.return_value.delete.return_value = 2

        deleted_count = self.chat_repository.delete_session_history("session1")

        self.assertEqual(deleted_count, 2)

    def test_get_recent_messages(self):
        """Prueba para obtener los últimos N mensajes de una sesión"""
        self.db_mock.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
            self._make_model()
        ]

        recent_messages = self.chat_repository.get_recent_messages("session1", 2)

        self.assertEqual(len(recent_messages), 1)
        self.assertEqual(recent_messages[0].message, "Hola")


if __name__ == "__main__":
    unittest.main()