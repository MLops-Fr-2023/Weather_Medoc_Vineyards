import pytest
import datetime
from fastapi.testclient import TestClient
from main import app
from security import authent

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.text == '"Welcome to the Joffrey LEMERY, Nicolas CARAYON and Jacques DROUVROY weather API (for places around Margaux-Cantenac)"'
 
def test_login():
    test_user = 'admax'
    test_password = 'XXXXX'
    response = client.post("/token", data={"username": test_user, "password": test_password})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_read_users_me():

    #Authentificated_unused
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
    #Data for testing
    user_add = {
        'user_id': 'test_user',
        'pwd_hash': 'test_password',
        'firstname': 'test_firstname',
        'lastname': 'test_lastname',
        'user_email': 'test_email',
        'position': 'test_position',
        'active': 1
    }

    sub_1 = {"sub" : "admax"}
    sub_2 = {"sub" : "test"}


    #Authentificated_unused
    response = client.post("/add_user", params = user_add)
    assert response.status_code == 401

    # Assuming valid authentication token without user management permission
    expires_delta = datetime.timedelta(minutes=15)
    access_token = authent.create_access_token(data=sub_2, expires_delta=expires_delta)
    headers = {'accept': 'application/json', "Authorization": f"Bearer {access_token}"}
    response = client.post("/add_user", params = user_add, headers=headers)
    assert response.status_code == 403

    # Assuming valid authentication token with user management permission
    expires_delta = datetime.timedelta(minutes=15)
    access_token = authent.create_access_token(data=sub_1, expires_delta=expires_delta)
    headers = {'accept': 'application/json', "Authorization": f"Bearer {access_token}"}
    response = client.post("/add_user", params = user_add, headers=headers)
    assert response.status_code == 200

    # Assuming valid authentication token with user management permission but for an existing user_id
    expires_delta = datetime.timedelta(minutes=15)
    access_token = authent.create_access_token(data=sub_1, expires_delta=expires_delta)
    headers = {'accept': 'application/json', "Authorization": f"Bearer {access_token}"}
    response = client.post("/add_user", params = user_add, headers=headers)
    assert response.status_code == 400


def test_edit_user():
    #Data for testing
    user_edit = {
        'user_id': 'test_user',
        'pwd_hash': 'test_password_edit',
        'firstname': 'test_firstname_edit',
        'lastname': 'test_lastname_edit',
        'user_email': 'test_email_edit',
        'position': 'test_position_edit',
        'active': 1
    }

    user_edit_false = {
        'user_id': 'test_user_false',
        'pwd_hash': 'test_password_edit',
        'firstname': 'test_firstname_edit',
        'lastname': 'test_lastname_edit',
        'user_email': 'test_email_edit',
        'position': 'test_position_edit',
        'active': 1
    }

    user_edit_admax = {
        'user_id': 'admax',
        'pwd_hash': 'test_password_edit',
        'firstname': 'test_firstname_edit',
        'lastname': 'test_lastname_edit',
        'user_email': 'test_email_edit',
        'position': 'test_position_edit',
        'active': 1
    }

    sub_1 = {"sub" : "admax"}
    sub_2 = {"sub" : "test"}

    #Authentificated_unused
    response = client.post("/add_user", params = user_edit)
    assert response.status_code == 401

    # Assuming valid authentication token without user management permission
    expires_delta = datetime.timedelta(minutes=15)
    access_token = authent.create_access_token(data=sub_2, expires_delta=expires_delta)
    headers = {'accept': 'application/json', "Authorization": f"Bearer {access_token}"}
    response = client.post("/edit_user", params = user_edit, headers=headers)
    assert response.status_code == 403

    # Assuming valid authentication token with user management permission but to edit admax
    expires_delta = datetime.timedelta(minutes=15)
    access_token = authent.create_access_token(data=sub_1, expires_delta=expires_delta)
    headers = {'accept': 'application/json', "Authorization": f"Bearer {access_token}"}
    response = client.post("/edit_user", params = user_edit_admax, headers=headers)
    assert response.status_code == 403

    # Assuming valid authentication token with user management permission but for an non existing user_id
    expires_delta = datetime.timedelta(minutes=15)
    access_token = authent.create_access_token(data=sub_1, expires_delta=expires_delta)
    headers = {'accept': 'application/json', "Authorization": f"Bearer {access_token}"}
    response = client.post("/edit_user", params = user_edit_false, headers=headers)
    assert response.status_code == 400

    # Assuming valid authentication token with user management permission
    expires_delta = datetime.timedelta(minutes=15)
    access_token = authent.create_access_token(data=sub_1, expires_delta=expires_delta)
    headers = {'accept': 'application/json', "Authorization": f"Bearer {access_token}"}
    response = client.post("/edit_user", params = user_edit, headers=headers)
    assert response.status_code == 200



