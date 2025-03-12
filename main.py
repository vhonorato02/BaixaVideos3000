import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from gui.main_window import DownloadApp
from utils.dependencies import YtDlpUpdater

def main():
    app = QApplication(sys.argv)

    # Atualiza o yt-dlpasdasdasdasdasd
    updater = YtDlpUpdater()
    updater.progress_signal.connect(lambda msg: print(msg))  # Ou conecte a um sinal de progresso na GUI
    updater.finished_signal.connect(lambda success: print("Atualização concluída" if success else "Atualização falhou"))
    updater.start()
    updater.wait()  # Espera a atualização terminar antes de continuar

    window = DownloadApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()