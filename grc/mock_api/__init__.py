from flask import Blueprint, request, jsonify, current_app
from grc.utils.logger import LogLevel, Logger


mock_api = Blueprint('mock_api', __name__, url_prefix='/glimr/api')
logger = Logger()

@mock_api.route('/test', methods=['POST'])
def test_endpoint():
    return jsonify({'status': 'Mock API is working'}), 200

@mock_api.route('/tdsapi/registernewcase', methods=['POST'])
def register_new_case_test():
    try:
        data = request.get_json()
        logger.log(LogLevel.INFO, f"Recieved data in GLiMR API: {data}")

        response = {
          "jurisdictionId": 8,
          "tribunalCaseId": 12345678,
          "tribunalCaseNumber": "TC/2016/00006",
          "caseTitle": "John James vs HMRC",
          "confirmationCode": "DEF456"
        }

        return jsonify(response)

    except Exception as e:
        logger.log(LogLevel.ERROR, str(e))
        return jsonify({'error': str(e)})

@mock_api.before_request
def log_request_info():
    logger.log(LogLevel.INFO, f"Mock API request: {request.method} {request.url}")
    return None 