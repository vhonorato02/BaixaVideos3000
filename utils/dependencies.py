import os
import sys
import subprocess
import logging
import shutil
import zipfile
import requests
from pathlib import Path
from PyQt5.QtCore import QThread, pyqtSignal

class FFmpegInstaller(QThread):
    progress_signal = pyqtSignal(str)  # Para enviar mensagens de progresso
    finished_signal = pyqtSignal(bool)  # True se instalou com sucesso, False se falhou

    def run(self):
        try:
            if check_ffmpeg():
                self.finished_signal.emit(True)
                return

            self.progress_signal.emit("Iniciando instalação do FFmpeg...")
            
            # Cria diretório para armazenar o FFmpeg se não existir
            ffmpeg_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ffmpeg')
            os.makedirs(ffmpeg_dir, exist_ok=True)
            
            # URL do FFmpeg para Windows (versão estática)
            ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
            
            # Download do arquivo
            self.progress_signal.emit("Baixando FFmpeg...")
            response = requests.get(ffmpeg_url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            zip_path = os.path.join(ffmpeg_dir, 'ffmpeg.zip')
            
            block_size = 8192
            downloaded = 0
            
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=block_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size:
                            percent = (downloaded / total_size) * 100
                            self.progress_signal.emit(f"Baixando FFmpeg... {percent:.1f}%")
            
            # Extrai o arquivo
            self.progress_signal.emit("Extraindo FFmpeg...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(ffmpeg_dir)
            
            # Move os executáveis para o diretório principal do FFmpeg
            self.progress_signal.emit("Configurando FFmpeg...")
            ffmpeg_bin_dir = next(Path(ffmpeg_dir).rglob('bin'))
            for exe in ffmpeg_bin_dir.glob('*.exe'):
                shutil.move(str(exe), ffmpeg_dir)
            
            # Limpa arquivos temporários
            os.remove(zip_path)
            shutil.rmtree(next(Path(ffmpeg_dir).glob('ffmpeg-*')))
            
            # Adiciona o diretório ao PATH
            if ffmpeg_dir not in os.environ['PATH']:
                os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ['PATH']
            
            self.progress_signal.emit("FFmpeg instalado com sucesso!")
            self.finished_signal.emit(True)
            
        except Exception as e:
            error_msg = f"Erro ao instalar FFmpeg: {str(e)}"
            logging.error(error_msg)
            self.progress_signal.emit(error_msg)
            self.finished_signal.emit(False)

def check_ffmpeg():
    """Verifica se o FFmpeg está instalado e acessível"""
    try:
        # Primeiro verifica na pasta local
        ffmpeg_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ffmpeg')
        if os.path.exists(os.path.join(ffmpeg_dir, 'ffmpeg.exe')):
            if ffmpeg_dir not in os.environ['PATH']:
                os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ['PATH']
            return True
            
        # Se não encontrar, verifica no PATH do sistema
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False

class YtDlpUpdater(QThread):
    progress_signal = pyqtSignal(str)  # Para enviar mensagens de progresso
    finished_signal = pyqtSignal(bool)  # True se atualizou com sucesso, False se falhou

    def run(self):
        try:
            self.progress_signal.emit("Atualizando yt-dlp...")
            subprocess.run(["pip", "install", "--upgrade", "yt-dlp"], check=True)
            self.progress_signal.emit("yt-dlp atualizado com sucesso!")
            self.finished_signal.emit(True)
        except subprocess.CalledProcessError as e:
            error_msg = f"Erro ao atualizar yt-dlp: {str(e)}"
            logging.error(error_msg)
            self.progress_signal.emit(error_msg)
            self.finished_signal.emit(False)