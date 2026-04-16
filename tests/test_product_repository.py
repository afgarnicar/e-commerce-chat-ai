import unittest
from unittest.mock import MagicMock, call
from src.infrastructure.repositories.product_repository import SQLProductRepository
from src.domain.entities import Product
from src.infrastructure.db.models import ProductModel
from sqlalchemy.orm import Session


class TestSQLProductRepository(unittest.TestCase):
    """Pruebas para el repositorio de productos SQL"""

    def setUp(self):
        """Configura el entorno antes de cada prueba"""
        self.db_mock = MagicMock(spec=Session)
        self.product_repository = SQLProductRepository(self.db_mock)

    def test_get_all(self):
        """Prueba para obtener todos los productos"""
        # El repositorio hace: self.db.query(ProductModel).all()
        # Hay que configurar la cadena completa del mock
        self.db_mock.query.return_value.all.return_value = [
            ProductModel(id=1, name="Zapato", brand="Nike", category="Running",
                         size="42", color="Negro", price=100, stock=10, description="Zapato de correr"),
            ProductModel(id=2, name="Camisa", brand="Adidas", category="Casual",
                         size="M", color="Rojo", price=50, stock=20, description="Camisa casual")
        ]

        products = self.product_repository.get_all()

        # Verificar que se llamó query con ProductModel
        self.db_mock.query.assert_called_once_with(ProductModel)

        # Verificar que la lista tiene 2 productos
        self.assertEqual(len(products), 2)

    def test_get_by_id(self):
        """Prueba para obtener un producto por ID"""
        self.db_mock.query.return_value.filter.return_value.first.return_value = ProductModel(
            id=1, name="Zapato", brand="Nike", category="Running",
            size="42", color="Negro", price=100, stock=10, description="Zapato de correr"
        )

        product = self.product_repository.get_by_id(1)

        self.assertEqual(product.id, 1)

    def test_get_by_id_not_found(self):
        """Prueba que retorna None si no encuentra un producto"""
        self.db_mock.query.return_value.filter.return_value.first.return_value = None

        product = self.product_repository.get_by_id(999)
        self.assertIsNone(product)

    def test_save_create_product(self):
        """Prueba para crear un nuevo producto (sin ID)"""
        product = Product(id=None, name="Zapato", brand="Nike", category="Running",
                          size="42", color="Negro", price=100, stock=10, description="Zapato deportivo")

        self.db_mock.commit.return_value = None
        self.db_mock.refresh.return_value = None

        saved_product = self.product_repository.save(product)

        # Verificar que se llamó a `add` (con cualquier ProductModel)
        self.db_mock.add.assert_called_once()
        # El argumento debe ser un ProductModel
        add_arg = self.db_mock.add.call_args[0][0]
        self.assertIsInstance(add_arg, ProductModel)

    def test_save_update_product(self):
        """Prueba para actualizar un producto (con ID)"""
        product = Product(id=1, name="Zapato", brand="Nike", category="Running",
                          size="42", color="Negro", price=120, stock=5, description="Zapato actualizado")

        # merge devuelve un ProductModel actualizado
        merged_model = ProductModel(id=1, name="Zapato", brand="Nike", category="Running",
                                    size="42", color="Negro", price=120, stock=5,
                                    description="Zapato actualizado")
        self.db_mock.merge.return_value = merged_model
        self.db_mock.commit.return_value = None

        saved_product = self.product_repository.save(product)

        # Verificar que se llamó a `merge` con un ProductModel
        self.db_mock.merge.assert_called_once()
        merge_arg = self.db_mock.merge.call_args[0][0]
        self.assertIsInstance(merge_arg, ProductModel)

        # Verificar que el producto devuelto tiene el ID correcto
        self.assertEqual(saved_product.id, 1)

    def test_delete(self):
        """Prueba para eliminar un producto"""
        self.db_mock.query.return_value.filter.return_value.first.return_value = ProductModel(
            id=1, name="Zapato", brand="Nike", category="Running",
            size="42", color="Negro", price=100, stock=10, description="Zapato de correr"
        )
        self.db_mock.delete.return_value = None
        self.db_mock.commit.return_value = None

        result = self.product_repository.delete(1)

        self.assertTrue(result)
        self.db_mock.delete.assert_called_once()


if __name__ == "__main__":
    unittest.main()