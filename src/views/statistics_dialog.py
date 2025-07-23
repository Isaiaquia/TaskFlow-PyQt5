
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models.task import Task

class StatisticsDialog(QDialog):
    def __init__(self, db_session: Session, parent=None):
        super().__init__(parent)
        self.db_session = db_session
        self.setWindowTitle("Estadísticas de Tareas")
        self.resize(600, 400)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.load_statistics()

    def load_statistics(self):
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        category_times = self.db_session.query(
            Task.category, func.sum(Task.time_spent)
        ).group_by(Task.category).all()

        if not category_times:
            self.layout.addWidget(QLabel("No hay datos de tareas para mostrar estadísticas."))
            return

        summary_label = QLabel("Tiempo total por categoría:")
        self.layout.addWidget(summary_label)
        for category, total_seconds in category_times:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            self.layout.addWidget(QLabel(f"  - {category}: {hours:02d}:{minutes:02d}:{seconds:02d}"))

        categories = [item[0] for item in category_times]
        times_in_hours = [item[1] / 3600]

        fig = Figure()
        ax = fig.add_subplot(111)
        ax.bar(categories, times_in_hours)
        ax.set_xlabel("Categoría")
        ax.set_ylabel("Tiempo (horas)")
        ax.set_title("Tiempo Total por Categoría")

        canvas = FigureCanvas(fig)
        self.layout.addWidget(canvas)
