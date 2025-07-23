
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from src.models.task import Task

class TaskDialog(QDialog):
    def __init__(self, parent=None, task: Task = None):
        super().__init__(parent)
        self.task = task
        self.setup_ui()
        if task:
            self.populate_fields()

    def setup_ui(self):
        self.setWindowTitle("Nueva Tarea" if not self.task else "Editar Tarea")
        self.setModal(True)
        self.resize(400, 200)

        layout = QVBoxLayout()

        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Título:"))
        self.title_input = QLineEdit()
        title_layout.addWidget(self.title_input)
        layout.addLayout(title_layout)

        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Categoría:"))
        self.category_input = QLineEdit()
        self.category_input.setText("General")
        category_layout.addWidget(self.category_input)
        layout.addLayout(category_layout)

        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Aceptar")
        self.cancel_button = QPushButton("Cancelar")
        
        self.ok_button.clicked.connect(self.validate_and_accept)
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def populate_fields(self):
        if self.task:
            self.title_input.setText(self.task.title)
            self.category_input.setText(self.task.category)

    def validate_and_accept(self):
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Error de Validación", "El título de la tarea no puede estar vacío.")
            return

        category = self.category_input.text().strip()
        if not category:
            self.category_input.setText("General")

        self.accept()
