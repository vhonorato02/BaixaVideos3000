import os
import json
import logging
from typing import List, Dict, Any

class Config:
    DEFAULT_CONFIG = {
        "download_path": os.path.join(os.path.expanduser("~"), "Downloads"),
        "theme": "Escuro",
        "language": "pt_BR",
        "max_concurrent_downloads": 3,
        "history": [],
        "auto_delete_completed": False,
        "notifications_enabled": True,
        "save_subtitles": False,
        "preferred_quality": "1080p",
        "preferred_format": "mp4",
        "version": "0.0.3"
    }

    def __init__(self, config_file="downloader_config.json"):
        self.config_file = config_file
        self.config = self.load()
        # Define a pasta padrão de download como a pasta "Downloads" do usuário se não estiver definida
        if "download_folder" not in self.config:
            self.config["download_folder"] = os.path.join(os.path.expanduser("~"), "Downloads")
            self.save()

    def load(self) -> dict:
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding='utf-8') as f:
                    config = json.load(f)
                    # Atualiza com configurações padrão faltantes
                    return {**self.DEFAULT_CONFIG, **config}
            except Exception as e:
                logging.error(f"Erro ao ler configuração: {e}")
        return self.DEFAULT_CONFIG.copy()

    def save(self):
        try:
            with open(self.config_file, "w", encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Erro ao salvar configuração: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        self.config[key] = value
        self.save()

    def add_to_history(self, download_info: Dict):
        """Adiciona um download ao histórico"""
        history = self.get("history", [])
        history.insert(0, download_info)  # Adiciona no início da lista
        # Mantém apenas os últimos 100 downloads
        self.set("history", history[:100])

    def clear_history(self):
        """Limpa o histórico de downloads"""
        self.set("history", [])

    @property
    def download_path(self) -> str:
        return self.get("download_path")

    @download_path.setter
    def download_path(self, value: str):
        self.set("download_path", value)

    @property
    def theme(self) -> str:
        return self.get("theme")

    @theme.setter
    def theme(self, value: str):
        self.set("theme", value)

    @property
    def language(self) -> str:
        return self.get("language")

    @language.setter
    def language(self, value: str):
        self.set("language", value)

    def __setitem__(self, key: str, value: Any):
        self.config[key] = value

    def __getitem__(self, key: str) -> Any:
        return self.config.get(key)

# Versão atual do aplicativo
CURRENT_VERSION = "0.0.3"

# Função para buscar atualizações automaticamente (comentada para uso futuro)
# def check_updates(parent):
#     try:
#         response = requests.get("https://api.github.com/repos/ReginaldoHorse/BaixaVideos3000/releases/latest", timeout=5)
#         if response.status_code == 200:
#             release_info = response.json()
#             latest_version = release_info.get("tag_name", "")
#             if latest_version and latest_version != CURRENT_VERSION:
#                 QMessageBox.information(parent, "Atualização Disponível",
#                                         f"Uma nova versão ({latest_version}) está disponível no GitHub.\n"
#                                         "Acesse https://github.com/ReginaldoHorse/BaixaVideos3000/ para atualizar.")
#     except Exception as e:
#         logging.error("Erro ao buscar atualizações: " + str(e))