import os
import requests


def test_json_health_check():
    # Access health pages, currently does not work with admin app
    public_response = requests.get(f"{os.environ['TEST_URL']}/health")

    # Converting into accessible data
    public_data = public_response.json()

    # Public app assertions
    assert public_response.status_code == 200
    assert 'status' in public_data and public_data['status'] == 'success', 'Public app JSON status unsuccessful'
    assert public_data['results'][0]['passed'] is True, 'Public app JSON results has not passed'
    print('Public app JSON response is healthy')


