# Usar la imagen oficial de Python como base
FROM python:3.9-slim

# Establecer el directorio de trabajo
WORKDIR /app2

# Copiar los archivos requeridos
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copiar el resto de la aplicación
COPY . .

# Exponer el puerto en el que Flask se ejecuta
EXPOSE 5001

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]
