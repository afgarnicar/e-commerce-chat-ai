import unittest
from src.domain.exceptions import ProductNotFoundError, InvalidProductDataError, ChatServiceError

class TestExceptions(unittest.TestCase):
    """
    Clase para probar las excepciones definidas en el dominio.
    Se lanzan y capturan las excepciones para verificar que funcionan correctamente.
    """

    def test_product_not_found_error(self):
        """Prueba para la excepción ProductNotFoundError"""
        try:
            raise ProductNotFoundError(123)
        except ProductNotFoundError as e:
            print(f"Producto no encontrado: {e}")
            self.assertEqual(str(e), "Producto con ID 123 no encontrado")

    def test_invalid_product_data_error(self):
        """Prueba para la excepción InvalidProductDataError"""
        try:
            raise InvalidProductDataError("El stock no puede ser negativo")
        except InvalidProductDataError as e:
            print(f"Datos inválidos del producto: {e}")
            self.assertEqual(str(e), "El stock no puede ser negativo")

    def test_chat_service_error(self):
        """Prueba para la excepción ChatServiceError"""
        try:
            raise ChatServiceError("No se pudo conectar con la IA")
        except ChatServiceError as e:
            print(f"Error en el servicio de chat: {e}")
            self.assertEqual(str(e), "No se pudo conectar con la IA")


# Ejecutar las pruebas
if __name__ == "__main__":
    unittest.main()