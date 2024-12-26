import os
import requests
from msal import ConfidentialClientApplication
from dotenv import load_dotenv
load_dotenv()
# Configuración de la aplicación
CLIENT_ID = os.getenv('CLIENTEID')
TENANT_ID = os.getenv('TENANTID')
CLIENT_SECRET = os.getenv('CLIENTESECRET')
SCOPES = ["https://graph.microsoft.com/.default"]
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"

# Ruta del token (opcional para persistencia)
TOKEN_CACHE = os.getenv('TOKENCHACHE')

# Inicializar la aplicación MSAL
# Inicializar la aplicación MSAL
app = ConfidentialClientApplication(
    client_id=CLIENT_ID,
    authority=AUTHORITY,
    client_credential=CLIENT_SECRET
)

def get_access_token():
    """
    Obtiene un token de acceso desde MSAL.
    """
    result = app.acquire_token_for_client(scopes=SCOPES)
    if "access_token" in result:
        return result["access_token"]
    else:
        raise Exception(f"Error al obtener el token: {result.get('error_description')}")


def upload_to_onedrive(file_path, folder_id=None):
    """
    Sube un archivo a OneDrive.
    :param file_path: Ruta local del archivo.
    :param folder_id: ID de la carpeta en OneDrive (opcional).
    :return: URL del archivo subido.
    """
    access_token = get_access_token()

    # URL base para subir archivos
    if folder_id:
        upload_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{folder_id}:/{os.path.basename(file_path)}:/content"
    else:
        upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{os.path.basename(file_path)}:/content"

    with open(file_path, "rb") as f:
        response = requests.put(
            upload_url,
            headers={"Authorization": f"Bearer {access_token}"},
            data=f,
        )

    if response.status_code == 201 or response.status_code == 200:
        print("Archivo subido con éxito.")
        return response.json().get("@microsoft.graph.downloadUrl")
    else:
        raise Exception(f"Error al subir archivo: {response.json()}")


def download_from_onedrive(file_id, save_path):
    """
    Descarga un archivo desde OneDrive.
    :param file_id: ID del archivo en OneDrive.
    :param save_path: Ruta donde guardar el archivo.
    """
    access_token = get_access_token()

    download_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content"

    response = requests.get(download_url, headers={"Authorization": f"Bearer {access_token}"}, stream=True)

    if response.status_code == 200:
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Archivo descargado en: {save_path}")
    else:
        raise Exception(f"Error al descargar archivo: {response.json()}")


def list_onedrive_files(folder_id=None):
    """
    Lista archivos en OneDrive.
    :param folder_id: ID de la carpeta en OneDrive (opcional).
    :return: Lista de archivos y carpetas.
    """
    access_token = get_access_token()

    if folder_id:
        url = f"https://graph.microsoft.com/v1.0/me/drive/items/{folder_id}/children"
    else:
        url = "https://graph.microsoft.com/v1.0/me/drive/root/children"

    response = requests.get(url, headers={"Authorization": f"Bearer {access_token}"})

    if response.status_code == 200:
        files = response.json().get("value", [])
        for file in files:
            print(f"Nombre: {file['name']}, ID: {file['id']}")
        return files
    else:
        raise Exception(f"Error al listar archivos: {response.json()}")

def list_folder_contents(folder_id):
    """
    Lista los contenidos de una carpeta específica en OneDrive.
    """
    access_token = get_access_token()

    url = f"https://graph.microsoft.com/v1.0/me/drive/items/{folder_id}/children"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        items = response.json().get("value", [])
        for item in items:
            print(f"Nombre: {item['name']}, ID: {item['id']}, Tipo: {'Carpeta' if item['folder'] else 'Archivo'}")
    else:
        raise Exception(f"Error al listar contenidos: {response.json()}")

import requests

def get_folder_id_from_sharepoint(site_id, folder_path):
    """
    Obtiene el ID de una carpeta en SharePoint.
    :param site_id: El ID del sitio de SharePoint.
    :param folder_path: La ruta de la carpeta dentro del sitio.
    :return: ID de la carpeta.
    """
    access_token = get_access_token()  # Utiliza tu función para obtener el token de acceso

    url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:{folder_path}:/children"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        items = response.json().get("value", [])
        for item in items:
            if 'folder' in item:  # Solo seleccionamos carpetas
                print(f"Nombre de la carpeta: {item['name']}, ID: {item['id']}")
                return item['id']
    else:
        raise Exception(f"Error al obtener la carpeta: {response.json()}")

def get_site_id(urlid):
    access_token = get_access_token()
    url = urlid
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        site_id = response.json().get("id")
        print(f"Site ID: {site_id}")
        return site_id
    else:
        raise Exception(f"Error al obtener el site-id: {response.json()}")