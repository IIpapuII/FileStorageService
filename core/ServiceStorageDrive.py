import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.oauth2.service_account import Credentials
from io import BytesIO
from dotenv import load_dotenv
load_dotenv()

# Ruta al archivo de credenciales JSON descargado desde Google Cloud
CREDENTIALS_FILE = os.getenv('PATHFILECREDENTIALS')

def get_service():
    """
    Crea una instancia del cliente de Google Drive.
    :return: Servicio de Google Drive.
    """
    if not os.path.exists(CREDENTIALS_FILE):
        raise FileNotFoundError("El archivo de credenciales JSON no se encontró.")
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE)
    return build('drive', 'v3', credentials=creds)

def upload_to_drive(file_path, folder_id=None):
    """
    Sube un archivo a Google Drive.
    :param file_path: Ruta al archivo local a subir.
    :param folder_id: ID de la carpeta en Google Drive (opcional).
    :return: URL del archivo subido.
    """
    service = get_service()

    # Configurar los metadatos del archivo
    file_metadata = {'name': os.path.basename(file_path)}
    if folder_id:
        file_metadata['parents'] = [folder_id]

    # Subir el archivo
    media = MediaFileUpload(file_path, resumable=True)
    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()

    return uploaded_file.get('webViewLink','id')  # Devuelve el enlace público

def search_file(name, folder_id=None):
    """
    Busca un archivo por su nombre en Google Drive.
    :param name: Nombre del archivo a buscar.
    :param folder_id: ID de la carpeta en Google Drive (opcional).
    :return: Lista de archivos que coinciden con el nombre.
    """
    service = get_service()
    query = f"name = '{name}' and trashed = false"
    if folder_id:
        query += f" and '{folder_id}' in parents"

    results = service.files().list(q=query, fields="files(id, name, webViewLink)").execute()
    return results.get('files', [])

def download_file(file_id, save_path):
    """
    Descarga un archivo desde Google Drive.
    :param file_id: ID del archivo en Google Drive.
    :param save_path: Ruta donde se guardará el archivo descargado.
    """
    service = get_service()
    request = service.files().get_media(fileId=file_id)
    file_stream = BytesIO()
    downloader = MediaIoBaseDownload(file_stream, request)

    done = False
    while not done:
        _, done = downloader.next_chunk()

    # Escribir el contenido en el archivo local
    with open(save_path, 'wb') as f:
        f.write(file_stream.getvalue())
    print(f"Archivo descargado en: {save_path}")
