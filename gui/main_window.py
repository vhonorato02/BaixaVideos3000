import os
import logging
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QTabWidget, QLineEdit, QRadioButton, QButtonGroup, QPushButton,
                            QComboBox, QLabel, QTableWidget, QTableWidgetItem, QTextEdit,
                            QMessageBox, QHeaderView, QProgressBar, QDialog, QFileDialog)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont, QIcon

from core.download_manager import DownloadThread
from core.log_handler import LogHandler
from gui.config_dialog import ConfigDialog
from gui.themes import get_dark_theme, get_light_theme
from models.download_item import DownloadItem
from models.history import DownloadHistory
from utils.config import Config
from utils.dependencies import FFmpegInstaller, check_ffmpeg
from utils.i18n import I18n

class FFmpegInstallDialog(QDialog):
    def __init__(self, i18n, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.setWindowTitle(self.i18n.get("installing_ffmpeg"))
        self.setModal(True)
        self.resize(400, 100)
        
        layout = QVBoxLayout()
        
        self.status_label = QLabel(self.i18n.get("checking_ffmpeg"))
        layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Modo indeterminado
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
        
        self.installer = FFmpegInstaller()
        self.installer.progress_signal.connect(self.update_status)
        self.installer.finished_signal.connect(self.installation_finished)
        self.installer.start()
        
    def update_status(self, message):
        self.status_label.setText(message)
        if "%" in message:
            try:
                percent = float(message.split("%")[0].split("...")[-1].strip())
                self.progress_bar.setRange(0, 100)
                self.progress_bar.setValue(int(percent))
            except:
                self.progress_bar.setRange(0, 0)
        
    def installation_finished(self, success):
        if success:
            self.accept()
        else:
            self.reject()

class DownloadApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.i18n = I18n(self.config.language)
        self.history = DownloadHistory()
        
        self.setWindowTitle(self.i18n.get("app_title"))
        self.resize(800, 600)
        self.setWindowIcon(QIcon('ico.ico'))
        self.setFont(QFont("Segoe UI", 10))
        
        if not os.path.exists("temp_downloads"):
            os.makedirs("temp_downloads")
        self.downloads = {}   # {id: DownloadItem}
        self.threads = {}     # {id: DownloadThread}
        
        self.init_ui()
        self.setup_logging()
        self.apply_theme()  # Aplica o tema das configurações
        
        # Verifica e instala FFmpeg se necessário
        if not check_ffmpeg():
            dialog = FFmpegInstallDialog(self.i18n, self)
            if dialog.exec_() != QDialog.Accepted:
                QMessageBox.warning(self, self.i18n.get("warning"), self.i18n.get("error_ffmpeg"))

    def init_ui(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.init_downloads_tab()
        self.init_logs_tab()
        self.init_config_tab()

    def init_downloads_tab(self):
        downloads_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        header = QLabel(self.i18n.get("app_title"))
        header.setFont(QFont("Segoe UI", 20, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        form_layout = QFormLayout()
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText(self.i18n.get("video_url"))
        form_layout.addRow(self.i18n.get("video_url") + ":", self.url_edit)

        self.format_group = QButtonGroup()
        h_format = QHBoxLayout()
        self.radio_mp4 = QRadioButton(self.i18n.get("video_mp4"))
        self.radio_mp3 = QRadioButton(self.i18n.get("music_mp3"))
        self.radio_mp4.setChecked(True)
        self.format_group.addButton(self.radio_mp4)
        self.format_group.addButton(self.radio_mp3)
        h_format.addWidget(self.radio_mp4)
        h_format.addWidget(self.radio_mp3)
        form_layout.addRow(self.i18n.get("format") + ":", h_format)

        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems([
            self.i18n.get("best_quality"),
            "8K",
            "4K",
            "1080p",
            "720p",
            "360p"
        ])
        form_layout.addRow(self.i18n.get("resolution") + ":", self.resolution_combo)
        layout.addLayout(form_layout)

        self.radio_mp3.toggled.connect(self.toggle_resolution)

        self.add_button = QPushButton(self.i18n.get("add_to_queue"))
        self.add_button.setFixedHeight(45)
        layout.addWidget(self.add_button, alignment=Qt.AlignCenter)
        self.add_button.clicked.connect(self.add_download)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            self.i18n.get("title"),
            self.i18n.get("format"),
            self.i18n.get("resolution"),
            self.i18n.get("progress"),
            self.i18n.get("status"),
            self.i18n.get("added"),
            self.i18n.get("action")
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        header_table = self.table.horizontalHeader()
        header_table.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        action_layout = QHBoxLayout()
        self.btn_clear = QPushButton(self.i18n.get("clear_completed"))
        self.btn_retry = QPushButton(self.i18n.get("retry_download"))
        self.btn_remove = QPushButton(self.i18n.get("remove_selected"))
        self.btn_cancel = QPushButton(self.i18n.get("cancel_download"))
        for btn in [self.btn_clear, self.btn_retry, self.btn_remove, self.btn_cancel]:
            btn.setFixedHeight(40)
            action_layout.addWidget(btn)
        self.btn_clear.clicked.connect(self.clear_completed)
        self.btn_retry.clicked.connect(self.retry_download)
        self.btn_remove.clicked.connect(self.remove_selected)
        self.btn_cancel.clicked.connect(self.cancel_download)
        layout.addLayout(action_layout)

        downloads_widget.setLayout(layout)
        self.tabs.addTab(downloads_widget, self.i18n.get("downloads"))

    def init_logs_tab(self):
        logs_widget = QWidget()
        layout = QVBoxLayout()
        
        # Área de texto para logs
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        # Botões
        btn_layout = QHBoxLayout()
        self.btn_clear_logs = QPushButton(self.i18n.get("clear_logs"))
        self.btn_clear_logs.clicked.connect(lambda: self.log_text.clear())
        self.btn_export_log = QPushButton(self.i18n.get("export_log"))
        self.btn_export_log.clicked.connect(self.export_log)
        btn_layout.addWidget(self.btn_clear_logs)
        btn_layout.addWidget(self.btn_export_log)
        layout.addLayout(btn_layout)
        
        logs_widget.setLayout(layout)
        self.tabs.addTab(logs_widget, self.i18n.get("logs"))

    def init_config_tab(self):
        config_widget = QWidget()
        layout = QFormLayout()
        
        # Pasta de Download
        self.folder_edit = QLineEdit(self.config.download_path)
        self.folder_edit.setReadOnly(True)
        self.btn_change_folder = QPushButton(self.i18n.get("change_folder"))
        self.btn_change_folder.clicked.connect(self.change_folder)
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.folder_edit)
        h_layout.addWidget(self.btn_change_folder)
        layout.addRow(self.i18n.get("download_folder"), h_layout)
        
        # Tema
        self.theme_combo = QComboBox()
        dark_text = self.i18n.get("dark")
        light_text = self.i18n.get("light")
        self.theme_combo.addItems([dark_text, light_text])
        # Define o tema atual
        if self.config.theme == "Escuro":
            self.theme_combo.setCurrentText(dark_text)
        else:
            self.theme_combo.setCurrentText(light_text)
        self.theme_label = QLabel(self.i18n.get("theme"))
        layout.addRow(self.theme_label, self.theme_combo)
        
        # Idioma
        self.language_combo = QComboBox()
        for code, name in self.i18n.available_languages.items():
            self.language_combo.addItem(name, code)
        # Define o idioma atual
        index = self.language_combo.findData(self.config.language)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        self.language_label = QLabel(self.i18n.get("language"))
        layout.addRow(self.language_label, self.language_combo)
        
        # Botão Aplicar
        self.btn_apply = QPushButton(self.i18n.get("apply_settings"))
        self.btn_apply.clicked.connect(self.apply_config)
        layout.addRow(self.btn_apply)
        
        config_widget.setLayout(layout)
        self.tabs.addTab(config_widget, self.i18n.get("settings"))

    def toggle_resolution(self):
        if self.radio_mp3.isChecked():
            self.resolution_combo.setEnabled(False)
        else:
            self.resolution_combo.setEnabled(True)

    def open_config_dialog(self):
        dialog = ConfigDialog(self.i18n, self.config, self)
        if dialog.exec_() == QDialog.Accepted:
            settings = dialog.get_settings()
            self.config.download_path = settings["download_path"]
            self.config.theme = settings["theme"]
            self.config.language = settings["language"]
            
            self.i18n.set_language(self.config.language)
            self.apply_theme()
            self.retranslate_ui()
        
    def apply_theme(self):
        if self.config.theme == "Escuro":
            self.setStyleSheet(get_dark_theme())
        else:
            self.setStyleSheet(get_light_theme())

    def apply_config(self):
        # Salva o caminho de download
        self.config.download_path = self.folder_edit.text()
        
        # Atualiza o idioma primeiro
        new_language = self.language_combo.currentData()
        if new_language != self.config.language:
            self.config.language = new_language
            self.i18n.set_language(new_language)
            self.retranslate_ui()
        
        # Atualiza o tema
        theme_text = self.theme_combo.currentText()
        self.config.theme = "Escuro" if theme_text == self.i18n.get("dark") else "Claro"
        self.apply_theme()
        
        # Mostra mensagem de confirmação no idioma atualizado
        QMessageBox.information(
            self,
            self.i18n.get("information"),
            self.i18n.get("settings_saved")
        )

    def retranslate_ui(self):
        """Atualiza todos os textos da interface com o idioma atual"""
        # Título da janela e cabeçalho
        self.setWindowTitle(self.i18n.get("app_title"))
        
        # Tabs
        self.tabs.setTabText(0, self.i18n.get("downloads"))
        self.tabs.setTabText(1, self.i18n.get("logs"))
        self.tabs.setTabText(2, self.i18n.get("settings"))
        
        # Aba de Downloads
        header = self.findChild(QLabel)
        if header:
            header.setText(self.i18n.get("app_title"))
            
        self.url_edit.setPlaceholderText(self.i18n.get("video_url"))
        self.radio_mp4.setText(self.i18n.get("video_mp4"))
        self.radio_mp3.setText(self.i18n.get("music_mp3"))
        
        # ComboBox de resolução
        current_idx = self.resolution_combo.currentIndex()
        self.resolution_combo.clear()
        self.resolution_combo.addItems([
            self.i18n.get("best_quality"),
            "8K", "4K", "1080p", "720p", "360p"
        ])
        self.resolution_combo.setCurrentIndex(current_idx)
        
        # Botões principais
        self.add_button.setText(self.i18n.get("add_to_queue"))
        self.btn_clear.setText(self.i18n.get("clear_completed"))
        self.btn_retry.setText(self.i18n.get("retry_download"))
        self.btn_remove.setText(self.i18n.get("remove_selected"))
        self.btn_cancel.setText(self.i18n.get("cancel_download"))
        
        # Headers da tabela
        header_labels = [
            self.i18n.get("title"),
            self.i18n.get("format"),
            self.i18n.get("resolution"),
            self.i18n.get("progress"),
            self.i18n.get("status"),
            self.i18n.get("added"),
            self.i18n.get("action")
        ]
        self.table.setHorizontalHeaderLabels(header_labels)
        
        # Botões de ação na tabela
        for row in range(self.table.rowCount()):
            btn = self.table.cellWidget(row, 6)
            if isinstance(btn, QPushButton):
                btn.setText(self.i18n.get("open"))
        
        # Aba de Logs
        self.btn_clear_logs.setText(self.i18n.get("clear_logs"))
        self.btn_export_log.setText(self.i18n.get("export_log"))
        
        # Aba de Configurações
        self.btn_change_folder.setText(self.i18n.get("change_folder"))
        
        # ComboBox de tema
        current_theme = self.theme_combo.currentIndex()
        self.theme_combo.clear()
        self.theme_combo.addItems([self.i18n.get("dark"), self.i18n.get("light")])
        self.theme_combo.setCurrentIndex(current_theme)
        
        # Labels de configuração
        self.theme_label.setText(self.i18n.get("theme"))
        self.language_label.setText(self.i18n.get("language"))
        
        # Botão aplicar
        self.btn_apply.setText(self.i18n.get("apply_settings"))
        
        # Status na tabela
        for row in range(self.table.rowCount()):
            status_item = self.table.item(row, 4)
            if status_item:
                current_status = status_item.text()
                if current_status == "Queued":
                    status_item.setText(self.i18n.get("status_queued"))
                elif current_status == "Downloading":
                    status_item.setText(self.i18n.get("status_downloading"))
                elif current_status == "Processing":
                    status_item.setText(self.i18n.get("status_processing"))
                elif current_status == "Completed":
                    status_item.setText(self.i18n.get("status_completed"))
                elif current_status == "Cancelled":
                    status_item.setText(self.i18n.get("status_cancelled"))
                elif current_status.startswith("Error"):
                    status_item.setText(self.i18n.get("status_error"))

    def change_folder(self):
        folder = QFileDialog.getExistingDirectory(self, self.i18n.get("change_folder"), self.config.download_path)
        if folder:
            self.config.download_path = folder
            self.folder_edit.setText(folder)
            logging.info(f"Pasta de download alterada para: {folder}")

    def export_log(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            self.i18n.get("export_log"),
            "",
            "Text Files (*.txt)",
            options=options
        )
        if file_name:
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(self.log_text.toPlainText())
            QMessageBox.information(
                self,
                self.i18n.get("information"),
                self.i18n.get("log_exported")
            )

    def setup_logging(self):
        self.log_handler = LogHandler(self.log_text)
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
        self.log_handler.setFormatter(formatter)
        logging.getLogger().addHandler(self.log_handler)
        logging.getLogger().setLevel(logging.INFO)

    def add_download(self):
        url = self.url_edit.text().strip()
        if not url:
            QMessageBox.warning(self, self.i18n.get("warning"), self.i18n.get("error_no_url"))
            return
        fmt = "Vídeo - MP4" if self.radio_mp4.isChecked() else "Música - MP3"
        resolution = self.resolution_combo.currentText()
        if "instagram.com" in url.lower() and "/p/" in url.lower() and "/reel/" not in url.lower():
            url = url.replace("/p/", "/reel/")
            logging.info("Link de Instagram convertido para Reels.")
        item = DownloadItem(url, fmt, resolution)
        self.downloads[item.id] = item

        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(item.title))
        self.table.setItem(row, 1, QTableWidgetItem(item.format_choice))
        self.table.setItem(row, 2, QTableWidgetItem(item.resolution_choice))
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(0)
        progress_bar.setFormat("%p%")
        progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #41e535; }")
        self.table.setCellWidget(row, 3, progress_bar)
        self.table.setItem(row, 4, QTableWidgetItem(item.status))
        self.table.setItem(row, 5, QTableWidgetItem(item.added_at))
        btn_open = QPushButton(self.i18n.get("open"))
        btn_open.setEnabled(False)
        btn_open.clicked.connect(lambda _, id=item.id: self.open_file(id))
        self.table.setCellWidget(row, 6, btn_open)
        self.table.setRowHeight(row, 40)

        thread = DownloadThread(item, self.config.download_path)
        thread.progress_signal.connect(self.update_download)
        thread.finished_signal.connect(self.download_finished)
        self.threads[item.id] = thread
        thread.start()

        self.url_edit.clear()
        logging.info(f"Download adicionado: {url}")

    @pyqtSlot(str, float, str)
    def update_download(self, download_id: str, progress: float, status: str):
        item = self.downloads.get(download_id)
        if not item:
            return
        item.progress = progress
        item.status = status
        for row in range(self.table.rowCount()):
            cell = self.table.item(row, 5)
            if cell and cell.text() == item.added_at:
                self.table.setItem(row, 0, QTableWidgetItem(item.title))
                prog_widget = self.table.cellWidget(row, 3)
                if prog_widget:
                    if status == "Processando":
                        prog_widget.setValue(100)
                    else:
                        # Atualiza somente se o novo valor for maior para evitar "voltas"
                        if int(progress) > prog_widget.value():
                            prog_widget.setValue(int(progress))
                self.table.setItem(row, 4, QTableWidgetItem(item.status))
                btn_open = self.table.cellWidget(row, 6)
                if item.status == "Concluído":
                    btn_open.setEnabled(True)
                else:
                    btn_open.setEnabled(False)
                break

    @pyqtSlot(str)
    def download_finished(self, download_id: str):
        logging.info(f"Download finalizado: {download_id}")

    def open_file(self, download_id: str):
        item = self.downloads.get(download_id)
        if item and item.status == "Concluído" and os.path.exists(item.file_path):
            try:
                os.startfile(item.file_path)
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Não foi possível abrir o arquivo:\n{e}")
        else:
            QMessageBox.information(self, "Abrir", "Arquivo não disponível.")

    def clear_completed(self):
        remove_ids = [id for id, item in self.downloads.items() if item.status in ("Concluído", "Erro", "Cancelado") or item.status.startswith("Erro")]
        rows_to_remove = []
        for row in range(self.table.rowCount()):
            status_item = self.table.item(row, 4)
            if status_item and status_item.text() in ("Concluído", "Erro", "Cancelado"):
                rows_to_remove.append(row)
        for row in sorted(rows_to_remove, reverse=True):
            self.table.removeRow(row)
        for rid in remove_ids:
            if rid in self.downloads:
                del self.downloads[rid]
        logging.info("Downloads finalizados removidos.")

    def remove_selected(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.information(
                self,
                self.i18n.get("information"),
                self.i18n.get("select_to_remove")
            )
            return
        row = selected[0].row()
        added = self.table.item(row, 5).text()
        remove_id = None
        for id, item in self.downloads.items():
            if item.added_at == added:
                remove_id = id
                break
        if remove_id:
            del self.downloads[remove_id]
            self.table.removeRow(row)
            logging.info(f"Download removido: {remove_id}")

    def retry_download(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.information(
                self,
                self.i18n.get("information"),
                self.i18n.get("select_to_retry")
            )
            return
        row = selected[0].row()
        added = self.table.item(row, 5).text()
        for id, item in self.downloads.items():
            if item.added_at == added:
                if item.status.startswith("Erro"):
                    item.status = self.i18n.get("status_queued")
                    item.progress = 0.0
                    item.cancelled = False
                    thread = DownloadThread(item, self.config.download_path)
                    thread.progress_signal.connect(self.update_download)
                    thread.finished_signal.connect(self.download_finished)
                    self.threads[item.id] = thread
                    thread.start()
                    logging.info(f"Reiniciando download: {item.url}")
                else:
                    QMessageBox.information(
                        self,
                        self.i18n.get("information"),
                        self.i18n.get("error_retry")
                    )
                break

    def cancel_download(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.information(
                self,
                self.i18n.get("information"),
                self.i18n.get("select_to_cancel")
            )
            return
        row = selected[0].row()
        added = self.table.item(row, 5).text()
        for id, item in self.downloads.items():
            if item.added_at == added:
                item.cancelled = True
                item.status = self.i18n.get("status_cancelled")
                self.update_download(item.id, item.progress, item.status)
                logging.info(f"Download cancelado: {item.url}")
                break 