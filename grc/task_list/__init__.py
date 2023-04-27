from flask import Blueprint, render_template
from grc.business_logic.data_store import DataStore
from grc.utils.decorators import LoginRequired
from grc.utils.application_progress import calculate_progress_status_colour
from grc.list_status import ListStatus

taskList = Blueprint('taskList', __name__)


@taskList.route('/task-list', methods=['GET'])
@LoginRequired
def index():
    application_data = DataStore.load_application_by_session_reference_number()
    print("".join(f'{i.aws_file_name}, {i.original_file_name}, {i.password_required}' for i in
                  application_data.uploads_data.birth_or_adoption_certificates), flush=True)
    return render_template(
        'task-list.html',
        application_data=application_data,
        get_colour=calculate_progress_status_colour,
        ListStatus=ListStatus
    )
