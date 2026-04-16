import unittest
from src.domain.repositories import IProductRepository, IChatRepository
from abc import ABC

class TestRepositories(unittest.TestCase):
    """
    Clase para probar que las interfaces no se pueden instanciar directamente.
    """
    
    def test_product_repository_cannot_be_instantiated(self):
        """Verifica que no se pueda instanciar IProductRepository directamente"""
        with self.assertRaises(TypeError):
            repo = IProductRepository()

    def test_chat_repository_cannot_be_instantiated(self):
        """Verifica que no se pueda instanciar IChatRepository directamente"""
        with self.assertRaises(TypeError):
            repo = IChatRepository()

# Ejecutar las pruebas
if __name__ == "__main__":
    unittest.main()