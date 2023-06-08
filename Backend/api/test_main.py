import pytest
import datetime
from fastapi.testclient import TestClient
from main import app
from security import authent

client = TestClient(app)


# def test_read_root():
#     response = client.get("/")
#     assert response.status_code == 200
#     assert response.text == '"Welcome to the Joffrey LEMERY, Nicolas CARAYON and Jacques DROUVROY weather API (for places around Margaux-Cantenac)"'


# def test_login():
#     test_user = 'admax'
#     test_password = 'XXXXX'
#     response = client.post("/token", data={"username": test_user, "password": test_password})
#     assert response.status_code == 200
#     assert "access_token" in response.json()
#     assert response.json()["token_type"] == "bearer"


def test_read_users_me():

    #Authentificated_used
    response = client.get("/users/me/")
    assert response.status_code == 401


    #Authentificated_used
    expires_delta = datetime.timedelta(minutes=15)
    data = {"sub" : "admax"}
    access_token = authent.create_access_token(data=data, expires_delta=expires_delta)
    headers = {'accept': 'application/json', "Authorization": f"Bearer {access_token}"}
    response = client.get("/users/me/", headers=headers)
    assert response.status_code == 200
    assert "user_id" in response.json()
    assert response.json()['user_id'] == 'admax'


def test_add_user():
    user_add = {'user_id': 'test_user', 'pwd_hash': 'test_password', 'firstname': 'test_firstname', 'lastname': 'test_lastname', 'user_email': 'test_email', 'position': 'test_position', 'active': int(1)}

    #Authentificated_used
    response = client.post("/add_user", json = user_add)
    assert response.status_code == 401

    # Assuming valid authentication token with user management permission
    expires_delta = datetime.timedelta(minutes=15)
    data = {"sub" : "admax"}
    access_token = authent.create_access_token(data=data, expires_delta=expires_delta)
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post("/add_user", json = user_add, headers=headers)
    assert response.status_code == 200
    assert "Message" in response.json()



