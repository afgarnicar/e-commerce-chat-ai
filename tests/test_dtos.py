import unittest
from pydantic import ValidationError
from src.application.dtos import ProductDTO, ChatMessageRequestDTO
from datetime import datetime

class TestDTOs(unittest.TestCase):
    
    def test_product_dto_invalid_price(self):
        """Prueba para validar que el precio sea mayor a 0"""
        with self.assertRaises(ValidationError):
            ProductDTO(name="Zapato", brand="Nike", category="Running", size="42", color="Negro", price=-10, stock=5, description="Zapato deportivo")

    def test_product_dto_invalid_stock(self):
        """Prueba para validar que el stock no sea negativo"""
        with self.assertRaises(ValidationError):
            ProductDTO(name="Zapato", brand="Nike", category="Running", size="42", color="Negro", price=50, stock=-1, description="Zapato deportivo")

    def test_chat_message_request_dto_empty_message(self):
        """Prueba para validar que el mensaje no esté vacío"""
        with self.assertRaises(ValidationError):
            ChatMessageRequestDTO(session_id="session123", message="   ")

    def test_chat_message_request_dto_empty_session_id(self):
        """Prueba para validar que el session_id no esté vacío"""
        with self.assertRaises(ValidationError):
            ChatMessageRequestDTO(session_id="", message="Hola, ¿cómo estás?")

if __name__ == "__main__":
    unittest.main()