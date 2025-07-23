
class TaskFlowError(Exception):
    pass

class TaskNotFoundError(TaskFlowError):
    pass

class TaskValidationError(TaskFlowError):
    pass

class DatabaseError(TaskFlowError):
    pass
