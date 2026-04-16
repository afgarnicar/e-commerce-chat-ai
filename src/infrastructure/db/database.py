from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

# URL para la base de datos SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/ecommerce_chat.db"

# Crear motor de conexión a SQLite
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Crear la base para los modelos ORM
Base = declarative_base()

# Crear la fábrica de sesiones para interactuar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db() -> Session:
    """
    Dependency de FastAPI para manejar sesiones de base de datos.
    Usamos yield para que se cierre automáticamente después de la operación.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Inicializa la base de datos y crea las tablas si no existen.
    Se usa Base.metadata.create_all() para crear todas las tablas definidas.
    """
    Base.metadata.create_all(bind=engine)