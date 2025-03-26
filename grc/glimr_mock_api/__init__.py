from flask import Blueprint, request, jsonify, current_app
from grc.utils.logger import LogLevel, Logger

glimr_mock_api = Blueprint('glimr_mock_api', __name__, url_prefix='/glimr/api/tdsapi')
logger = Logger()

@glimr_mock_api.route('/registernewcase', methods=['POST'])
def glimr_register_case_api():
    try:
        data = request.get_json()
        headers = request.headers

        required_headers = ['Content-Type', 'Accept', 'Authorization']
        missing_headers = [header for header in required_headers if header not in headers]

        if missing_headers:
            return jsonify({'error': 'The given header was not found.'}), 400

        if 'jurisdictionId' not in data:
            return jsonify({"error": "No JurisdictionID supplied"}), 401

        if 'onlineMappingCode' not in data:
            return jsonify({"error": "No OnlineMappingCode supplied"}), 402

        if 'contactFullName' not in data:
            return jsonify({"error": "No contact name supplied"}), 403

        if data['jurisdictionId'] != 2000000:
            return jsonify({"error": f"Active Jurisdiction not found for JurisdictionId {data['jurisdictionId']}"}), 411

        if data['onlineMappingCode'] != 'GRP_STANDARD':
            return jsonify({"error": "Online Mapping invalid or not found"}), 412

        response = {
          "jurisdictionId": 2000000,
          "tribunalCaseId": 12345,
          "tribunalCaseNumber": "GRS/2025/0001",
          "caseTitle": data['contactFullName'],
          "confirmationCode": None,
        }

        return jsonify(response), 200

    except Exception as e:
        logger.log(LogLevel.ERROR, str(e))
        return jsonify({'error': str(e)}), 400

@glimr_mock_api.route('/glimravailable', methods=['POST'])
def glimr_available_api():
    pass

@glimr_mock_api.before_request
def log_request_info():
    logger.log(LogLevel.INFO, f"Mock API request: {request.method} {request.url}")
    return None 