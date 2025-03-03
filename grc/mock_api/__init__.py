from flask import Blueprint, request, jsonify, current_app
import logging

mock_api = Blueprint('mock_api', __name__, url_prefix='/glimr/api')
logger = logging.getLogger(__name__)

@mock_api.route('/test', methods=['GET'])
def test_endpoint():
    return jsonify({'status': 'Mock API is working'}), 200

@mock_api.route('/tdsapi/registernewcase', methods=['POST'])
def register_new_case():
    logger.info("Received request to register new case")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request headers: {request.headers}")
    logger.info(f"Request URL: {request.url}")
    try:
        data = request.get_json()
        logger.info(f"Received request data: {data}")

        # Validate required fields
        required_fields = ['jurisdictionId', 'onlineMappingCode', 'contactFirstName', 'contactLastName']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Mock response
        response = {
            'jurisdictionId': data.get('jurisdictionId'),
            'tribunalCaseId': 66476,  # Mock ID
            'tribunalCaseNumber': 'TC/2024/00312',  # Mock number
            'caseTitle': f"{data.get('contactFirstName')} {data.get('contactLastName')}",
            'confirmationCode': None
        }

        logger.info(f"Sending response: {response}")
        return jsonify(response)

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({'error': str(e)}), 500

@mock_api.before_request
def log_request_info():
    logger.info(f"Mock API request: {request.method} {request.url}")
    return None 