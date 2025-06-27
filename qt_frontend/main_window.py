from PyQt6 import QtWidgets
from core.scanner import EVENT_BUS
import asyncio
import logging
from external_api import shodan_lookup, wigle_lookup

logger = logging.getLogger(__name__)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BLE Scanner")
        self.text = QtWidgets.QTextEdit()
        self.setCentralWidget(self.text)
        self._setup_menu()
        asyncio.create_task(self.update_loop())

    def _setup_menu(self) -> None:
        menu = self.menuBar().addMenu("Tools")
        shodan_action = menu.addAction("Shodan Lookup")
        shodan_action.triggered.connect(
            lambda: asyncio.create_task(self.lookup_shodan())
        )
        wigle_action = menu.addAction("Wigle Lookup")
        wigle_action.triggered.connect(lambda: asyncio.create_task(self.lookup_wigle()))

    async def update_loop(self):
        while True:
            event = await EVENT_BUS.get()
            self.text.append(str(event))

    async def lookup_shodan(self) -> None:
        query, ok = QtWidgets.QInputDialog.getText(self, "Shodan Query", "Query:")
        if ok:
            res = await asyncio.to_thread(shodan_lookup, query)
            self.text.append(str(res))

    async def lookup_wigle(self) -> None:
        ssid, ok = QtWidgets.QInputDialog.getText(self, "WiGLE SSID", "SSID:")
        if ok:
            res = await asyncio.to_thread(wigle_lookup, ssid)
            self.text.append(str(res))


def run():
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
