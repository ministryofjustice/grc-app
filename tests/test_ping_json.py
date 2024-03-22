import os
import requests
import time


def pytest_addoption(parser):
    parser.addoption("--max-retries", type=int, default=1, help="Add number of attempts to ping endpoint")
    parser.addoption("--timeout", type=int, default=3, help="Timeout in seconds between each ping")


def test_json_health_check(request):
    max_retries = request.config.getoption("--max-retries")
    timeout = request.config.getoption("--timeout")

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


