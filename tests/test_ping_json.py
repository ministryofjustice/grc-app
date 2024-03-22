import os
import requests
import time


def test_json_health_check(max_retries, timeout):
    max_retries = max_retries
    timeout = timeout

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(f"{os.environ['TEST_URL']}/health")
            response.raise_for_status()

            # Converting into accessible data
            public_data = response.json()

            # Public app assertions
            assert response.status_code == 200
            assert 'status' in public_data and public_data['status'] == 'success', 'Public app JSON status unsuccessful'
            assert public_data['results'][0]['passed'] is True, 'Public app JSON results has not passed'
            print('Public app JSON response is healthy')
            return

        except requests.RequestException as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt < max_retries:
                print(f"Retrying in {timeout} seconds...")
                time.sleep(timeout)

    print("Failed after maximum retries.")


