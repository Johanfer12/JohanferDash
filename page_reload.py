import requests
from time import sleep
import json
import os

# Cambia la ruta del archivo JSON según tu estructura de carpetas
ruta_json = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'apikey.json')

# Estructura del JSON
""" {
    "username": "",
    "api_token": "",
    "domain_name": ""
} """

# Función para cargar datos desde el archivo JSON
def cargar_datos_desde_json(ruta_json):
    with open(ruta_json) as archivo_json:
        return json.load(archivo_json)

# Obtener valores del JSON
datos_json = cargar_datos_desde_json(ruta_json)
username = datos_json.get('username', '')
api_token = datos_json.get('api_token', '')
domain_name = datos_json.get('domain_name', '')
sleep(10)
response = requests.post(
    'https://www.pythonanywhere.com/api/v0/user/{username}/webapps/{domain_name}/reload/'.format(
        username=username, domain_name=domain_name
    ),
    headers={'Authorization': 'Token {token}'.format(token=api_token)}
)
if response.status_code == 200:
    print('reloaded OK')
else:
    print('Got unexpected status code {}: {!r}'.format(response.status_code, response.content))