from sqlalchemy.orm import Session
from src.domain.repositories import IProductRepository
from src.infrastructure.db.models import ProductModel
from src.domain.entities import Product
from typing import List, Optional

class SQLProductRepository(IProductRepository):
    def __init__(self, db: Session):
        """
        Constructor para inyectar la sesión de base de datos.
        
        Args:
            db (Session): La sesión de base de datos SQLAlchemy
        """
        self.db = db

    def get_all(self) -> List[Product]:
        """Obtiene todos los productos de la base de datos."""
        product_models = self.db.query(ProductModel).all()
        return [self._model_to_entity(model) for model in product_models]

    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Obtiene un producto por ID."""
        product_model = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if product_model:
            return self._model_to_entity(product_model)
        return None

    def get_by_brand(self, brand: str) -> List[Product]:
        """Obtiene productos por marca."""
        product_models = self.db.query(ProductModel).filter(ProductModel.brand == brand).all()
        return [self._model_to_entity(model) for model in product_models]

    def get_by_category(self, category: str) -> List[Product]:
        """Obtiene productos por categoría."""
        product_models = self.db.query(ProductModel).filter(ProductModel.category == category).all()
        return [self._model_to_entity(model) for model in product_models]

    def save(self, product: Product) -> Product:
        """Guarda o actualiza un producto."""
        product_model = self._entity_to_model(product)
        if product.id:
            # Actualizar el producto si tiene un ID
            self.db.merge(product_model)
        else:
            # Crear un nuevo producto si no tiene ID
            self.db.add(product_model)
            self.db.commit()
            self.db.refresh(product_model)  # Obtener el ID generado
        self.db.commit()  # Confirmar cambios
        return self._model_to_entity(product_model)

    def delete(self, product_id: int) -> bool:
        """Elimina un producto por ID."""
        product_model = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if product_model:
            self.db.delete(product_model)
            self.db.commit()
            return True
        return False

    def _model_to_entity(self, model: ProductModel) -> Product:
        """Convierte un modelo ORM a una entidad del dominio."""
        return Product(
            id=model.id,
            name=model.name,
            brand=model.brand,
            category=model.category,
            size=model.size,
            color=model.color,
            price=model.price,
            stock=model.stock,
            description=model.description
        )

    def _entity_to_model(self, entity: Product) -> ProductModel:
        """Convierte una entidad del dominio a un modelo ORM."""
        return ProductModel(
            id=entity.id,
            name=entity.name,
            brand=entity.brand,
            category=entity.category,
            size=entity.size,
            color=entity.color,
            price=entity.price,
            stock=entity.stock,
            description=entity.description
        )