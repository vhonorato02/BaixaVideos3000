import os
import uuid
import time

class DownloadItem:
    def __init__(self, url, format_choice, resolution_choice):
        self.id = str(uuid.uuid4())
        self.url = url
        self.format_choice = format_choice
        self.resolution_choice = resolution_choice
        self.title = ""
        self.status = "Na fila"
        self.progress = 0.0
        self.cancelled = False
        self.added_at = time.strftime("%Y-%m-%d %H:%M:%S")
        self.file_path = ""  # Inicializa o caminho do arquivo

    def set_file_path(self, download_path, title):
        ext = ".mp4" if "Vídeo" in self.format_choice else ".mp3"
        self.file_path = os.path.join(download_path, f"{title}{ext}")