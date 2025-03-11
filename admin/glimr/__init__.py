from flask import Blueprint, request, jsonify

from admin.glimr.glimr_new_case import GlimrNewCase
from grc.models import Application
from grc.utils.logger import LogLevel, Logger
import requests
from grc.models import db

glimr = Blueprint('glimr', __name__)
logger = Logger()

@glimr.route('/glimr/submit', methods=['POST'])
def submit_register_cases():
    data = request.get_json()
    reference_numbers = data['applications']

    if len(reference_numbers) <= 0:
        return jsonify({'error': 'No Cases Submitted'}), 404

    failed_cases = []
    processed_cases = []

    for reference_number in reference_numbers:
        try:
            application = get_application(reference_number)

            if application is None:
                failed_cases.append({'referenceNumber': reference_number, 'error': 'Application not found'})
                logger.log(LogLevel.ERROR, f'Application #{reference_number} not found.')

            else:
                glimr_case = GlimrNewCase(application).call_glimr_register_api()
                set_case_registered(application)
                save_glimr_case_details(glimr_case)
                processed_cases.append(reference_number)
                logger.log(LogLevel.INFO, f'Application #{reference_number} successfully registered to GLiMR.')

        except Exception as e:
            failed_cases.append({'referenceNumber': reference_number, 'error': f'Error: {str(e)}'})
            logger.log(LogLevel.ERROR, f"GLiMR API request failed with error {str(e)} for application #{reference_number}.")

    response_body = {
        'processedCases': processed_cases,
        'failedCases': failed_cases,
    }

    return jsonify(response_body), 200 if processed_cases else 400

def get_application(reference_number):
    application: Application = Application.query.filter_by(
        reference_number=reference_number
    ).first()

    if application is None:
        logger.log(LogLevel.ERROR, f"Application #{reference_number} cannot be found.")
        return None

    return application

def save_glimr_case_details(glimr_case: GlimrNewCase):
    logger.log(LogLevel.INFO, 'Case saved!')
    logger.log(LogLevel.INFO, f'Case reference UPDATED: {glimr_case.case_reference}')
    logger.log(LogLevel.INFO, f'Confirmation code UPDATED: {glimr_case.confirmation_code}')
    '''
        Implement saving to GLiMR code here
    '''

def set_case_registered(application: Application):
    try:
        application.case_registered = True
        db.session.commit()
        logger.log(LogLevel.INFO, f"Application marked as registered in database.")

    except Exception as e:
        logger.log(LogLevel.ERROR, f"Application failed to be marked as registered in database caused by: {str(e)}.")
        raise Exception(str(e))

