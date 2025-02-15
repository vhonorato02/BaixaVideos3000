from PyQt5.QtWidgets import (QDialog, QFormLayout, QLineEdit, QPushButton,
                             QHBoxLayout, QComboBox, QDialogButtonBox, QFileDialog, QCheckBox)

class ConfigDialog(QDialog):
    def __init__(self, i18n, config, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.config = config
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.i18n.get("settings"))
        self.resize(400, 300)

        layout = QFormLayout()

        self.download_folder_edit = QLineEdit(self.config.get("download_folder", ""))
        self.change_folder_button = QPushButton(self.i18n.get("change_folder"))
        self.change_folder_button.clicked.connect(self.change_folder)

        self.show_completion_message_checkbox = QCheckBox(self.i18n.get("show_completion_message"))
        self.show_completion_message_checkbox.setChecked(self.config.get("show_completion_message", True))

        layout.addRow(self.i18n.get("download_folder"), self.download_folder_edit)
        layout.addRow("", self.change_folder_button)
        layout.addRow(self.i18n.get("show_completion_message"), self.show_completion_message_checkbox)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout.addRow(self.button_box)

        self.setLayout(layout)

    def change_folder(self):
        folder = QFileDialog.getExistingDirectory(self, self.i18n.get("select_download_folder"))
        if folder:
            self.download_folder_edit.setText(folder)

    def accept(self):
        self.config["download_folder"] = self.download_folder_edit.text()
        self.config["show_completion_message"] = self.show_completion_message_checkbox.isChecked()
        self.config.save()
        super().accept()

    def get_settings(self):
        return {
            "download_folder": self.download_folder_edit.text(),
            "show_completion_message": self.show_completion_message_checkbox.isChecked()
        }