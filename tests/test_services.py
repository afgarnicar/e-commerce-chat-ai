"""
Tests unitarios para los servicios de aplicación.
Cubre: ProductService, ChatService
Usa pytest.fixture y unittest.mock para aislar dependencias.
"""
import pytest
import pytest_asyncio
from datetime import datetime, timezone
from unittest.mock import MagicMock, AsyncMock, patch

from src.application.product_service import ProductService
from src.application.chat_service import ChatService
from src.application.dtos import ProductDTO, ChatMessageRequestDTO
from src.domain.entities import Product, ChatMessage
from src.domain.exceptions import ProductNotFoundError, ChatServiceError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_product(
    product_id: int = 1,
    name: str = "Nike Air Zoom",
    stock: int = 10,
    price: float = 120.0,
) -> Product:
    return Product(
        id=product_id,
        name=name,
        brand="Nike",
        category="Running",
        size="42",
        color="Negro",
        price=price,
        stock=stock,
        description="Zapato de correr.",
    )


def make_chat_message(role: str = "user", text: str = "Hola") -> ChatMessage:
    return ChatMessage(
        id=1,
        session_id="sesion-1",
        role=role,
        message=text,
        timestamp=datetime.now(timezone.utc),
    )


def make_product_dto(**overrides) -> ProductDTO:
    defaults = dict(
        name="Nike Air Zoom",
        brand="Nike",
        category="Running",
        size="42",
        color="Negro",
        price=120.0,
        stock=10,
        description="Zapato de correr.",
    )
    defaults.update(overrides)
    return ProductDTO(**defaults)


# ---------------------------------------------------------------------------
# Fixtures: ProductService
# ---------------------------------------------------------------------------

@pytest.fixture
def product_repo_mock():
    """Mock del repositorio de productos."""
    return MagicMock()


@pytest.fixture
def product_service(product_repo_mock) -> ProductService:
    """ProductService con repositorio mockeado."""
    return ProductService(product_repository=product_repo_mock)


# ---------------------------------------------------------------------------
# Tests: ProductService
# ---------------------------------------------------------------------------

class TestProductServiceGetAll:

    def test_get_all_returns_list(self, product_service, product_repo_mock):
        """get_all_products debe retornar la lista completa del repositorio."""
        product_repo_mock.get_all.return_value = [make_product(1), make_product(2)]
        result = product_service.get_all_products()
        assert len(result) == 2
        product_repo_mock.get_all.assert_called_once()

    def test_get_all_empty_list(self, product_service, product_repo_mock):
        """get_all_products con repositorio vacío debe retornar lista vacía."""
        product_repo_mock.get_all.return_value = []
        result = product_service.get_all_products()
        assert result == []


class TestProductServiceGetById:

    def test_get_by_id_found(self, product_service, product_repo_mock):
        """get_product_by_id debe retornar el producto cuando existe."""
        product_repo_mock.get_by_id.return_value = make_product(1)
        result = product_service.get_product_by_id(1)
        assert result.id == 1
        product_repo_mock.get_by_id.assert_called_once_with(1)

    def test_get_by_id_not_found_raises(self, product_service, product_repo_mock):
        """get_product_by_id debe lanzar ProductNotFoundError si no existe."""
        product_repo_mock.get_by_id.return_value = None
        with pytest.raises(ProductNotFoundError):
            product_service.get_product_by_id(999)

    def test_not_found_error_contains_id(self, product_service, product_repo_mock):
        """El mensaje del error debe incluir el ID buscado."""
        product_repo_mock.get_by_id.return_value = None
        with pytest.raises(ProductNotFoundError, match="999"):
            product_service.get_product_by_id(999)


class TestProductServiceSearch:

    def test_search_by_brand(self, product_service, product_repo_mock):
        """search_products con filtro brand debe llamar get_by_brand."""
        product_repo_mock.get_by_brand.return_value = [make_product()]
        result = product_service.search_products({"brand": "Nike"})
        product_repo_mock.get_by_brand.assert_called_once_with("Nike")
        assert len(result) == 1

    def test_search_by_category(self, product_service, product_repo_mock):
        """search_products con filtro category debe llamar get_by_category."""
        product_repo_mock.get_by_category.return_value = [make_product()]
        result = product_service.search_products({"category": "Running"})
        product_repo_mock.get_by_category.assert_called_once_with("Running")

    def test_search_no_filters_returns_all(self, product_service, product_repo_mock):
        """search_products sin filtros debe retornar todos los productos."""
        product_repo_mock.get_all.return_value = [make_product()]
        result = product_service.search_products({})
        product_repo_mock.get_all.assert_called_once()


