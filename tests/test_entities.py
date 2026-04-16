import unittest
from datetime import datetime
from src.domain.entities import Product, ChatMessage, ChatContext

class TestEntities(unittest.TestCase):

    def test_product_validations(self):
        # Prueba para validar precio <= 0
        with self.assertRaises(ValueError):
            Product(id=1, name="Zapato", brand="Nike", category="Running", 
                    size="42", color="Negro", price=-50, stock=10, description="Zapato de correr")
        
        # Prueba para validar stock < 0
        with self.assertRaises(ValueError):
            Product(id=2, name="Zapato", brand="Adidas", category="Casual", 
                    size="40", color="Rojo", price=80, stock=-5, description="Zapato casual")
        
        # Prueba para validar nombre vacío
        with self.assertRaises(ValueError):
            Product(id=3, name=" ", brand="Puma", category="Running", 
                    size="43", color="Azul", price=100, stock=15, description="Zapato deportivo")

    def test_chat_message_validations(self):
        # Prueba para rol no válido
        with self.assertRaises(ValueError):
            ChatMessage(id=1, session_id="user123", role="admin", 
                        message="Hola, busco zapatos", timestamp=datetime.now())
        
        # Prueba para mensaje vacío
        with self.assertRaises(ValueError):
            ChatMessage(id=2, session_id="user123", role="user", 
                        message="   ", timestamp=datetime.now())
        
        # Prueba para session_id vacío
        with self.assertRaises(ValueError):
            ChatMessage(id=3, session_id="   ", role="assistant", 
                        message="Tengo varios zapatos para correr", timestamp=datetime.now())

    def test_chat_context_methods(self):
        # Crear varios mensajes de chat
        messages = [
            ChatMessage(id=i, session_id="user123", role="user", message=f"Mensaje {i}", timestamp=datetime.now())
            for i in range(10)
        ]
        chat_context = ChatContext(messages=messages, max_messages=6)

        # Verificar que solo los últimos 6 mensajes sean devueltos
        recent_messages = chat_context.get_recent_messages()
        self.assertEqual(len(recent_messages), 6, "Debe devolver los últimos 6 mensajes.")
        
        # Formatear los mensajes para el prompt de la IA
        formatted_prompt = chat_context.format_for_prompt()
        self.assertTrue(formatted_prompt.startswith("Usuario:"), "El formato debe ser correcto para IA.")

if __name__ == "__main__":
    unittest.main()