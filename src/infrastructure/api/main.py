from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from src.application.chat_service import ChatService
from src.application.dtos import (
    ChatHistoryDTO,
    ChatMessageRequestDTO,
    ChatMessageResponseDTO,
    ProductDTO,
)
from src.application.product_service import ProductService
from src.domain.exceptions import ChatServiceError, ProductNotFoundError
from src.infrastructure.db.database import get_db, init_db
from src.infrastructure.db.init_data import load_initial_data
from src.infrastructure.llm_providers.gemini_service import GeminiService
from src.infrastructure.repositories.chat_repository import SQLChatRepository
from src.infrastructure.repositories.product_repository import SQLProductRepository


# ---------------------------------------------------------------------------
# Lifespan: reemplaza el deprecado @app.on_event("startup")
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa la base de datos y carga datos al arrancar la aplicación."""
    init_db()
    load_initial_data()
    yield
    # Aquí se puede añadir lógica de shutdown si hace falta


app = FastAPI(
    title="E-commerce Chat AI API",
    description="API REST de e-commerce de zapatos con chat inteligente usando Clean Architecture.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
def read_root() -> dict:
    """Retorna información básica de la API."""
    return {
        "name": "E-commerce Chat AI API",
        "version": "1.0.0",
        "description": "API REST para e-commerce de zapatos con chat impulsado por Gemini.",
        "endpoints": {
            "products": {
                "list": "GET /products",
                "detail": "GET /products/{product_id}",
            },
            "chat": {
                "send_message": "POST /chat",
                "history": "GET /chat/history/{session_id}",
                "clear_history": "DELETE /chat/history/{session_id}",
            },
            "health": "GET /health",
        },
    }


@app.get("/products", response_model=List[ProductDTO])
def get_products(db: Session = Depends(get_db)) -> List[ProductDTO]:
    """Obtiene la lista completa de productos."""
    product_repository = SQLProductRepository(db)
    product_service = ProductService(product_repository)

    products = product_service.get_all_products()
    # Pydantic V2: model_validate reemplaza from_orm
    return [ProductDTO.model_validate(product) for product in products]


@app.get("/products/{product_id}", response_model=ProductDTO)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)) -> ProductDTO:
    """Obtiene un producto por su ID."""
    product_repository = SQLProductRepository(db)
    product_service = ProductService(product_repository)

    try:
        product = product_service.get_product_by_id(product_id)
        return ProductDTO.model_validate(product)
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/chat", response_model=ChatMessageResponseDTO)
async def send_chat_message(
    request: ChatMessageRequestDTO,
    db: Session = Depends(get_db),
) -> ChatMessageResponseDTO:
    """Procesa un mensaje de chat del usuario y retorna la respuesta de la IA."""
    product_repository = SQLProductRepository(db)
    chat_repository = SQLChatRepository(db)
    ai_service = GeminiService()

    chat_service = ChatService(
        product_repository=product_repository,
        chat_repository=chat_repository,
        ai_service=ai_service,
    )

    try:
        return await chat_service.process_message(request)
    except ChatServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error while processing chat message: {exc}",
        ) from exc


@app.get("/chat/history/{session_id}", response_model=List[ChatHistoryDTO])
def get_chat_history(
    session_id: str,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> List[ChatHistoryDTO]:
    """Obtiene el historial de chat de una sesión."""
    # No se necesita GeminiService para leer el historial
    chat_repository = SQLChatRepository(db)
    product_repository = SQLProductRepository(db)

    chat_service = ChatService(
        product_repository=product_repository,
        chat_repository=chat_repository,
        ai_service=None,  # No se usa en get_session_history
    )

    return chat_service.get_session_history(session_id, limit)


@app.delete("/chat/history/{session_id}")
def clear_chat_history(session_id: str, db: Session = Depends(get_db)) -> dict:
    """Elimina el historial de una sesión de chat."""
    # No se necesita GeminiService para borrar historial
    chat_repository = SQLChatRepository(db)
    product_repository = SQLProductRepository(db)

    chat_service = ChatService(
        product_repository=product_repository,
        chat_repository=chat_repository,
        ai_service=None,  # No se usa en clear_session_history
    )

    deleted_count = chat_service.clear_session_history(session_id)

    return {
        "session_id": session_id,
        "deleted_messages": deleted_count,
    }


@app.get("/health")
def health_check() -> dict:
    """Endpoint de verificación de salud de la API."""
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }