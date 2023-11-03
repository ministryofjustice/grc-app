import requests


def test_json_health_check():
    # Access health pages
    public_response = requests.get("http://localhost:3000/health")
    admin_response = requests.get("http://localhost:3001/health")

    # Converting into accessible data
    public_data = public_response.json()
    admin_data = admin_response.json()

    # Public app assertions
    assert public_response.status_code == 200
    assert 'status' in public_data and public_data['status'] == 'success', 'Public app JSON status unsuccessful'
    assert public_data['results'][0]['passed'] is True, 'Public app JSON results has not passed'
    print('Public app JSON response is healthy')

    # Admin app assertions
    assert admin_response.status_code == 200
    assert 'status' in admin_data and admin_data['status'] == 'success', 'Admin app JSON status unsuccessful'
    assert admin_data['results'][0]['passed'] is True, 'Admin app JSON results has not passed'
    print('Admin app JSON response is healthy')

    # Log for public app
    if public_response.status_code == 200:
        if 'status' in public_data and public_data['status'] == 'success':
            if public_data['results'][0]['passed'] is True:
                print("Public app JSON response is healthy")
        else:
            print("Error - could not access health page, public app JSON response is not healthy")
            print(f"Public app HTTP request failed with status code: {public_response.status_code}")

    # Log for admin app
    if admin_response.status_code == 200:
        if 'status' in admin_data and admin_data['status'] == 'success':
            if admin_data['results'][0]['passed'] is True:
                print("Admin app JSON response is healthy")
        else:
            print("Error - could not access health page, admin app JSON response is not healthy")
            print(f"Admin app HTTP request failed with status code: {public_response.status_code}")


test_json_health_check()
