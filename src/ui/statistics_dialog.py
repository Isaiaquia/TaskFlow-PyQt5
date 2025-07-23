
from PyQt5.QtWidgets import QDialog, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class StatisticsDialog(QDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Estadísticas")
        self.layout = QVBoxLayout(self)
        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.layout.addWidget(self.canvas)
        self.plot(data)

    def plot(self, data):
        ax = self.canvas.figure.subplots()
        categories = list(data.keys())
        times = list(data.values())
        ax.bar(categories, times)
        ax.set_ylabel("Tiempo (segundos)")
        ax.set_title("Tiempo por Categoría")
