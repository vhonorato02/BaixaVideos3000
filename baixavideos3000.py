import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from yt_dlp import YoutubeDL
import shutil
from queue import Queue
import threading
from datetime import datetime
import json

class DownloadItem:
    def __init__(self, url, format_choice, resolution_choice):
        self.url = url
        self.format_choice = format_choice
        self.resolution_choice = resolution_choice
        self.progress = 0
        self.status = "Na fila"  # Na fila, Baixando, Concluído, Erro
        self.title = "Carregando..."
        self.id = datetime.now().strftime("%Y%m%d_%H%M%S")

class BaixaVideos3000:
    def __init__(self):
        self.TEMP_DIR = "videosFoda"
        self.config_file = "downloader_config.json"
        self.load_config()
        
        if not os.path.exists(self.TEMP_DIR):
            os.makedirs(self.TEMP_DIR)
            
        self.download_queue = Queue()
        self.downloads = []  # Lista para manter referência dos downloads
        
        self.setup_ui()
        self.start_queue_processor()
    
    def load_config(self):
        try:
            # Obtém o caminho da pasta Downloads do usuário atual
            downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
            
            # Se existe um arquivo de configuração, carrega ele
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.DESTINO = config.get('download_path', downloads_path)
            else:
                # Se não existe, usa a pasta Downloads como padrão
                self.DESTINO = downloads_path
                self.save_config()
                
        except Exception as e:
            # Em caso de qualquer erro, usa a pasta Downloads como fallback
            self.DESTINO = os.path.join(os.path.expanduser('~'), 'Downloads')
            self.save_config()
    
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump({'download_path': self.DESTINO}, f)
    
    def setup_ui(self):
        self.root = tk.Tk()
        self.root.title("Baixa Videos 3000 by Reginaldo Horse")
        self.root.geometry("800x600")
        
        # Frame superior para entrada de URL e controles
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # URL input
        ttk.Label(top_frame, text="Link do vídeo:").pack(side=tk.LEFT, padx=5)
        self.url_entry = ttk.Entry(top_frame, width=50)
        self.url_entry.pack(side=tk.LEFT, padx=5)
        
        # Formato selection
        self.format_var = tk.StringVar(value="MP4")
        ttk.Radiobutton(top_frame, text="MP4", variable=self.format_var, 
                       value="MP4").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(top_frame, text="MP3", variable=self.format_var, 
                       value="MP3").pack(side=tk.LEFT, padx=5)
        
        # Resolução selection
        self.resolution_var = tk.StringVar(value="Melhor Qualidade")
        self.resolution_menu = ttk.Combobox(top_frame, textvariable=self.resolution_var, 
                                          state="readonly", width=15)
        self.resolution_menu['values'] = ["Melhor Qualidade", "8K", "4K", "1080p", "720p", "360p"]
        self.resolution_menu.pack(side=tk.LEFT, padx=5)
        
        # Add to queue button
        ttk.Button(top_frame, text="Adicionar à Fila", 
                  command=self.add_to_queue).pack(side=tk.LEFT, padx=5)
        
        # Downloads list
        list_frame = ttk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Treeview for downloads
        columns = ('title', 'format', 'resolution', 'progress', 'status')
        self.downloads_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # Configure columns
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
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                command=self.downloads_tree.yview)
        self.downloads_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack list and scrollbar
        self.downloads_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bottom frame for download path
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(bottom_frame, text="Pasta de Download:").pack(side=tk.LEFT, padx=5)
        self.path_var = tk.StringVar(value=self.DESTINO)
        self.path_entry = ttk.Entry(bottom_frame, textvariable=self.path_var, width=50, state='readonly')
        self.path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Button(bottom_frame, text="Alterar Pasta", 
                  command=self.change_download_path).pack(side=tk.LEFT, padx=5)
    
    def get_format_string(self, resolution_choice):
        if resolution_choice == "Melhor Qualidade":
            return "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]"
        elif resolution_choice == "8K":
            return "bestvideo[height<=4320][ext=mp4]+bestaudio[ext=m4a]/best[height<=4320][ext=mp4]"
        elif resolution_choice == "4K":
            return "bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]/best[height<=2160][ext=mp4]"
        elif resolution_choice == "1080p":
            return "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]"
        elif resolution_choice == "720p":
            return "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]"
        elif resolution_choice == "360p":
            return "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]"
        return "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]"
    
    def change_download_path(self):
        new_path = filedialog.askdirectory(initialdir=self.DESTINO)
        if new_path:
            self.DESTINO = new_path
            self.path_var.set(new_path)
            self.save_config()
    
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            # Calculate progress
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            if total_bytes > 0:
                downloaded_bytes = d.get('downloaded_bytes', 0)
                progress = (downloaded_bytes / total_bytes) * 100
                
                # Update progress in tree
                current_download = self.downloads[-1]  # Get the latest download
                current_download.progress = progress
                self.root.after(100, self.update_tree_item, current_download)
    
    def update_tree_item(self, download_item):
        try:
            item_id = str(download_item.id)
            self.downloads_tree.set(item_id, 'progress', f"{download_item.progress:.1f}%")
            self.downloads_tree.set(item_id, 'status', download_item.status)
            self.downloads_tree.set(item_id, 'title', download_item.title)
        except tk.TkError:
            pass  # Item might have been deleted
    
    def add_to_queue(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Erro", "Por favor, insira um link do vídeo!")
            return
        
        # Create download item
        download_item = DownloadItem(
            url=url,
            format_choice=self.format_var.get(),
            resolution_choice=self.resolution_var.get()
        )
        
        # Add to our tracking list and queue
        self.downloads.append(download_item)
        self.download_queue.put(download_item)
        
        # Add to tree
        self.downloads_tree.insert('', 'end', iid=str(download_item.id),
                                 values=(download_item.title,
                                        download_item.format_choice,
                                        download_item.resolution_choice,
                                        "0%",
                                        "Na fila"))
        
        # Clear entry
        self.url_entry.delete(0, tk.END)
    
    def start_queue_processor(self):
        def process_queue():
            while True:
                try:
                    download_item = self.download_queue.get()
                    self.process_download(download_item)
                    self.download_queue.task_done()
                except Exception as e:
                    print(f"Error processing queue: {e}")
        
        thread = threading.Thread(target=process_queue, daemon=True)
        thread.start()
    
    def process_download(self, download_item):
        download_item.status = "Baixando"
        self.root.after(100, self.update_tree_item, download_item)
        
        ydl_opts = {
            'outtmpl': os.path.join(self.TEMP_DIR, '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],
            'retries': 10,
            'fragment_retries': 10,
            'skip_unavailable_fragments': False,
            'nocheckcertificate': True,
            'http_chunk_size': 1024 * 1024,
        }
        
        # Configure format options
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
                # Get video info first
                info = ydl.extract_info(download_item.url, download=False)
                download_item.title = info.get('title', 'Unknown Title')
                self.root.after(100, self.update_tree_item, download_item)
                
                # Download video
                ydl.download([download_item.url])
                
                # Move file to destination
                arquivo_baixado = ydl.prepare_filename(info)
                extensao_final = "mp3" if download_item.format_choice == "MP3" else "mp4"
                arquivo_final = arquivo_baixado.rsplit(".", 1)[0] + f".{extensao_final}"
                
                if os.path.exists(arquivo_final):
                    destino_final = os.path.join(self.DESTINO, os.path.basename(arquivo_final))
                    shutil.move(arquivo_final, destino_final)
                    download_item.status = "Concluído"
                else:
                    download_item.status = "Erro"
        except Exception as e:
            download_item.status = f"Erro: {str(e)}"
        
        self.root.after(100, self.update_tree_item, download_item)

if __name__ == "__main__":
    app = BaixaVideos3000()
    app.root.mainloop()