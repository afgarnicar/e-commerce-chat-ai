from src.infrastructure.db.database import SessionLocal
from src.infrastructure.db.models import ProductModel
from random import randint, choice

def load_initial_data():
    """
    Carga datos iniciales en la base de datos si no existen productos.
    Crea 10 productos de ejemplo con datos variados.
    """
    with SessionLocal() as db:
        # Verificar si ya existen productos en la base de datos
        if db.query(ProductModel).count() == 0:
            products = []
            brands = ["Nike", "Adidas", "Puma", "Reebok", "Under Armour"]
            categories = ["Running", "Casual", "Formal", "Sportswear"]
            
            for _ in range(10):
                product = ProductModel(
                    name=f"Producto {randint(1, 100)}",
                    brand=choice(brands),
                    category=choice(categories),
                    size=f"{randint(36, 46)}",
                    color=choice(["Rojo", "Negro", "Azul", "Verde", "Blanco"]),
                    price=randint(50, 200),
                    stock=randint(0, 50),
                    description="Producto de ejemplo"
                )
                products.append(product)
            
            # Insertar los productos en la base de datos
            db.add_all(products)
            db.commit()
            print("Datos iniciales cargados.")
        else:
            print("La base de datos ya tiene productos.")