import datetime
from fastapi.testclient import TestClient
from main import app
from security import authent


client = TestClient(app)

class HttpCodes():
    success = 200
    bad_request = 400
    not_authenticated = 401
    access_refused = 403
    

def get_authent_headers(user_id):
    sub = {"sub": user_id}
    expires_delta = datetime.timedelta(minutes=15)
    access_token = authent.create_access_token(data=sub, expires_delta=expires_delta)
    headers = {'accept': 'application/json', "Authorization": f"Bearer {access_token}"}
    return headers


def test_read_root():
    response = client.get("/")
    assert response.status_code == HttpCodes.success
    assert response.text == '"Welcome to the Joffrey LEMERY, Nicolas CARAYON and Jacques DROUVROY weather API (for places around Margaux-Cantenac)"'


def test_login():
    test_user = 'admax'
    test_password = 'XXXXX'
    response = client.post("/token", data={"username": test_user, "password": test_password})
    assert response.status_code == HttpCodes.success
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_read_users_me():

    # Not authenticated
    response = client.get("/users/me/")
    assert response.status_code == HttpCodes.not_authenticated

    # Authenticated
    expires_delta = datetime.timedelta(minutes=15)
    data = {"sub" : "admax"}
    access_token = authent.create_access_token(data=data, expires_delta=expires_delta)
    headers = {'accept': 'application/json', "Authorization": f"Bearer {access_token}"}

    response = client.get("/users/me/", headers=headers)
    assert response.status_code == HttpCodes.success
    assert "user_id" in response.json()
    assert response.json()['user_id'] == 'admax'


def test_add_user():
    # Data for testing
    user_add = {
        'user_id': 'test_user',
        'pwd_hash': 'test_password',
        'firstname': 'test_firstname',
        'lastname': 'test_lastname',
        'user_email': 'test_email',
        'position': 'test_position',
        'active': 1
    }

    # Not authenticated
    response = client.post("/add_user", params = user_add)
    assert response.status_code == HttpCodes.not_authenticated

    # Authenticated without permission
    headers = get_authent_headers("test")
    response = client.post("/add_user", params = user_add, headers=headers)
    assert response.status_code == HttpCodes.access_refused

    # Authenticated with permission
    headers = get_authent_headers("admax")
    response = client.post("/add_user", params = user_add, headers=headers)
    assert response.status_code == HttpCodes.success

    # Authenticated with permission trying to add an already existing user_id
    response = client.post("/add_user", params = user_add, headers=headers)
    assert response.status_code == HttpCodes.bad_request


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

    # Not authentificated
    response = client.post("/add_user", params=user_edit)
    assert response.status_code == HttpCodes.not_authenticated

    # Authenticated without permission
    headers = get_authent_headers("test")
    response = client.post("/edit_user", params=user_edit, headers=headers)
    assert response.status_code == HttpCodes.access_refused

    # Authenticated with permission trying to edit non editable user "admax"
    headers = get_authent_headers("admax")
    response = client.post("/edit_user", params=user_edit_admax, headers=headers)
    assert response.status_code == HttpCodes.access_refused

    # Authenticated with permission trying to edit non existing user
    response = client.post("/edit_user", params=user_edit_false, headers=headers)
    assert response.status_code == HttpCodes.bad_request

    # Authenticated with permission editing existing user
    response = client.post("/edit_user", params=user_edit, headers=headers)
    assert response.status_code == HttpCodes.success