class TestProductServiceCreate:

    def test_create_product_calls_save(self, product_service, product_repo_mock):
        """create_product debe guardar el producto en el repositorio."""
        dto = make_product_dto()
        product_repo_mock.save.return_value = make_product(1)
        result = product_service.create_product(dto)
        product_repo_mock.save.assert_called_once()
        assert result.id == 1

    def test_create_product_id_is_none(self, product_service, product_repo_mock):
        """create_product debe pasar id=None al repositorio (nuevo registro)."""
        dto = make_product_dto()
        product_repo_mock.save.return_value = make_product(1)
        product_service.create_product(dto)
        saved_entity = product_repo_mock.save.call_args[0][0]
        assert saved_entity.id is None


class TestProductServiceUpdate:

    def test_update_existing_product(self, product_service, product_repo_mock):
        """update_product debe actualizar los campos y guardar."""
        original = make_product(1, price=100.0)
        product_repo_mock.get_by_id.return_value = original
        updated = make_product(1, price=200.0)
        product_repo_mock.save.return_value = updated

        dto = make_product_dto(price=200.0)
        result = product_service.update_product(1, dto)
        assert result.price == 200.0
        product_repo_mock.save.assert_called_once()

    def test_update_nonexistent_product_raises(self, product_service, product_repo_mock):
        """update_product debe lanzar ProductNotFoundError si no existe."""
        product_repo_mock.get_by_id.return_value = None
        with pytest.raises(ProductNotFoundError):
            product_service.update_product(999, make_product_dto())


class TestProductServiceDelete:

    def test_delete_existing_product(self, product_service, product_repo_mock):
        """delete_product debe eliminar y retornar True."""
        product_repo_mock.get_by_id.return_value = make_product(1)
        product_repo_mock.delete.return_value = True
        result = product_service.delete_product(1)
        assert result is True
        product_repo_mock.delete.assert_called_once_with(1)

    def test_delete_nonexistent_product_raises(self, product_service, product_repo_mock):
        """delete_product debe lanzar ProductNotFoundError si no existe."""
        product_repo_mock.get_by_id.return_value = None
        with pytest.raises(ProductNotFoundError):
            product_service.delete_product(999)


class TestProductServiceAvailable:

    def test_get_available_filters_out_of_stock(self, product_service, product_repo_mock):
        """get_available_products debe excluir productos sin stock."""
        product_repo_mock.get_all.return_value = [
            make_product(1, stock=5),
            make_product(2, stock=0),
            make_product(3, stock=3),
        ]
        result = product_service.get_available_products()
        assert len(result) == 2
        assert all(p.stock > 0 for p in result)

    def test_get_available_all_out_of_stock(self, product_service, product_repo_mock):
        """Si todos están agotados debe retornar lista vacía."""
        product_repo_mock.get_all.return_value = [
            make_product(1, stock=0),
            make_product(2, stock=0),
        ]
        result = product_service.get_available_products()
        assert result == []


# ---------------------------------------------------------------------------
# Fixtures: ChatService
# ---------------------------------------------------------------------------

@pytest.fixture
def chat_repo_mock():
    return MagicMock()


@pytest.fixture
def ai_service_mock():
    mock = MagicMock()
    mock.generate_response = AsyncMock(return_value="¡Hola! Tenemos varios modelos.")
    return mock


@pytest.fixture
def chat_service(product_repo_mock, chat_repo_mock, ai_service_mock) -> ChatService:
    """ChatService con todas las dependencias mockeadas."""
    return ChatService(
        product_repository=product_repo_mock,
        chat_repository=chat_repo_mock,
        ai_service=ai_service_mock,
    )


# ---------------------------------------------------------------------------
# Tests: ChatService
# ---------------------------------------------------------------------------

