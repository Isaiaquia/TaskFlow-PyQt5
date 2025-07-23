
import sys
import os
from PyQt5.QtWidgets import QApplication
import qdarkstyle

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.views.main_window import MainWindow
from src.utils.database import create_tables

def main():
    create_tables()
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
