from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QRadioButton, QTableWidget, QTableWidgetItem, QHeaderView, QButtonGroup, QCheckBox
from PyQt5.QtCore import Qt

class PlaylistDialog(QDialog):
    def __init__(self, i18n, videos, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.videos = videos
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.i18n.get("playlist_download"))
        self.resize(600, 400)

        layout = QVBoxLayout()

        self.audio_only_radio = QRadioButton(self.i18n.get("download_audio_only"))
        self.audio_only_radio.setChecked(True)
        self.video_radio = QRadioButton(self.i18n.get("download_video"))

        self.button_group = QButtonGroup()
        self.button_group.addButton(self.audio_only_radio)
        self.button_group.addButton(self.video_radio)

        layout.addWidget(self.audio_only_radio)
        layout.addWidget(self.video_radio)

        self.table = QTableWidget(len(self.videos), 2)
        self.table.setHorizontalHeaderLabels([self.i18n.get("title"), self.i18n.get("select")])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        header_table = self.table.horizontalHeader()
        header_table.setSectionResizeMode(QHeaderView.Stretch)

        for row, video in enumerate(self.videos):
            if 'title' not in video:
                continue  # Pula vídeos indisponíveis

            self.table.setItem(row, 0, QTableWidgetItem(video['title']))
            checkbox = QCheckBox()
            checkbox.setChecked(False) 
            self.table.setCellWidget(row, 1, checkbox)

        layout.addWidget(self.table)

        button_layout = QHBoxLayout()
        self.cancel_button = QPushButton(self.i18n.get("cancel"))
        self.download_all_button = QPushButton(self.i18n.get("download_all"))
        self.download_selected_button = QPushButton(self.i18n.get("download_selected"))

        self.cancel_button.clicked.connect(self.reject)
        self.download_all_button.clicked.connect(self.download_all)
        self.download_selected_button.clicked.connect(self.download_selected)

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.download_all_button)
        button_layout.addWidget(self.download_selected_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def download_all(self):
        self.accept()
        self.download_videos(all_videos=True)

    def download_selected(self):
        self.accept()
        self.download_videos(all_videos=False)

    def download_videos(self, all_videos):
        selected_videos = []
        for row in range(self.table.rowCount()):
            if all_videos or self.table.cellWidget(row, 1).isChecked():
                if 'url' in self.videos[row]:
                    selected_videos.append(self.videos[row])
        # Emitir sinal ou chamar função para iniciar o download dos vídeos selecionados
        self.parent().start_playlist_download(selected_videos, self.audio_only_radio.isChecked(), self.video_radio.isChecked())
