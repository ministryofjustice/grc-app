import enum
from grc.task_list.constants import TaskListConstants as c


class ListStatus(enum.Enum):
    COMPLETED = c.COMPLETED
    IN_PROGRESS = c.IN_PROGRESS
    NOT_STARTED = c.NOT_STARTED
    CANNOT_START_YET = c.CANNOT_START_YET
    IN_REVIEW = c.IN_REVIEW  # Value 'in progress' is used only at task list
    ERROR = c.ERROR
