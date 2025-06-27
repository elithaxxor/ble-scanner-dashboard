from PyQt6 import QtWidgets
from core.scanner import EVENT_BUS
import asyncio
import logging

logger = logging.getLogger(__name__)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BLE Scanner")
        self.text = QtWidgets.QTextEdit()
        self.setCentralWidget(self.text)
        asyncio.create_task(self.update_loop())

    async def update_loop(self):
        while True:
            event = await EVENT_BUS.get()
            self.text.append(str(event))


def run():
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
