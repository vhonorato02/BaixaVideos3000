from datetime import datetime

class DownloadItem:
    def __init__(self, url: str, format_choice: str, resolution_choice: str):
        self.url = url
        self.format_choice = format_choice
        self.resolution_choice = resolution_choice
        self.progress = 0.0
        self.status = "Na fila"  # "Na fila", "Baixando", "Concluído", "Erro", "Cancelado"
        self.title = "Carregando..."
        self.id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        self.added_at = datetime.now().strftime("%H:%M:%S %d/%m")
        self.cancelled = False
        self.file_path = ""  # Armazena o caminho do arquivo baixado 