def test_delete_user():

    #Data for testing
    user_to_delete = {
        'user_id': 'test_user'
    }

    user_to_delete_admax = {
        'user_id': 'admax'
    }

    # Not authenticated
    response = client.post("/delete_user", params=user_to_delete)
    assert response.status_code == HttpCodes.not_authenticated

    # Authenticated without permission
    headers = get_authent_headers("test")
    response = client.post("/delete_user", params=user_to_delete, headers=headers)
    assert response.status_code == HttpCodes.access_refused

    # Authenticated with permission trying to delete non editable user "admax"
    headers = get_authent_headers("admax")
    response = client.post("/delete_user", params=user_to_delete_admax, headers=headers)
    assert response.status_code == HttpCodes.access_refused

    # Authenticated with permission deleting existing user
    response = client.post("/delete_user", params=user_to_delete, headers=headers)
    assert response.status_code == HttpCodes.success

    # Authenticated with permission trying to delete non existing user    
    response = client.post("/delete_user", params=user_to_delete, headers=headers)
    assert response.status_code == HttpCodes.bad_request


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

    # Not authenticated
    response = client.post("/add_user_permission", params=user_permission)
    assert response.status_code == HttpCodes.not_authenticated

    # Authenticated without permission    
    headers = get_authent_headers("test")
    response = client.post("/add_user_permission", params=user_permission, headers=headers)
    assert response.status_code == HttpCodes.access_refused

    # Authenticated with permission trying to delete permission to non editable user "admax"
    headers = get_authent_headers("admax")
    response = client.post("/add_user_permission", params=user_permission_admax, headers=headers)
    assert response.status_code == HttpCodes.access_refused

    # Authenticated with permission trying to delete permission to a non existing user_id    
    response = client.post("/add_user_permission", params=user_permission_false_user, headers=headers)
    assert response.status_code == HttpCodes.bad_request

    # Authenticated with permission trying to delete a non existing permission_id    
    response = client.post("/add_user_permission", params=user_permission_false_permission, headers=headers)
    assert response.status_code == HttpCodes.bad_request

    # Authenticated with permission    
    response = client.post("/add_user_permission", params=user_permission, headers=headers)
    assert response.status_code == HttpCodes.success


def test_delete_user():

    # Data for testing
    user_to_delete = {
        'user_id': 'test_user'
    }

    user_to_delete_admax = {
        'user_id': 'admax'
    }

    # Not authenticated
    response = client.post("/delete_user", params=user_to_delete)
    assert response.status_code == HttpCodes.not_authenticated

    # Authenticated without permission
    headers = get_authent_headers("test")
    response = client.post("/delete_user", params=user_to_delete, headers=headers)
    assert response.status_code == HttpCodes.access_refused

    # Authenticated with permission trying to delete non editable user "admax"
    headers = get_authent_headers("admax")
    response = client.post("/delete_user", params=user_to_delete_admax, headers=headers)
    assert response.status_code == HttpCodes.access_refused

    # Authenticated with permission deleting existing user   
    response = client.post("/delete_user", params=user_to_delete, headers=headers)
    assert response.status_code == HttpCodes.success

    # Authenticated with permission trying to delete non existing user
    headers = get_authent_headers("admax")
    response = client.post("/delete_user", params=user_to_delete, headers=headers)
    assert response.status_code == HttpCodes.bad_request


def test_delete_user_permission():

    # Data for testing
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

    # Not authenticated
    response = client.post("/delete_user_permission", params = user_permission)
    assert response.status_code == HttpCodes.not_authenticated

    # Authenticated without permission
    headers = get_authent_headers("test")
    response = client.post("/delete_user_permission", params =  user_permission, headers=headers)
    assert response.status_code == HttpCodes.access_refused

    # Authenticated with permission trying to delete permission to non editable user_id "admax"
    headers = get_authent_headers("admax")
    response = client.post("/delete_user_permission", params = user_permission_admax, headers=headers)
    assert response.status_code == HttpCodes.access_refused

    # Authenticated with permission trying to delete permission to a non existing user_id    
    response = client.post("/delete_user_permission", params = user_permission_false_user, headers=headers)
    assert response.status_code == HttpCodes.bad_request

    # Authenticated with permission trying to delete non existing permission_id to user_id
    response = client.post("/delete_user_permission", params = user_permission_false_permission, headers=headers)
    assert response.status_code == HttpCodes.bad_request

    # Authenticated with permission delete existing permission_id to existing user_id   
    response = client.post("/delete_user_permission", params = user_permission, headers=headers)
    assert response.status_code == HttpCodes.success