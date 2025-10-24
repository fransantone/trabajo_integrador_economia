import sys
from PySide6.QtWidgets import QApplication
from controller_demanda import DemandController

def main():
    app = QApplication(sys.argv)
    controller = DemandController()
    controller.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
