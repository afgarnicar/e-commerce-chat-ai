# Imagen base slim para reducir tamaño
FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar requirements primero para aprovechar cache de layers de Docker
# Si requirements.txt no cambia, Docker reutiliza esta capa en builds futuros
COPY requirements.txt .

# Instalar dependencias sin guardar cache de pip (reduce tamaño de imagen)
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código fuente
COPY . .

# Crear el directorio de datos para la base de datos SQLite
RUN mkdir -p /app/data

# Exponer el puerto de la aplicación
EXPOSE 8000

# Comando por defecto para producción (sin --reload)
CMD ["uvicorn", "src.infrastructure.api.main:app", "--host", "0.0.0.0", "--port", "8000"]