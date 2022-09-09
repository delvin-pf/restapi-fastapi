from client import client


def test_main_app():
	response = client.get('/')
	assert response.status_code == 200
	assert response.json() == {
		"name": "RestApi with FastApi in Python",
		"description": "RestApi example to shop",
		"version": "v1",
		"developed_by": "Delvin Pérez"
	}
