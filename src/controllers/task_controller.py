from typing import List, Optional
from sqlalchemy.orm import Session
from src.models.task import Task
from src.utils.exceptions import TaskNotFoundError, TaskValidationError, DatabaseError

class TaskController:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_task(self, title: str, category: str = "General") -> Task:
        if not title:
            raise TaskValidationError("Task title cannot be empty.")
        try:
            new_task = Task(title=title, category=category)
            self.db_session.add(new_task)
            self.db_session.commit()
            self.db_session.refresh(new_task)
            return new_task
        except Exception as e:
            self.db_session.rollback()
            raise DatabaseError(f"Error creating task: {e}")

    def get_task(self, task_id: int) -> Task:
        task = self.db_session.get(Task, task_id)
        if not task:
            raise TaskNotFoundError(f"Task with ID {task_id} not found.")
        return task

    def get_all_tasks(self) -> List[Task]:
        return self.db_session.query(Task).all()

    def update_task(self, task_id: int, **kwargs) -> Task:
        task = self.get_task(task_id)
        if "title" in kwargs and not kwargs["title"]:
            raise TaskValidationError("Task title cannot be empty.")
        try:
            for key, value in kwargs.items():
                setattr(task, key, value)
            self.db_session.commit()
            self.db_session.refresh(task)
            return task
        except Exception as e:
            self.db_session.rollback()
            raise DatabaseError(f"Error updating task: {e}")

    def delete_task(self, task_id: int) -> None:
        task = self.get_task(task_id)
        try:
            self.db_session.delete(task)
            self.db_session.commit()
        except Exception as e:
            self.db_session.rollback()
            raise DatabaseError(f"Error deleting task: {e}")

    def start_task_timer(self, task_id: int) -> Task:
        task = self.get_task(task_id)
        try:
            task.start_timer()
            self.db_session.commit()
            self.db_session.refresh(task)
            return task
        except Exception as e:
            self.db_session.rollback()
            raise DatabaseError(f"Error starting timer for task {task_id}: {e}")

    def stop_task_timer(self, task_id: int) -> Task:
        task = self.get_task(task_id)
        print(f"[TaskController.stop_task_timer] Before commit: started_at={task.started_at}")
        try:
            task.stop_timer()
            self.db_session.commit()
            self.db_session.refresh(task)
            print(f"[TaskController.stop_task_timer] After commit and refresh: started_at={task.started_at}")
            return task
        except Exception as e:
            self.db_session.rollback()
            raise DatabaseError(f"Error stopping timer for task {task_id}: {e}")

    def reset_task_timer(self, task_id: int) -> Task:
        task = self.get_task(task_id)
        try:
            task.reset_timer()
            self.db_session.commit()
            self.db_session.refresh(task)
            return task
        except Exception as e:
            self.db_session.rollback()
            raise DatabaseError(f"Error resetting timer for task {task_id}: {e}")

    def save_task_progress(self, task: Task) -> None:
        try:
            self.db_session.add(task)
            self.db_session.commit()
            self.db_session.refresh(task)
        except Exception as e:
            self.db_session.rollback()
            raise DatabaseError(f"Error saving task progress for task {task.id}: {e}")

    def get_tasks_by_category(self, category: str) -> List[Task]:
        return self.db_session.query(Task).filter_by(category=category).all()

    def get_running_task(self) -> Optional[Task]:
        return self.db_session.query(Task).filter(Task.started_at.isnot(None)).order_by(Task.started_at.desc()).first()