class TestChatServiceProcessMessage:

    @pytest.mark.asyncio
    async def test_process_message_returns_response(
        self, chat_service, product_repo_mock, chat_repo_mock, ai_service_mock
    ):
        """process_message debe retornar un ChatMessageResponseDTO con la respuesta."""
        product_repo_mock.get_all.return_value = [make_product()]
        chat_repo_mock.get_recent_messages.return_value = []
        saved = make_chat_message()
        chat_repo_mock.save_message.return_value = saved

        request = ChatMessageRequestDTO(
            session_id="sesion-1",
            message="¿Qué zapatos tienen?",
        )
        result = await chat_service.process_message(request)

        assert result.session_id == "sesion-1"
        assert result.user_message == "¿Qué zapatos tienen?"
        assert result.assistant_message == "¡Hola! Tenemos varios modelos."

    @pytest.mark.asyncio
    async def test_process_message_saves_both_messages(
        self, chat_service, product_repo_mock, chat_repo_mock, ai_service_mock
    ):
        """process_message debe guardar el mensaje del usuario y el del asistente."""
        product_repo_mock.get_all.return_value = []
        chat_repo_mock.get_recent_messages.return_value = []
        chat_repo_mock.save_message.return_value = make_chat_message()

        request = ChatMessageRequestDTO(session_id="s1", message="Hola")
        await chat_service.process_message(request)

        assert chat_repo_mock.save_message.call_count == 2

    @pytest.mark.asyncio
    async def test_process_message_calls_ai_with_products(
        self, chat_service, product_repo_mock, chat_repo_mock, ai_service_mock
    ):
        """process_message debe pasar los productos al servicio de IA."""
        products = [make_product(1), make_product(2)]
        product_repo_mock.get_all.return_value = products
        chat_repo_mock.get_recent_messages.return_value = []
        chat_repo_mock.save_message.return_value = make_chat_message()

        request = ChatMessageRequestDTO(session_id="s1", message="Hola")
        await chat_service.process_message(request)

        call_kwargs = ai_service_mock.generate_response.call_args.kwargs
        assert call_kwargs["products"] == products

    @pytest.mark.asyncio
    async def test_process_message_ai_error_raises_chat_service_error(
        self, chat_service, product_repo_mock, chat_repo_mock, ai_service_mock
    ):
        """Si la IA falla, debe lanzar ChatServiceError."""
        product_repo_mock.get_all.return_value = []
        chat_repo_mock.get_recent_messages.return_value = []
        ai_service_mock.generate_response.side_effect = RuntimeError("Gemini down")

        request = ChatMessageRequestDTO(session_id="s1", message="Hola")
        with pytest.raises(ChatServiceError):
            await chat_service.process_message(request)


class TestChatServiceHistory:

    def test_get_session_history_returns_dtos(
        self, chat_service, chat_repo_mock
    ):
        """get_session_history debe convertir mensajes a ChatHistoryDTO."""
        chat_repo_mock.get_session_history.return_value = [
            make_chat_message("user", "Hola"),
            make_chat_message("assistant", "¿En qué te ayudo?"),
        ]
        result = chat_service.get_session_history("sesion-1", limit=10)
        assert len(result) == 2
        assert result[0].role == "user"
        assert result[1].role == "assistant"

    def test_get_session_history_empty(self, chat_service, chat_repo_mock):
        """get_session_history con sesión sin mensajes debe retornar lista vacía."""
        chat_repo_mock.get_session_history.return_value = []
        result = chat_service.get_session_history("sesion-vacia")
        assert result == []

    def test_clear_session_history_returns_count(
        self, chat_service, chat_repo_mock
    ):
        """clear_session_history debe retornar el número de mensajes eliminados."""
        chat_repo_mock.delete_session_history.return_value = 5
        result = chat_service.clear_session_history("sesion-1")
        assert result == 5
        chat_repo_mock.delete_session_history.assert_called_once_with("sesion-1")

    def test_clear_session_history_zero(self, chat_service, chat_repo_mock):
        """clear_session_history con sesión vacía debe retornar 0."""
        chat_repo_mock.delete_session_history.return_value = 0
        result = chat_service.clear_session_history("sesion-nueva")
        assert result == 0