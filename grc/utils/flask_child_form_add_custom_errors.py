from flask_wtf import FlaskForm
from wtforms import FieldList
from grc.utils.logger import LogLevel, Logger

logger = Logger()

def add_error_for_child_form(parent_form_field_list: FieldList, child_form: FlaskForm, child_form_field_name: str, error_message: str):
    logger.log(LogLevel.ERROR, f"field_list.errors: {parent_form_field_list.errors}")
    setup_field_list_to_accept_custom_errors(parent_form_field_list)

    # Add the error to the child form
    child_form[child_form_field_name].errors.append(error_message)

    # Add the error to the parent form
    child_form_index = find_child_form_index(parent_form_field_list, child_form)
    errors_for_child_form = parent_form_field_list.errors[child_form_index]

    if child_form_field_name not in errors_for_child_form:
        errors_for_child_form[child_form_field_name] = []

    errors_for_child_form_field = errors_for_child_form[child_form_field_name]
    errors_for_child_form_field.append(error_message)
    logger.log(LogLevel.ERROR, f"field_list.errors: {parent_form_field_list.errors}")

def add_multiple_errors_for_child_form(parent_form_field_list: FieldList, child_form: FlaskForm,
                                       child_form_field_names_with_errors: {str: str}):
    print(f"field_list.errors: {parent_form_field_list.errors}", flush=True)
    setup_field_list_to_accept_custom_errors(parent_form_field_list)

    # Add the error to the child form
    for field_name, error_message in child_form_field_names_with_errors.items():
        child_form[field_name].errors.append(error_message)

    # Add the error to the parent form
    child_form_index = find_child_form_index(parent_form_field_list, child_form)
    errors_for_child_form = parent_form_field_list.errors[child_form_index]

    for field_name, error_message in child_form_field_names_with_errors.items():
        if field_name not in errors_for_child_form:
            errors_for_child_form[field_name] = []

        errors_for_child_form_field = errors_for_child_form[field_name]
        errors_for_child_form_field.append(error_message)
    print(f"field_list.errors: {parent_form_field_list.errors}", flush=True)


def setup_field_list_to_accept_custom_errors(field_list: FieldList):
    if not field_list.errors:
        # Add an empty error object for each child form
        field_list.errors = []
        number_of_child_forms_for_this_field = len(field_list)
        for i in range(number_of_child_forms_for_this_field):
            field_list.errors.append({})


def find_child_form_index(parent_form_field_list: FieldList, child_form: FlaskForm):
    child_form_index = 0
    for child_form_in_list in parent_form_field_list:
        if child_form_in_list == child_form:
            return child_form_index
        child_form_index = child_form_index + 1
    return -1
