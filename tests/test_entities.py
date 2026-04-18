"""
Tests unitarios para las entidades del dominio.
Cubre: Product, ChatMessage, ChatContext
"""
import pytest
from datetime import datetime, timezone
from src.domain.entities import Product, ChatMessage, ChatContext


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def valid_product() -> Product:
    """Producto válido reutilizable en múltiples tests."""
    return Product(
        id=1,
        name="Nike Air Zoom",
        brand="Nike",
        category="Running",
        size="42",
        color="Negro",
        price=120.0,
        stock=10,
        description="Zapato de correr con buena amortiguación.",
    )


@pytest.fixture
def out_of_stock_product() -> Product:
    """Producto sin stock."""
    return Product(
        id=2,
        name="Adidas Ultraboost",
        brand="Adidas",
        category="Running",
        size="41",
        color="Blanco",
        price=150.0,
        stock=0,
        description="Zapato premium para running.",
    )


@pytest.fixture
def user_message() -> ChatMessage:
    """Mensaje de usuario válido."""
    return ChatMessage(
        id=1,
        session_id="sesion-abc",
        role="user",
        message="¿Qué zapatos tienen disponibles?",
        timestamp=datetime.now(timezone.utc),
    )


@pytest.fixture
def assistant_message() -> ChatMessage:
    """Mensaje de asistente válido."""
    return ChatMessage(
        id=2,
        session_id="sesion-abc",
        role="assistant",
        message="Tenemos varios modelos disponibles.",
        timestamp=datetime.now(timezone.utc),
    )


# ---------------------------------------------------------------------------
# Tests: Product — validaciones en __post_init__
# ---------------------------------------------------------------------------

class TestProductValidations:
    """Tests para las validaciones de la entidad Product."""

    def test_create_valid_product(self, valid_product):
        """Un producto con datos correctos debe crearse sin errores."""
        assert valid_product.name == "Nike Air Zoom"
        assert valid_product.price == 120.0
        assert valid_product.stock == 10

    def test_product_price_zero_raises(self):
        """Precio igual a 0 debe lanzar ValueError."""
        with pytest.raises(ValueError, match="mayor a 0"):
            Product(id=None, name="Test", brand="X", category="Y",
                    size="40", color="Rojo", price=0, stock=5,
                    description="desc")

    def test_product_negative_price_raises(self):
        """Precio negativo debe lanzar ValueError."""
        with pytest.raises(ValueError, match="mayor a 0"):
            Product(id=None, name="Test", brand="X", category="Y",
                    size="40", color="Rojo", price=-10.0, stock=5,
                    description="desc")

    def test_product_negative_stock_raises(self):
        """Stock negativo debe lanzar ValueError."""
        with pytest.raises(ValueError, match="negativo"):
            Product(id=None, name="Test", brand="X", category="Y",
                    size="40", color="Rojo", price=50.0, stock=-1,
                    description="desc")

    def test_product_empty_name_raises(self):
        """Nombre vacío debe lanzar ValueError."""
        with pytest.raises(ValueError, match="vacío"):
            Product(id=None, name="   ", brand="X", category="Y",
                    size="40", color="Rojo", price=50.0, stock=5,
                    description="desc")

    def test_product_zero_stock_is_valid(self):
        """Stock igual a 0 es válido (producto agotado pero existente)."""
        product = Product(id=None, name="Test", brand="X", category="Y",
                          size="40", color="Rojo", price=50.0, stock=0,
                          description="desc")
        assert product.stock == 0

    def test_product_none_id_is_valid(self):
        """ID None es válido para productos aún no persistidos."""
        product = Product(id=None, name="Test", brand="X", category="Y",
                          size="40", color="Rojo", price=50.0, stock=5,
                          description="desc")
        assert product.id is None


# ---------------------------------------------------------------------------
# Tests: Product — métodos de negocio
# ---------------------------------------------------------------------------

class TestProductMethods:
    """Tests para los métodos de negocio de Product."""

    def test_is_available_with_stock(self, valid_product):
        """Producto con stock debe estar disponible."""
        assert valid_product.is_available() is True

    def test_is_available_without_stock(self, out_of_stock_product):
        """Producto sin stock no debe estar disponible."""
        assert out_of_stock_product.is_available() is False

    def test_reduce_stock_success(self, valid_product):
        """Reducir stock en cantidad válida debe actualizar correctamente."""
        valid_product.reduce_stock(3)
        assert valid_product.stock == 7

    def test_reduce_stock_exact_amount(self, valid_product):
        """Reducir exactamente el stock disponible debe dejar stock en 0."""
        valid_product.reduce_stock(10)
        assert valid_product.stock == 0

    def test_reduce_stock_exceeds_available_raises(self, valid_product):
        """Reducir más del stock disponible debe lanzar ValueError."""
        with pytest.raises(ValueError, match="suficiente stock"):
            valid_product.reduce_stock(99)

    def test_reduce_stock_zero_raises(self, valid_product):
        """Reducir con cantidad 0 debe lanzar ValueError."""
        with pytest.raises(ValueError, match="positiva"):
            valid_product.reduce_stock(0)

    def test_reduce_stock_negative_raises(self, valid_product):
        """Reducir con cantidad negativa debe lanzar ValueError."""
        with pytest.raises(ValueError, match="positiva"):
            valid_product.reduce_stock(-5)

    def test_increase_stock_success(self, valid_product):
        """Aumentar stock en cantidad válida debe actualizar correctamente."""
        valid_product.increase_stock(5)
        assert valid_product.stock == 15

    def test_increase_stock_zero_raises(self, valid_product):
        """Aumentar con cantidad 0 debe lanzar ValueError."""
        with pytest.raises(ValueError, match="positiva"):
            valid_product.increase_stock(0)

    def test_increase_stock_negative_raises(self, valid_product):
        """Aumentar con cantidad negativa debe lanzar ValueError."""
        with pytest.raises(ValueError, match="positiva"):
            valid_product.increase_stock(-3)


