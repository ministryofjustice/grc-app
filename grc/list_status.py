import enum
from flask_babel import lazy_gettext as _l


class ListStatus(enum.Enum):
    COMPLETED = _l("Completed")
    IN_PROGRESS = _l("In progress")
    NOT_STARTED = _l("Not started")
    CANNOT_START_YET = _l("Cannot start yet")
    IN_REVIEW = _l("In review")  # Value 'in progress' is used only at task list
    ERROR = _l("Error")
