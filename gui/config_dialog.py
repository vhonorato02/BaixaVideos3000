from PyQt5.QtWidgets import (QDialog, QFormLayout, QLineEdit, QPushButton,
                             QHBoxLayout, QComboBox, QDialogButtonBox, QFileDialog)

class ConfigDialog(QDialog):
    def __init__(self, i18n, config, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.config = config
        
        self.setWindowTitle(self.i18n.get("settings"))
        self.setModal(True)
        self.resize(400, 200)
        
        layout = QFormLayout()
        
        # Pasta de Download
        self.folder_edit = QLineEdit(self.config.download_path)
        self.folder_edit.setReadOnly(True)
        btn_change = QPushButton(self.i18n.get("change_folder"))
        btn_change.clicked.connect(self.change_folder)
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.folder_edit)
        h_layout.addWidget(btn_change)
        layout.addRow(self.i18n.get("download_folder"), h_layout)
        
        # Tema
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([self.i18n.get("dark"), self.i18n.get("light")])
        self.theme_combo.setCurrentText(self.i18n.get(self.config.theme.lower()))
        layout.addRow(self.i18n.get("theme"), self.theme_combo)
        
        # Idioma
        self.language_combo = QComboBox()
        for code, name in self.i18n.available_languages.items():
            self.language_combo.addItem(name, code)
        index = self.language_combo.findData(self.config.language)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        layout.addRow(self.i18n.get("language"), self.language_combo)
        
        # Botões OK/Cancelar
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        layout.addRow(self.buttonBox)
        
        self.setLayout(layout)

    def change_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            self.i18n.get("change_folder"),
            self.folder_edit.text()
        )
        if folder:
            self.folder_edit.setText(folder)

    def get_settings(self):
        return {
            "download_path": self.folder_edit.text(),
            "theme": "Escuro" if self.theme_combo.currentText() == self.i18n.get("dark") else "Claro",
            "language": self.language_combo.currentData()
        } 