import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from yt_dlp import YoutubeDL
import shutil
from queue import Queue
import threading
from datetime import datetime
import json
import logging
from typing import Any, Dict
import time

# Configuração do logging para facilitar o debug
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')


class DownloadItem:
    """
    Representa um item de download com URL, formato, resolução, progresso e status.
    """
    def __init__(self, url: str, format_choice: str, resolution_choice: str) -> None:
        self.url = url
        self.format_choice = format_choice
        self.resolution_choice = resolution_choice
        self.progress: float = 0.0
        self.status: str = "Na fila"  # Possíveis valores: Na fila, Baixando, Concluído, Erro
        self.title: str = "Carregando..."
        # Utiliza microssegundos para garantir unicidade
        self.id: str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")


class BaixaVideos3000:
    """
    Aplicação para baixar vídeos utilizando yt_dlp e uma interface gráfica em Tkinter.
    Versão Alpha 0.0.1
    """
    def __init__(self) -> None:
        self.TEMP_DIR: str = "videosFoda"  # Nome irreverente que nos agrada!
        self.config_file: str = "downloader_config.json"
        self.load_config()

        if not os.path.exists(self.TEMP_DIR):
            os.makedirs(self.TEMP_DIR)

        self.download_queue: Queue[DownloadItem] = Queue()
        self.downloads: list[DownloadItem] = []  # Lista para manter referência dos downloads

        self.setup_ui()
        self.start_queue_processor()

    def load_config(self) -> None:
        """
        Carrega as configurações do arquivo JSON ou define a pasta padrão (Downloads do usuário).
        """
        try:
            downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.DESTINO = config.get('download_path', downloads_path)
            else:
                self.DESTINO = downloads_path
                self.save_config()
        except Exception as e:
            logging.error(f"Erro ao carregar configuração: {e}")
            self.DESTINO = os.path.join(os.path.expanduser('~'), 'Downloads')
            self.save_config()

    def save_config(self) -> None:
        """Salva a configuração atual no arquivo JSON."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump({'download_path': self.DESTINO}, f)
        except Exception as e:
            logging.error(f"Erro ao salvar configuração: {e}")

    def setup_ui(self) -> None:
        """Configura a interface gráfica da aplicação."""
        self.root = tk.Tk()
        self.root.title("Baixa Videos 3000 by Reginaldo Horse")
        self.root.geometry("800x600")

        # Frame superior: entrada de URL e controles
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(top_frame, text="Link do vídeo:").pack(side=tk.LEFT, padx=5)
        self.url_entry = ttk.Entry(top_frame, width=50)
        self.url_entry.pack(side=tk.LEFT, padx=5)

        # Seletor de formato
        self.format_var = tk.StringVar(value="MP4")
        ttk.Radiobutton(top_frame, text="MP4", variable=self.format_var, value="MP4").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(top_frame, text="MP3", variable=self.format_var, value="MP3").pack(side=tk.LEFT, padx=5)

        # Seletor de resolução
        self.resolution_var = tk.StringVar(value="Melhor Qualidade")
        self.resolution_menu = ttk.Combobox(top_frame, textvariable=self.resolution_var, state="readonly", width=15)
        self.resolution_menu['values'] = ["Melhor Qualidade", "8K", "4K", "1080p", "720p", "360p"]
        self.resolution_menu.pack(side=tk.LEFT, padx=5)

        # Botão para adicionar o download à fila
        ttk.Button(top_frame, text="Adicionar à Fila", command=self.add_to_queue).pack(side=tk.LEFT, padx=5)

        # Frame para a lista de downloads
        list_frame = ttk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ('title', 'format', 'resolution', 'progress', 'status')
        self.downloads_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        self.downloads_tree.heading('title', text='Título')
        self.downloads_tree.heading('format', text='Formato')
        self.downloads_tree.heading('resolution', text='Resolução')
        self.downloads_tree.heading('progress', text='Progresso')
        self.downloads_tree.heading('status', text='Status')

        self.downloads_tree.column('title', width=300)
        self.downloads_tree.column('format', width=70)
        self.downloads_tree.column('resolution', width=100)
        self.downloads_tree.column('progress', width=100)
        self.downloads_tree.column('status', width=100)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.downloads_tree.yview)
        self.downloads_tree.configure(yscrollcommand=scrollbar.set)
        self.downloads_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Frame inferior: seleção da pasta de download
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(bottom_frame, text="Pasta de Download:").pack(side=tk.LEFT, padx=5)
        self.path_var = tk.StringVar(value=self.DESTINO)
        self.path_entry = ttk.Entry(bottom_frame, textvariable=self.path_var, width=50, state='readonly')
        self.path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        ttk.Button(bottom_frame, text="Alterar Pasta", command=self.change_download_path).pack(side=tk.LEFT, padx=5)

    def get_format_string(self, resolution_choice: str) -> str:
        """
        Retorna a string de formato para o yt_dlp baseado na resolução desejada.
        """
        mapping = {
            "Melhor Qualidade": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
            "8K": "bestvideo[height<=4320][ext=mp4]+bestaudio[ext=m4a]/best[height<=4320][ext=mp4]",
            "4K": "bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]/best[height<=2160][ext=mp4]",
            "1080p": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]",
            "720p": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]",
            "360p": "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]",
        }
        return mapping.get(resolution_choice, mapping["Melhor Qualidade"])

    def change_download_path(self) -> None:
        """Abre um diálogo para alterar a pasta de download."""
        new_path = filedialog.askdirectory(initialdir=self.DESTINO)
        if new_path:
            self.DESTINO = new_path
            self.path_var.set(new_path)
            self.save_config()

    def update_tree_item(self, download_item: DownloadItem) -> None:
        """Atualiza o item na Treeview com o status e progresso atuais."""
        try:
            item_id = str(download_item.id)
            self.downloads_tree.set(item_id, 'progress', f"{download_item.progress:.1f}%")
            self.downloads_tree.set(item_id, 'status', download_item.status)
            self.downloads_tree.set(item_id, 'title', download_item.title)
        except tk.TclError:
            pass  # O item pode ter sido removido da árvore

    def add_to_queue(self) -> None:
        """Adiciona um novo download à fila."""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Erro", "Por favor, insira um link do vídeo!")
            return

        # Se for Instagram e o link estiver no formato /p/, converte para /reel/ (solução para reels)
        if "instagram.com" in url.lower():
            if "/p/" in url.lower() and "/reel/" not in url.lower():
                new_url = url.replace("/p/", "/reel/")
                logging.info("Link de Instagram modificado para formato de Reels: " + new_url)
                url = new_url

        # Força "Melhor Qualidade" para vídeos do Twitter ou Instagram para evitar erros conhecidos
        if ("twitter.com" in url.lower() or "instagram.com" in url.lower()) and self.resolution_var.get() != "Melhor Qualidade":
            logging.info("Forçando 'Melhor Qualidade' para vídeos do Twitter/Instagram.")
            resolution_choice = "Melhor Qualidade"
        else:
            resolution_choice = self.resolution_var.get()

        download_item = DownloadItem(
            url=url,
            format_choice=self.format_var.get(),
            resolution_choice=resolution_choice
        )

        self.downloads.append(download_item)
        self.download_queue.put(download_item)

        self.downloads_tree.insert(
            '',
            'end',
            iid=str(download_item.id),
            values=(
                download_item.title,
                download_item.format_choice,
                download_item.resolution_choice,
                "0%",
                "Na fila"
            )
        )

        self.url_entry.delete(0, tk.END)

    def start_queue_processor(self) -> None:
        """
        Inicia threads daemon para processar a fila de downloads em paralelo.
        Cada item da fila é processado em sua própria thread.
        """
        def worker():
            while True:
                download_item = self.download_queue.get()
                thread = threading.Thread(target=self.process_download, args=(download_item,))
                thread.daemon = True
                thread.start()
                self.download_queue.task_done()
        threading.Thread(target=worker, daemon=True).start()

    def process_download(self, download_item: DownloadItem) -> None:
        """
        Processa o download de um item utilizando yt_dlp.
        Utiliza uma função de hook de progresso local para atualizar corretamente o progresso.
        """
        download_item.status = "Baixando"
        self.root.after(100, self.update_tree_item, download_item)

        def progress_hook_local(d: Dict[str, Any]) -> None:
            if d.get('status') == 'downloading':
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                if total_bytes:
                    downloaded_bytes = d.get('downloaded_bytes', 0)
                    progress = (downloaded_bytes / total_bytes) * 100
                    download_item.progress = progress
                    self.root.after(100, self.update_tree_item, download_item)

        ydl_opts: Dict[str, Any] = {
            'outtmpl': os.path.join(self.TEMP_DIR, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook_local],
            'retries': 10,
            'fragment_retries': 10,
            'skip_unavailable_fragments': False,
            'nocheckcertificate': True,
            'http_chunk_size': 1024 * 1024,
        }

        # Se o vídeo for da Twitch, ajusta opções para melhorar a velocidade de download
        if "twitch.tv" in download_item.url.lower():
            ydl_opts['concurrent_fragment_downloads'] = 4

        if download_item.format_choice == "MP3":
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            ydl_opts['format'] = self.get_format_string(download_item.resolution_choice)

        try:
            with YoutubeDL(ydl_opts) as ydl:
                # Extrai informações para atualizar o título do vídeo
                info = ydl.extract_info(download_item.url, download=False)
                download_item.title = info.get('title', 'Unknown Title')
                self.root.after(100, self.update_tree_item, download_item)

                # Realiza o download
                ydl.download([download_item.url])

                # Prepara o nome do arquivo final
                arquivo_baixado = ydl.prepare_filename(info)
                extensao_final = "mp3" if download_item.format_choice == "MP3" else "mp4"
                arquivo_final = arquivo_baixado.rsplit(".", 1)[0] + f".{extensao_final}"

                # Aguarda até 5 segundos para o arquivo aparecer na pasta
                timeout = 5
                for i in range(timeout):
                    if os.path.exists(arquivo_final):
                        break
                    time.sleep(1)

                if os.path.exists(arquivo_final):
                    destino_final = os.path.join(self.DESTINO, os.path.basename(arquivo_final))
                    shutil.move(arquivo_final, destino_final)
                    download_item.status = "Concluído"
                else:
                    download_item.status = "Erro: Arquivo não encontrado após 5 segundos."
        except Exception as e:
            msg = str(e)
            if "live" in msg.lower():
                download_item.status = "Erro: Live não finalizada ou processada."
            else:
                download_item.status = f"Erro: {e}"
            logging.error(f"Erro no download '{download_item.url}': {e}")

        self.root.after(100, self.update_tree_item, download_item)


if __name__ == "__main__":
    app = BaixaVideos3000()
    app.root.mainloop()