def test_delete_user():

    #Data for testing
    user_to_delete = {
        'user_id': 'test_user'
    }

    user_to_delete_admax = {
        'user_id': 'admax'
    }

    sub_1 = {"sub" : "admax"}
    sub_2 = {"sub" : "test"}

    #Authentificated_unused
    response = client.post("/delete_user", params = user_to_delete)
    assert response.status_code == 401

        # Assuming valid authentication token without user management permission
    expires_delta = datetime.timedelta(minutes=15)
    access_token = authent.create_access_token(data=sub_2, expires_delta=expires_delta)
    headers = {'accept': 'application/json', "Authorization": f"Bearer {access_token}"}
    response = client.post("/delete_user", params =  user_to_delete, headers=headers)
    assert response.status_code == 403

    # Assuming valid authentication token with user management permission but to delete admax
    expires_delta = datetime.timedelta(minutes=15)
    access_token = authent.create_access_token(data=sub_1, expires_delta=expires_delta)
    headers = {'accept': 'application/json', "Authorization": f"Bearer {access_token}"}
    response = client.post("/delete_user", params = user_to_delete_admax, headers=headers)
    assert response.status_code == 403

    # Assuming valid authentication token with user management permission
    expires_delta = datetime.timedelta(minutes=15)
    access_token = authent.create_access_token(data=sub_1, expires_delta=expires_delta)
    headers = {'accept': 'application/json', "Authorization": f"Bearer {access_token}"}
    response = client.post("/delete_user", params = user_to_delete, headers=headers)
    assert response.status_code == 200

    # Assuming valid authentication token with user management permission but for an non existing user_id
    expires_delta = datetime.timedelta(minutes=15)
    access_token = authent.create_access_token(data=sub_1, expires_delta=expires_delta)
    headers = {'accept': 'application/json', "Authorization": f"Bearer {access_token}"}
    response = client.post("/delete_user", params = user_to_delete, headers=headers)
    assert response.status_code == 400


def test_add_user_permission():

    #Data for testing
    user_permission = {
        'user_id': 'test',
        'permission_id' : 'get_data'
    }

    user_permission_admax = {
        'user_id': 'admax',
        'permission_id' : 'forecast'
    }

    user_permission_false_permission = {
        'user_id': 'test',
        'permission_id' : 'false'
    }

    user_permission_false_user = {
        'user_id': 'false',
        'permission_id' : 'forecast'
    }

    sub_1 = {"sub" : "admax"}
    sub_2 = {"sub" : "test"}

    #Authentificated_unused
    response = client.post("/add_user_permission", params = user_permission)
    assert response.status_code == 401


    # Assuming valid authentication token without user management permission
    expires_delta = datetime.timedelta(minutes=15)
    access_token = authent.create_access_token(data=sub_2, expires_delta=expires_delta)
    headers = {'accept': 'application/json', "Authorization": f"Bearer {access_token}"}
    response = client.post("/add_user_permission", params =  user_permission, headers=headers)
    assert response.status_code == 403

    # Assuming valid authentication token with user management permission but to delete admax
    expires_delta = datetime.timedelta(minutes=15)
    access_token = authent.create_access_token(data=sub_1, expires_delta=expires_delta)
    headers = {'accept': 'application/json', "Authorization": f"Bearer {access_token}"}
    response = client.post("/add_user_permission", params = user_permission_admax, headers=headers)
    assert response.status_code == 403

    # Assuming valid authentication token with user management permission but for an non existing user_id
    expires_delta = datetime.timedelta(minutes=15)
    access_token = authent.create_access_token(data=sub_1, expires_delta=expires_delta)
    headers = {'accept': 'application/json', "Authorization": f"Bearer {access_token}"}
    response = client.post("/add_user_permission", params = user_permission_false_user, headers=headers)
    assert response.status_code == 400

    # Assuming valid authentication token with user management permission but for an non existing permission_id
    expires_delta = datetime.timedelta(minutes=15)
    access_token = authent.create_access_token(data=sub_1, expires_delta=expires_delta)
    headers = {'accept': 'application/json', "Authorization": f"Bearer {access_token}"}
    response = client.post("/add_user_permission", params = user_permission_false_permission, headers=headers)
    assert response.status_code == 400

    # Assuming valid authentication token with user management permission
    expires_delta = datetime.timedelta(minutes=15)
    access_token = authent.create_access_token(data=sub_1, expires_delta=expires_delta)
    headers = {'accept': 'application/json', "Authorization": f"Bearer {access_token}"}
    response = client.post("/add_user_permission", params = user_permission, headers=headers)
    assert response.status_code == 200



