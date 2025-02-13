from typing import Dict

class I18n:
    TRANSLATIONS = {
        "pt_BR": {
            "app_title": "Baixa Videos 3000 by Reginaldo Horse",
            "download_folder": "Pasta de Download",
            "change_folder": "Alterar Pasta",
            "theme": "Tema",
            "dark": "Escuro",
            "light": "Claro",
            "language": "Idioma",
            "apply_settings": "Aplicar Configurações",
            "settings_saved": "Configurações aplicadas com sucesso.",
            "video_url": "Link do Vídeo",
            "format": "Formato",
            "resolution": "Resolução",
            "add_to_queue": "Adicionar à Fila",
            "clear_completed": "Limpar Finalizados",
            "retry_download": "Reiniciar Download",
            "remove_selected": "Remover Selecionado",
            "cancel_download": "Cancelar Download",
            "status_queued": "Na fila",
            "status_downloading": "Baixando",
            "status_processing": "Processando",
            "status_completed": "Concluído",
            "status_error": "Erro",
            "status_cancelled": "Cancelado",
            "error_no_url": "Por favor, insira a URL do vídeo.",
            "error_ffmpeg": "Não foi possível instalar o FFmpeg automaticamente. Alguns recursos podem não funcionar corretamente.",
            "history": "Histórico",
            "clear_history": "Limpar Histórico",
            "export_history": "Exportar Histórico",
            "no_items_selected": "Nenhum item selecionado.",
            "confirm_delete": "Confirmar exclusão",
            "confirm_clear_history": "Tem certeza que deseja limpar o histórico?",
            "settings": "Configurações",
            "downloads": "Downloads",
            "logs": "Logs",
            "title": "Título",
            "progress": "Progresso",
            "status": "Status",
            "added": "Adicionado",
            "action": "Ação",
            "open": "Abrir",
            "installing_ffmpeg": "Instalando FFmpeg",
            "checking_ffmpeg": "Verificando FFmpeg...",
            "warning": "Aviso",
            "information": "Informação",
            "export_log": "Exportar Log",
            "clear_logs": "Limpar Logs",
            "log_exported": "Log exportado com sucesso",
            "error_retry": "Somente downloads com erro podem ser reiniciados.",
            "select_to_retry": "Nenhum item selecionado para reiniciar.",
            "select_to_cancel": "Nenhum item selecionado para cancelar.",
            "select_to_remove": "Nenhum item selecionado para remover.",
            "video_mp4": "Vídeo - MP4",
            "music_mp3": "Música - MP3",
            "best_quality": "Melhor Qualidade"
        },
        "en_US": {
            "app_title": "Video Downloader 3000 by Reginaldo Horse",
            "download_folder": "Download Folder",
            "change_folder": "Change Folder",
            "theme": "Theme",
            "dark": "Dark",
            "light": "Light",
            "language": "Language",
            "apply_settings": "Apply Settings",
            "settings_saved": "Settings applied successfully.",
            "video_url": "Video URL",
            "format": "Format",
            "resolution": "Resolution",
            "add_to_queue": "Add to Queue",
            "clear_completed": "Clear Completed",
            "retry_download": "Retry Download",
            "remove_selected": "Remove Selected",
            "cancel_download": "Cancel Download",
            "status_queued": "Queued",
            "status_downloading": "Downloading",
            "status_processing": "Processing",
            "status_completed": "Completed",
            "status_error": "Error",
            "status_cancelled": "Cancelled",
            "error_no_url": "Please enter the video URL.",
            "error_ffmpeg": "Could not install FFmpeg automatically. Some features may not work properly.",
            "history": "History",
            "clear_history": "Clear History",
            "export_history": "Export History",
            "no_items_selected": "No items selected.",
            "confirm_delete": "Confirm deletion",
            "confirm_clear_history": "Are you sure you want to clear the history?",
            "settings": "Settings",
            "downloads": "Downloads",
            "logs": "Logs",
            "title": "Title",
            "progress": "Progress",
            "status": "Status",
            "added": "Added",
            "action": "Action",
            "open": "Open",
            "installing_ffmpeg": "Installing FFmpeg",
            "checking_ffmpeg": "Checking FFmpeg...",
            "warning": "Warning",
            "information": "Information",
            "export_log": "Export Log",
            "clear_logs": "Clear Logs",
            "log_exported": "Log exported successfully",
            "error_retry": "Only downloads with errors can be retried.",
            "select_to_retry": "No item selected to retry.",
            "select_to_cancel": "No item selected to cancel.",
            "select_to_remove": "No item selected to remove.",
            "video_mp4": "Video - MP4",
            "music_mp3": "Music - MP3",
            "best_quality": "Best Quality"
        }
    }

    def __init__(self, language: str = "pt_BR"):
        self.language = language

    def get(self, key: str) -> str:
        """Retorna a tradução para a chave especificada"""
        return self.TRANSLATIONS.get(self.language, {}).get(key, key)

    def set_language(self, language: str):
        """Define o idioma atual"""
        if language in self.TRANSLATIONS:
            self.language = language

    @property
    def available_languages(self) -> Dict[str, str]:
        """Retorna os idiomas disponíveis"""
        return {
            "pt_BR": "Português (Brasil)",
            "en_US": "English (US)"
        } 