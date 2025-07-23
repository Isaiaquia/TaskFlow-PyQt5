import os
import csv
from PyQt5.QtWidgets import QMainWindow, QListWidgetItem, QMessageBox, QFileDialog
from PyQt5.uic import loadUi
from PyQt5.QtCore import QTimer
from plyer import notification

from src.controllers.task_controller import TaskController
from src.utils.database import get_db_session
from src.models.task import Task
from src.views.task_dialog import TaskDialog
from src.views.statistics_dialog import StatisticsDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        ui_path = os.path.join(os.path.dirname(__file__), "..", "ui", "main_window.ui")
        loadUi(ui_path, self)

        self.db_session = get_db_session()
        self.task_controller = TaskController(self.db_session)
        self.current_task: Task | None = None

        self.setup_ui()
        self.load_tasks()
        self.setup_timer()

    def setup_ui(self):
        self.setWindowTitle("TaskFlow - Gestor de Tareas")
        self.add_task_button.clicked.connect(self.add_task)
        self.edit_task_button.clicked.connect(self.edit_selected_task)
        self.delete_task_button.clicked.connect(self.delete_selected_task)
        self.toggle_timer_button.clicked.connect(self.toggle_timer)
        self.task_list_widget.itemSelectionChanged.connect(self.update_button_states)
        self.category_filter_combobox.currentIndexChanged.connect(self.filter_tasks)
        self.action_estadisticas.triggered.connect(self.show_statistics)
        self.action_exportar.triggered.connect(self.export_tasks_to_csv)

        self.update_button_states()
        self.populate_categories()

    def populate_categories(self):
        self.category_filter_combobox.clear()
        self.category_filter_combobox.addItem("Todas")
        categories = sorted(list(set([task.category for task in self.task_controller.get_all_tasks()])))
        self.category_filter_combobox.addItems(categories)

    def load_tasks(self, category: str = "Todas"):
        self.task_list_widget.clear()
        if category == "Todas":
            tasks = self.task_controller.get_all_tasks()
        else:
            tasks = self.task_controller.get_tasks_by_category(category)

        for task in tasks:
            item = QListWidgetItem(f"{task.title} ({task.category}) - {task.status} - {task.time_spent_human}")
            item.setData(1, task.id)
            self.task_list_widget.addItem(item)

        self.update_button_states()

    def filter_tasks(self):
        selected_category = self.category_filter_combobox.currentText()
        self.load_tasks(selected_category)

    def add_task(self):
        dialog = TaskDialog(self)
        if dialog.exec_():
            title = dialog.title_input.text()
            category = dialog.category_input.text()
            try:
                self.task_controller.create_task(title, category)
                self.load_tasks()
                self.populate_categories()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def edit_selected_task(self):
        selected_item = self.task_list_widget.currentItem()
        if selected_item:
            task_id = selected_item.data(1)
            task = self.task_controller.get_task(task_id)
            dialog = TaskDialog(self, task)
            if dialog.exec_():
                title = dialog.title_input.text()
                category = dialog.category_input.text()
                try:
                    self.task_controller.update_task(task_id, title=title, category=category)
                    self.load_tasks()
                    self.populate_categories()
                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))

    def delete_selected_task(self):
        selected_item = self.task_list_widget.currentItem()
        if selected_item:
            task_id = selected_item.data(1)
            reply = QMessageBox.question(self, "Eliminar Tarea",
                                         "¿Estás seguro de que quieres eliminar esta tarea?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    self.task_controller.delete_task(task_id)
                    self.load_tasks()
                    self.populate_categories()
                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))

    def toggle_timer(self):
        selected_item = self.task_list_widget.currentItem()
        if selected_item:
            task_id = selected_item.data(1)
            task = self.task_controller.get_task(task_id)

            if task.is_running:
                self.task_controller.stop_task_timer(task_id)
                self.current_task = None
            else:
                if self.current_task and self.current_task.is_running:
                    self.task_controller.stop_task_timer(self.current_task.id)

                self.task_controller.start_task_timer(task_id)
                self.current_task = task

            self.load_tasks()
            self.update_button_states()

    def setup_timer(self):
        self.ui_timer = QTimer(self)
        self.ui_timer.setInterval(1000)
        self.ui_timer.timeout.connect(self.update_timer_display)
        self.ui_timer.start()

        running_task = self.task_controller.get_running_task()
        if running_task:
            self.current_task = running_task
            self.update_timer_display()

    def update_timer_display(self):
        if self.current_task and self.current_task.is_running:
            self.status_bar.showMessage(f"Tarea activa: {self.current_task.title} - {self.current_task.time_spent_human}")
            if self.current_task.get_current_session_time() % 5 == 0:
                self.task_controller.save_task_progress(self.current_task)
            
            if self.current_task.get_current_session_time() > 0 and self.current_task.get_current_session_time() % (25 * 60) == 0:
                notification.notify(
                    title='TaskFlow - ¡Descanso Pomodoro!',
                    message=f'¡Has trabajado en "{self.current_task.title}" por 25 minutos! Tómate un descanso.',
                    app_name='TaskFlow',
                    timeout=10
                )
        else:
            self.status_bar.showMessage("No hay tarea activa.")
            self.toggle_timer_button.setText("Iniciar Temporizador")

    def update_button_states(self):
        has_selection = self.task_list_widget.currentItem() is not None
        self.edit_task_button.setEnabled(has_selection)
        self.delete_task_button.setEnabled(has_selection)
        self.toggle_timer_button.setEnabled(has_selection)

        if has_selection:
            selected_item = self.task_list_widget.currentItem()
            task_id = selected_item.data(1)
            task = self.task_controller.get_task(task_id)
            if task.is_running:
                self.toggle_timer_button.setText("Detener Temporizador")
            else:
                self.toggle_timer_button.setText("Iniciar Temporizador")
        else:
            self.toggle_timer_button.setText("Iniciar Temporizador")

    def show_statistics(self):
        dialog = StatisticsDialog(self.db_session, self)
        dialog.exec_()

    def export_tasks_to_csv(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Exportar Tareas a CSV", "",
                                                   "CSV Files (*.csv);;All Files (*)", options=options)
        if file_name:
            try:
                tasks = self.task_controller.get_all_tasks()
                with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['ID', 'Título', 'Categoría', 'Estado', 'Tiempo Empleado (segundos)', 'Tiempo Empleado (HH:MM:SS)', 'Iniciada En', 'Creada En', 'Actualizada En']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    writer.writeheader()
                    for task in tasks:
                        writer.writerow({
                            'ID': task.id,
                            'Título': task.title,
                            'Categoría': task.category,
                            'Estado': task.status,
                            'Tiempo Empleado (segundos)': task.time_spent,
                            'Tiempo Empleado (HH:MM:SS)': task.time_spent_human,
                            'Iniciada En': task.started_at.isoformat() if task.started_at else '',
                            'Creada En': task.created_at.isoformat() if task.created_at else '',
                            'Actualizada En': task.updated_at.isoformat() if task.updated_at else ''
                        })
                QMessageBox.information(self, "Exportación Exitosa", "Tareas exportadas a CSV correctamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error de Exportación", f"Error al exportar tareas: {e}")

    def closeEvent(self, event):
        if self.current_task and self.current_task.is_running:
            self.task_controller.save_task_progress(self.current_task)
        self.db_session.close()
        event.accept()