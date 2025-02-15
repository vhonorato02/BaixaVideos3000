from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton
from PyQt5.QtCore import Qt

class PlaylistProgressDialog(QDialog):
    def __init__(self, i18n, total_items, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.total_items = total_items
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.i18n.get("playlist_download"))
        self.resize(400, 200)

        layout = QVBoxLayout()

        self.progress_label = QLabel(self.i18n.get("downloading_items").format(0, self.total_items))
        layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, self.total_items)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.skip_label = QLabel("")
        layout.addWidget(self.skip_label)

        self.cancel_button = QPushButton(self.i18n.get("cancel"))
        self.cancel_button.clicked.connect(self.reject)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

    def update_progress(self, current_item):
        self.progress_label.setText(self.i18n.get("downloading_items").format(current_item, self.total_items))
        self.progress_bar.setValue(current_item)

    def update_skip_message(self, skipped_items):
        self.skip_label.setText(self.i18n.get("skipping_unavailable_items").format(skipped_items))

    def disable_cancel_button(self):
        self.cancel_button.setEnabled(False)