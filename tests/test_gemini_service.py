import os
import unittest
from unittest.mock import MagicMock, patch

from src.domain.entities import Product, ChatContext, ChatMessage
from src.infrastructure.llm_providers.gemini_service import GeminiService


class TestGeminiService(unittest.TestCase):
    def setUp(self):
        os.environ["GEMINI_API_KEY"] = "fake-api-key"

        self.products = [
            Product(
                id=1,
                name="Nike Air Zoom",
                brand="Nike",
                category="Running",
                size="42",
                color="Negro",
                price=120.0,
                stock=5,
                description="Zapato para correr"
            ),
            Product(
                id=2,
                name="Adidas Ultraboost",
                brand="Adidas",
                category="Running",
                size="41",
                color="Blanco",
                price=150.0,
                stock=3,
                description="Zapato premium para running"
            ),
        ]

        self.context = ChatContext(
            messages=[
                ChatMessage(
                    id=1,
                    session_id="session-1",
                    role="user",
                    message="Hola, busco zapatos para correr",
                    timestamp=None,
                ),
                ChatMessage(
                    id=2,
                    session_id="session-1",
                    role="assistant",
                    message="Claro, ¿qué talla necesitas?",
                    timestamp=None,
                ),
            ],
            max_messages=6,
        )

    def test_format_products_info(self):
        service = GeminiService()
        result = service.format_products_info(self.products)

        self.assertIn("Nike Air Zoom", result)
        self.assertIn("Adidas Ultraboost", result)
        self.assertIn("Stock: 5", result)
        self.assertIn("$120.00", result)

    def test_build_prompt_contains_expected_sections(self):
        service = GeminiService()
        prompt = service._build_prompt(
            user_message="Talla 42",
            products=self.products,
            context=self.context,
        )

        self.assertIn("AVAILABLE PRODUCTS", prompt)
        self.assertIn("CONVERSATION HISTORY", prompt)
        self.assertIn("Nike Air Zoom", prompt)
        self.assertIn("Usuario: Hola, busco zapatos para correr", prompt)
        self.assertIn("User: Talla 42", prompt)

    @patch("src.infrastructure.llm_providers.gemini_service.genai.Client")
    def test_generate_response_success(self, mock_client_class):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Te recomiendo Nike Air Zoom en talla 42."
        mock_client.models.generate_content.return_value = mock_response
        mock_client_class.return_value = mock_client

        service = GeminiService()

        import asyncio
        result = asyncio.run(
            service.generate_response(
                user_message="Quiero talla 42",
                products=self.products,
                context=self.context,
            )
        )

        self.assertEqual(result, "Te recomiendo Nike Air Zoom en talla 42.")
        mock_client.models.generate_content.assert_called_once()

    @patch("src.infrastructure.llm_providers.gemini_service.genai.Client")
    def test_generate_response_empty_text_raises_error(self, mock_client_class):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = ""
        mock_client.models.generate_content.return_value = mock_response
        mock_client_class.return_value = mock_client

        service = GeminiService()

        import asyncio
        with self.assertRaises(RuntimeError):
            asyncio.run(
                service.generate_response(
                    user_message="Quiero talla 42",
                    products=self.products,
                    context=self.context,
                )
            )