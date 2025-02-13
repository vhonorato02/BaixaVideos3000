from datetime import datetime
from typing import List, Dict
import json

class DownloadHistory:
    def __init__(self):
        self.items: List[Dict] = []

    def add_item(self, url: str, title: str, format: str, resolution: str, status: str, file_path: str = None):
        """Adiciona um item ao histórico"""
        item = {
            "url": url,
            "title": title,
            "format": format,
            "resolution": resolution,
            "status": status,
            "file_path": file_path,
            "date": datetime.now().isoformat(),
        }
        self.items.insert(0, item)  # Adiciona no início da lista
        if len(self.items) > 100:  # Mantém apenas os últimos 100 downloads
            self.items = self.items[:100]

    def clear(self):
        """Limpa o histórico"""
        self.items.clear()

    def get_items(self, status: str = None) -> List[Dict]:
        """Retorna itens do histórico, opcionalmente filtrados por status"""
        if status:
            return [item for item in self.items if item["status"] == status]
        return self.items

    def export_to_json(self, file_path: str):
        """Exporta o histórico para um arquivo JSON"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.items, f, indent=4, ensure_ascii=False)

    def import_from_json(self, file_path: str):
        """Importa o histórico de um arquivo JSON"""
        with open(file_path, 'r', encoding='utf-8') as f:
            self.items = json.load(f)

    def get_statistics(self) -> Dict:
        """Retorna estatísticas do histórico"""
        total = len(self.items)
        completed = len([i for i in self.items if i["status"] == "Concluído"])
        failed = len([i for i in self.items if i["status"].startswith("Erro")])
        cancelled = len([i for i in self.items if i["status"] == "Cancelado"])
        
        formats = {}
        resolutions = {}
        for item in self.items:
            formats[item["format"]] = formats.get(item["format"], 0) + 1
            resolutions[item["resolution"]] = resolutions.get(item["resolution"], 0) + 1
        
        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "cancelled": cancelled,
            "success_rate": (completed / total * 100) if total > 0 else 0,
            "formats": formats,
            "resolutions": resolutions
        } 