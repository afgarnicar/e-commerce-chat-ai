from src.domain.repositories import IProductRepository
from src.domain.entities import Product
from src.domain.exceptions import ProductNotFoundError
from src.application.dtos import ProductDTO
from typing import List

class ProductService:
    """
    Servicio de aplicación para manejar la lógica de negocio relacionada con productos.
    Recibe IProductRepository por dependency injection.
    """
    
    def __init__(self, product_repository: IProductRepository):
        """
        Constructor para inyectar el repositorio de productos.
        """
        self.product_repository = product_repository

    def get_all_products(self) -> List[Product]:
        """
        Obtiene todos los productos.
        Retorna una lista de todos los productos.
        """
        return self.product_repository.get_all()

    def get_product_by_id(self, product_id: int) -> Product:
        """
        Busca un producto por su ID.
        Lanza una excepción ProductNotFoundError si el producto no existe.
        """
        product = self.product_repository.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(product_id)
        return product

    def search_products(self, filters: dict) -> List[Product]:
        """
        Busca productos según los filtros proporcionados.
        Los filtros son un diccionario con criterios como marca, categoría, etc.
        """
        # Lógica para filtrar según los criterios pasados
        if 'brand' in filters:
            return self.product_repository.get_by_brand(filters['brand'])
        if 'category' in filters:
            return self.product_repository.get_by_category(filters['category'])
        return self.product_repository.get_all()

    def create_product(self, product_dto: ProductDTO) -> Product:
        """
        Crea un nuevo producto.
        Convierte el DTO en una entidad Product y lo guarda en el repositorio.
        """
        product = Product(
            id=None,
            name=product_dto.name,
            brand=product_dto.brand,
            category=product_dto.category,
            size=product_dto.size,
            color=product_dto.color,
            price=product_dto.price,
            stock=product_dto.stock,
            description=product_dto.description
        )
        return self.product_repository.save(product)

    def update_product(self, product_id: int, product_dto: ProductDTO) -> Product:
        """
        Actualiza un producto existente.
        Verifica si el producto existe antes de actualizarlo.
        Lanza ProductNotFoundError si el producto no existe.
        """
        product = self.get_product_by_id(product_id)  # Verifica si el producto existe
        # Actualiza los atributos del producto
        product.name = product_dto.name
        product.brand = product_dto.brand
        product.category = product_dto.category
        product.size = product_dto.size
        product.color = product_dto.color
        product.price = product_dto.price
        product.stock = product_dto.stock
        product.description = product_dto.description
        return self.product_repository.save(product)

    def delete_product(self, product_id: int) -> bool:
        """
        Elimina un producto por ID.
        Lanza una excepción ProductNotFoundError si el producto no existe.
        """
        product = self.get_product_by_id(product_id)  # Verifica si el producto existe
        return self.product_repository.delete(product_id)

    def get_available_products(self) -> List[Product]:
        """
        Obtiene los productos con stock disponible.
        Retorna solo los productos cuyo stock sea mayor que 0.
        """
        all_products = self.product_repository.get_all()
        return [product for product in all_products if product.is_available()]