def test_delete_user():

    #Data for testing
    user_to_delete = {
        'user_id': 'test_user'
    }

    user_to_delete_admax = {
        'user_id': 'admax'
    }

    sub_1 = {"sub" : "admax"}
    sub_2 = {"sub" : "test"}

    #Authentificated_unused
    response = client.post("/delete_user", params = user_to_delete)
    assert response.status_code == 401

        # Assuming valid authentication token without user management permission
    expires_delta = datetime.timedelta(minutes=15)
    access_token = authent.create_access_token(data=sub_2, expires_delta=expires_delta)
    headers = {'accept': 'application/json', "Authorization": f"Bearer {access_token}"}
    response = client.post("/delete_user", params =  user_to_delete, headers=headers)
    assert response.status_code == 403

    # Assuming valid authentication token with user management permission but to delete admax
    expires_delta = datetime.timedelta(minutes=15)
    access_token = authent.create_access_token(data=sub_1, expires_delta=expires_delta)
    headers = {'accept': 'application/json', "Authorization": f"Bearer {access_token}"}
    response = client.post("/delete_user", params = user_to_delete_admax, headers=headers)
    assert response.status_code == 403

    # Assuming valid authentication token with user management permission
    expires_delta = datetime.timedelta(minutes=15)
    access_token = authent.create_access_token(data=sub_1, expires_delta=expires_delta)
    headers = {'accept': 'application/json', "Authorization": f"Bearer {access_token}"}
    response = client.post("/delete_user", params = user_to_delete, headers=headers)
    assert response.status_code == 200

    # Assuming valid authentication token with user management permission but for an non existing user_id
    expires_delta = datetime.timedelta(minutes=15)
    access_token = authent.create_access_token(data=sub_1, expires_delta=expires_delta)
    headers = {'accept': 'application/json', "Authorization": f"Bearer {access_token}"}
    response = client.post("/delete_user", params = user_to_delete, headers=headers)
    assert response.status_code == 400


def test_delete_user_permission():

    #Data for testing
    user_permission = {
        'user_id': 'test',
        'permission_id' : 'get_data'
    }

    user_permission_admax = {
        'user_id': 'admax',
        'permission_id' : 'forecast'
    }

    user_permission_false_permission = {
        'user_id': 'test',
        'permission_id' : 'false'
    }

    user_permission_false_user = {
        'user_id': 'false',
        'permission_id' : 'forecast'
    }

    sub_1 = {"sub" : "admax"}
    sub_2 = {"sub" : "test"}

    #Authentificated_unused
    response = client.post("/delete_user_permission", params = user_permission)
    assert response.status_code == 401


    # Assuming valid authentication token without user management permission
    expires_delta = datetime.timedelta(minutes=15)
    access_token = authent.create_access_token(data=sub_2, expires_delta=expires_delta)
    headers = {'accept': 'application/json', "Authorization": f"Bearer {access_token}"}
    response = client.post("/delete_user_permission", params =  user_permission, headers=headers)
    assert response.status_code == 403

    # Assuming valid authentication token with user management permission but to delete admax
    expires_delta = datetime.timedelta(minutes=15)
    access_token = authent.create_access_token(data=sub_1, expires_delta=expires_delta)
    headers = {'accept': 'application/json', "Authorization": f"Bearer {access_token}"}
    response = client.post("/delete_user_permission", params = user_permission_admax, headers=headers)
    assert response.status_code == 403

    # Assuming valid authentication token with user management permission but for an non existing user_id
    expires_delta = datetime.timedelta(minutes=15)
    access_token = authent.create_access_token(data=sub_1, expires_delta=expires_delta)
    headers = {'accept': 'application/json', "Authorization": f"Bearer {access_token}"}
    response = client.post("/delete_user_permission", params = user_permission_false_user, headers=headers)
    assert response.status_code == 400

    # Assuming valid authentication token with user management permission but for an non existing permission_id
    expires_delta = datetime.timedelta(minutes=15)
    access_token = authent.create_access_token(data=sub_1, expires_delta=expires_delta)
    headers = {'accept': 'application/json', "Authorization": f"Bearer {access_token}"}
    response = client.post("/delete_user_permission", params = user_permission_false_permission, headers=headers)
    assert response.status_code == 400

    # Assuming valid authentication token with user management permission
    expires_delta = datetime.timedelta(minutes=15)
    access_token = authent.create_access_token(data=sub_1, expires_delta=expires_delta)
    headers = {'accept': 'application/json', "Authorization": f"Bearer {access_token}"}
    response = client.post("/delete_user_permission", params = user_permission, headers=headers)
    assert response.status_code == 200