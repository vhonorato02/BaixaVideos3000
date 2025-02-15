import os
import shutil
import time
from PyQt5.QtCore import QThread, pyqtSignal
from yt_dlp import YoutubeDL
from models.download_item import DownloadItem

class DownloadThread(QThread):
    progress_signal = pyqtSignal(str, float, str)  # id, progresso, status
    finished_signal = pyqtSignal(str)              # id

    def __init__(self, download_item: DownloadItem, download_folder: str):
        super().__init__()
        self.item = download_item
        self.download_folder = download_folder

    def run(self):
        def progress_hook(d: dict):
            if self.item.cancelled:
                raise Exception("Download cancelado pelo usuário.")
            if d.get('status') == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                if total:
                    downloaded = d.get('downloaded_bytes', 0)
                    progress = (downloaded / total) * 100
                    # Emite o progresso apenas se for maior que o atual para evitar "voltas"
                    if progress >= self.item.progress:
                        self.item.progress = progress
                        self.progress_signal.emit(self.item.id, progress, "Baixando")
            elif d.get('status') == 'finished':
                self.progress_signal.emit(self.item.id, 100.0, "Processando")

        ydl_opts = {
            'outtmpl': os.path.join("temp_downloads", '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
            'retries': 10,
            'fragment_retries': 10,
            'skip_unavailable_fragments': False,
            'nocheckcertificate': True,
            'http_chunk_size': 1024 * 1024,
        }
        if "twitch.tv" in self.item.url.lower():
            ydl_opts['concurrent_fragment_downloads'] = 4
        if self.item.format_choice.upper() == "MÚSICA - MP3":
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            ydl_opts['format'] = {
                "Melhor Qualidade": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
                "8K": "bestvideo[height<=4320][ext=mp4]+bestaudio[ext=m4a]/best[height<=4320][ext=mp4]",
                "4K": "bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]/best[height<=2160][ext=mp4]",
                "1080p": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]",
                "720p": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]",
                "360p": "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]"
            }.get(self.item.resolution_choice, "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]")
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.item.url, download=False)
                self.item.title = info.get('title', 'Unknown Title')
                self.progress_signal.emit(self.item.id, 0, "Baixando")
                ydl.download([self.item.url])
                filename = ydl.prepare_filename(info)
                ext = "mp3" if self.item.format_choice.upper() == "MÚSICA - MP3" else "mp4"
                final_file = filename.rsplit(".", 1)[0] + f".{ext}"
                for _ in range(5):
                    if os.path.exists(final_file):
                        break
                    time.sleep(1)
                if os.path.exists(final_file):
                    destino = os.path.join(self.download_folder, os.path.basename(final_file))
                    shutil.move(final_file, destino)
                    self.item.file_path = destino
                    self.item.status = "Concluído"
                    self.progress_signal.emit(self.item.id, 100.0, "Concluído")
                else:
                    self.item.status = "Erro: Arquivo não encontrado"
                    self.progress_signal.emit(self.item.id, self.item.progress, self.item.status)
        except Exception as e:
            if "cancelado" in str(e).lower():
                self.item.status = "Cancelado"
            else:
                self.item.status = f"Erro: {e}"
            self.progress_signal.emit(self.item.id, self.item.progress, self.item.status)
        self.finished_signal.emit(self.item.id) 