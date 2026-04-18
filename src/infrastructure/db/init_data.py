from src.infrastructure.db.database import SessionLocal
from src.infrastructure.db.models import ProductModel


def load_initial_data() -> None:
    db = SessionLocal()
    try:
        existing_products = db.query(ProductModel).count()

        if existing_products == 0:
            products = [
                ProductModel(
                    name="Nike Air Zoom Pegasus",
                    brand="Nike",
                    category="Running",
                    size="42",
                    color="Negro",
                    price=120.0,
                    stock=5,
                    description="Zapato ideal para correr con buena amortiguación.",
                ),
                ProductModel(
                    name="Adidas Ultraboost 21",
                    brand="Adidas",
                    category="Running",
                    size="41",
                    color="Blanco",
                    price=150.0,
                    stock=3,
                    description="Zapato premium para running con gran comodidad.",
                ),
                ProductModel(
                    name="Puma Suede Classic",
                    brand="Puma",
                    category="Casual",
                    size="40",
                    color="Azul",
                    price=80.0,
                    stock=10,
                    description="Zapato casual clásico y cómodo.",
                ),
                ProductModel(
                    name="Nike Revolution 6",
                    brand="Nike",
                    category="Running",
                    size="43",
                    color="Gris",
                    price=95.0,
                    stock=7,
                    description="Opción versátil para correr y entrenar.",
                ),
                ProductModel(
                    name="Adidas Grand Court",
                    brand="Adidas",
                    category="Casual",
                    size="42",
                    color="Blanco",
                    price=85.0,
                    stock=6,
                    description="Estilo urbano y cómodo para uso diario.",
                ),
                ProductModel(
                    name="Puma Smash v2",
                    brand="Puma",
                    category="Casual",
                    size="41",
                    color="Negro",
                    price=75.0,
                    stock=8,
                    description="Zapato casual con diseño limpio.",
                ),
                ProductModel(
                    name="Reebok Nano X3",
                    brand="Reebok",
                    category="Sportswear",
                    size="42",
                    color="Rojo",
                    price=130.0,
                    stock=4,
                    description="Zapato deportivo para entrenamiento funcional.",
                ),
                ProductModel(
                    name="Under Armour Charged Assert",
                    brand="Under Armour",
                    category="Running",
                    size="44",
                    color="Negro",
                    price=110.0,
                    stock=5,
                    description="Buen soporte y comodidad para corredores.",
                ),
                ProductModel(
                    name="Clarks Oxford Leather",
                    brand="Clarks",
                    category="Formal",
                    size="42",
                    color="Café",
                    price=140.0,
                    stock=2,
                    description="Zapato formal de cuero para ocasiones elegantes.",
                ),
                ProductModel(
                    name="Ecco Citytray",
                    brand="Ecco",
                    category="Formal",
                    size="43",
                    color="Negro",
                    price=180.0,
                    stock=3,
                    description="Zapato formal moderno y confortable.",
                ),
            ]

            db.add_all(products)
            db.commit()

    finally:
        db.close()