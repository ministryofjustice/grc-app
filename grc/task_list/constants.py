from flask_babel import lazy_gettext as _l


class TaskListConstants:
    COMPLETED = _l("COMPLETED")
    IN_PROGRESS = _l("IN PROGRESS")
    NOT_STARTED = _l("NOT STARTED")
    CANNOT_START_YET = _l("CANNOT START YET")
    IN_REVIEW = _l("IN REVIEW")  # Value 'in progress' is used only at task list
    ERROR = _l("ERROR")
