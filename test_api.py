import requests
import os

# Asegúrate de que existe una imagen de prueba
image_path = "foto3.jpg"

if not os.path.exists(image_path):
    print(f"Error: No se encuentra {image_path}")
    print("Por favor, coloca una imagen .jpg en este directorio para probar.")
    exit(1)

print(f"Enviando {image_path} al servidor...")
files = {"image": open(image_path, "rb")}

try:
    r = requests.post("http://localhost:5000/detect", files=files)
    if r.status_code == 200:
        print("Respuesta del servidor:")
        print(r.json())
    else:
        print(f"Error del servidor: {r.status_code}")
        print(r.text)
except requests.exceptions.ConnectionError:
    print("Error de conexión. ¿Está corriendo el servidor (app.ipynb)?")