# ---------------------------------------------------------------------------
# Tests: ChatMessage — validaciones
# ---------------------------------------------------------------------------

class TestChatMessageValidations:
    """Tests para las validaciones de la entidad ChatMessage."""

    def test_create_user_message(self, user_message):
        """Mensaje de usuario válido debe crearse correctamente."""
        assert user_message.role == "user"
        assert user_message.session_id == "sesion-abc"

    def test_create_assistant_message(self, assistant_message):
        """Mensaje de asistente válido debe crearse correctamente."""
        assert assistant_message.role == "assistant"

    def test_invalid_role_raises(self):
        """Rol que no sea 'user' ni 'assistant' debe lanzar ValueError."""
        with pytest.raises(ValueError, match="'user' o 'assistant'"):
            ChatMessage(
                id=None, session_id="s1", role="admin",
                message="Hola", timestamp=datetime.now(timezone.utc),
            )

    def test_empty_message_raises(self):
        """Mensaje vacío debe lanzar ValueError."""
        with pytest.raises(ValueError, match="vacío"):
            ChatMessage(
                id=None, session_id="s1", role="user",
                message="   ", timestamp=datetime.now(timezone.utc),
            )

    def test_empty_session_id_raises(self):
        """Session ID vacío debe lanzar ValueError."""
        with pytest.raises(ValueError, match="session_id"):
            ChatMessage(
                id=None, session_id="   ", role="user",
                message="Hola", timestamp=datetime.now(timezone.utc),
            )

    def test_is_from_user(self, user_message):
        """is_from_user debe retornar True para mensajes de usuario."""
        assert user_message.is_from_user() is True
        assert user_message.is_from_assistant() is False

    def test_is_from_assistant(self, assistant_message):
        """is_from_assistant debe retornar True para mensajes de asistente."""
        assert assistant_message.is_from_assistant() is True
        assert assistant_message.is_from_user() is False


# ---------------------------------------------------------------------------
# Tests: ChatContext
# ---------------------------------------------------------------------------

class TestChatContext:
    """Tests para ChatContext y su formateo de prompts."""

    def _make_message(self, role: str, text: str) -> ChatMessage:
        return ChatMessage(
            id=None,
            session_id="s1",
            role=role,
            message=text,
            timestamp=datetime.now(timezone.utc),
        )

    def test_get_recent_messages_returns_last_n(self):
        """get_recent_messages debe retornar solo los últimos max_messages."""
        messages = [
            self._make_message("user", f"mensaje {i}") for i in range(10)
        ]
        context = ChatContext(messages=messages, max_messages=3)
        recent = context.get_recent_messages()
        assert len(recent) == 3
        assert recent[-1].message == "mensaje 9"

    def test_get_recent_messages_less_than_max(self):
        """Si hay menos mensajes que max_messages, retorna todos."""
        messages = [self._make_message("user", "hola")]
        context = ChatContext(messages=messages, max_messages=6)
        assert len(context.get_recent_messages()) == 1

    def test_get_recent_messages_empty(self):
        """Con historial vacío debe retornar lista vacía."""
        context = ChatContext(messages=[], max_messages=6)
        assert context.get_recent_messages() == []

    def test_format_for_prompt_labels(self):
        """format_for_prompt debe usar 'Usuario:' y 'Asistente:' correctamente."""
        messages = [
            self._make_message("user", "Hola"),
            self._make_message("assistant", "¡Hola! ¿En qué te ayudo?"),
        ]
        context = ChatContext(messages=messages, max_messages=6)
        result = context.format_for_prompt()
        assert "Usuario: Hola" in result
        assert "Asistente: ¡Hola! ¿En qué te ayudo?" in result

    def test_format_for_prompt_order(self):
        """El prompt debe mantener el orden cronológico de los mensajes."""
        messages = [
            self._make_message("user", "Primero"),
            self._make_message("assistant", "Segundo"),
        ]
        context = ChatContext(messages=messages, max_messages=6)
        result = context.format_for_prompt()
        assert result.index("Primero") < result.index("Segundo")

    def test_format_for_prompt_empty_history(self):
        """Con historial vacío debe retornar string vacío."""
        context = ChatContext(messages=[], max_messages=6)
        assert context.format_for_prompt() == ""

    def test_format_for_prompt_respects_max_messages(self):
        """format_for_prompt solo debe incluir los últimos max_messages."""
        messages = [
            self._make_message("user", f"msg {i}") for i in range(10)
        ]
        context = ChatContext(messages=messages, max_messages=2)
        result = context.format_for_prompt()
        # Solo los 2 últimos deben aparecer
        assert "msg 8" in result
        assert "msg 9" in result
        assert "msg 0" not in result