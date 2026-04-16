import unittest
from unittest.mock import MagicMock
from src.application.product_service import ProductService
from src.domain.entities import Product
from src.domain.exceptions import ProductNotFoundError
from src.application.dtos import ProductDTO

class TestProductService(unittest.TestCase):
    """
    Pruebas para verificar el comportamiento de ProductService
    """

    def setUp(self):
        """Se ejecuta antes de cada prueba"""
        self.product_repository_mock = MagicMock()
        self.product_service = ProductService(self.product_repository_mock)

    def test_get_all_products(self):
        """Prueba para obtener todos los productos"""
        self.product_repository_mock.get_all.return_value = [
            Product(id=1, name="Zapato", brand="Nike", category="Running",
                    size="42", color="Negro", price=100, stock=10, description="Zapato de correr"),
            Product(id=2, name="Camisa", brand="Adidas", category="Casual",
                    size="M", color="Rojo", price=50, stock=20, description="Camisa casual")
        ]

        products = self.product_service.get_all_products()

        self.product_repository_mock.get_all.assert_called_once()
        self.assertEqual(len(products), 2)

    def test_get_product_by_id(self):
        """Prueba para obtener un producto por ID"""
        self.product_repository_mock.get_by_id.return_value = Product(
            id=1, name="Zapato", brand="Nike", category="Running",
            size="42", color="Negro", price=100, stock=10, description="Zapato de correr"
        )

        product = self.product_service.get_product_by_id(1)

        self.assertEqual(product.id, 1)
        self.product_repository_mock.get_by_id.assert_called_once_with(1)

    def test_get_product_by_id_not_found(self):
        """Prueba que lanza ProductNotFoundError si el producto no se encuentra"""
        self.product_repository_mock.get_by_id.return_value = None

        with self.assertRaises(ProductNotFoundError):
            self.product_service.get_product_by_id(999)

    def test_create_product(self):
        """Prueba para crear un producto"""
        product_dto = ProductDTO(
            name="Zapato", brand="Nike", category="Running", size="42",
            color="Negro", price=100, stock=10, description="Zapato deportivo"
        )

        # Pydantic V2: usar model_dump en lugar de dict
        product_data = product_dto.model_dump(exclude={'id'})

        # El servicio construye Product sin id, así que el mock devuelve uno con id asignado
        self.product_repository_mock.save.return_value = Product(id=1, **product_data)

        created_product = self.product_service.create_product(product_dto)

        self.product_repository_mock.save.assert_called_once()
        self.assertEqual(created_product.id, 1)

    def test_update_product(self):
        """Prueba para actualizar un producto"""
        product_dto = ProductDTO(
            name="Zapato", brand="Nike", category="Running", size="42",
            color="Negro", price=120, stock=5, description="Zapato actualizado"
        )

        self.product_repository_mock.get_by_id.return_value = Product(
            id=1, name="Zapato", brand="Nike", category="Running",
            size="42", color="Negro", price=100, stock=10, description="Zapato de correr"
        )

        # Pydantic V2: usar model_dump en lugar de dict
        product_data = product_dto.model_dump(exclude={'id'})

        self.product_repository_mock.save.return_value = Product(id=1, **product_data)

        updated_product = self.product_service.update_product(1, product_dto)

        self.product_repository_mock.save.assert_called_once()
        self.assertEqual(updated_product.price, 120)

    def test_delete_product(self):
        """Prueba para eliminar un producto"""
        self.product_repository_mock.get_by_id.return_value = Product(
            id=1, name="Zapato", brand="Nike", category="Running",
            size="42", color="Negro", price=100, stock=10, description="Zapato de correr"
        )
        self.product_repository_mock.delete.return_value = True

        result = self.product_service.delete_product(1)

        self.product_repository_mock.delete.assert_called_once_with(1)
        self.assertTrue(result)

    def test_get_available_products(self):
        """Prueba para obtener solo productos con stock disponible"""
        self.product_repository_mock.get_all.return_value = [
            Product(id=1, name="Zapato", brand="Nike", category="Running",
                    size="42", color="Negro", price=100, stock=10, description="Zapato de correr"),
            Product(id=2, name="Camisa", brand="Adidas", category="Casual",
                    size="M", color="Rojo", price=50, stock=0, description="Camisa casual")
        ]

        available_products = self.product_service.get_available_products()

        self.assertEqual(len(available_products), 1)
        self.assertEqual(available_products[0].id, 1)


if __name__ == "__main__":
    unittest.main()