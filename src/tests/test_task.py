import pytest
from src.controllers.task_controller import TaskController
from src.utils.database import get_db_session, create_tables, engine, Base
from src.models.task import Task
import time

@pytest.fixture(scope="function")
def db_session():
    # Ensure a clean database for each test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = get_db_session()
    yield session
    session.close()

@pytest.fixture(scope="function")
def controller(db_session):
    return TaskController(db_session)

def test_create_task(controller):
    task = controller.create_task("Test Task", "Test Category")
    assert task.id is not None
    assert task.title == "Test Task"
    assert task.category == "Test Category"

def test_get_task(controller):
    created_task = controller.create_task("Get Task", "Category A")
    retrieved_task = controller.get_task(created_task.id)
    assert retrieved_task.title == "Get Task"

def test_update_task(controller):
    task = controller.create_task("Update Task", "Category B")
    updated_task = controller.update_task(task.id, title="Updated Title", status="Completed")
    assert updated_task.title == "Updated Title"
    assert updated_task.status == "Completed"

def test_delete_task(controller):
    task = controller.create_task("Delete Task", "Category C")
    controller.delete_task(task.id)
    with pytest.raises(Exception):
        controller.get_task(task.id)

def test_start_stop_timer(controller):
    task = controller.create_task("Timer Task", "Work")
    controller.start_task_timer(task.id)
    time.sleep(1)  # Simulate 1 second of work
    controller.stop_task_timer(task.id)
    updated_task = controller.get_task(task.id)
    assert updated_task.time_spent >= 1
    assert updated_task.is_running is False

def test_timer_regression(controller):
    task = controller.create_task("Regression Task", "Test")
    
    # Run 1
    controller.start_task_timer(task.id)
    time.sleep(1)
    controller.stop_task_timer(task.id)
    task = controller.get_task(task.id)
    initial_time = task.time_spent
    assert initial_time >= 1

    # Run 2
    controller.start_task_timer(task.id)
    time.sleep(1)
    controller.stop_task_timer(task.id)
    task = controller.get_task(task.id)
    second_time = task.time_spent
    assert second_time >= initial_time + 1

    # Run 3
    controller.start_task_timer(task.id)
    time.sleep(1)
    controller.stop_task_timer(task.id)
    task = controller.get_task(task.id)
    final_time = task.time_spent
    assert final_time >= second_time + 1

def test_get_running_task(controller):
    task1 = controller.create_task("Task 1", "Cat A")
    task2 = controller.create_task("Task 2", "Cat B")

    controller.start_task_timer(task1.id)
    running_task = controller.get_running_task()
    assert running_task.id == task1.id

    controller.stop_task_timer(task1.id)
    # No need for expire_all() here if db is clean for each test
    running_task = controller.get_running_task()
    assert running_task is None

    controller.start_task_timer(task2.id)
    running_task = controller.get_running_task()
    assert running_task.id == task2.id