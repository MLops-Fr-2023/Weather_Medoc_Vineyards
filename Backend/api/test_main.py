from datetime import timedelta
from fastapi.testclient import TestClient
from main import app
from security import authent
import pytest



class HttpCodes():
    success = 200
    bad_request = 400
    not_authenticated = 401
    access_refused = 403


######### FIXTURES #######

@pytest.fixture
def api_client():
    return TestClient(app)


@pytest.fixture
def access_token_test():
    user_id = 'test'
    data = {"sub": user_id}
    expires_delta = timedelta(minutes=15)
    access_token = authent.create_access_token(data=data, expires_delta=expires_delta)
    return access_token

@pytest.fixture
def access_token_admax():
    user_id = 'admax'
    data = {"sub": user_id}
    expires_delta = timedelta(minutes=15)
    access_token = authent.create_access_token(data=data, expires_delta=expires_delta)
    return access_token

@pytest.fixture
def access_token_external_client():
    user_id = 'external_client'
    data = {"sub": user_id}
    expires_delta = timedelta(minutes=15)
    access_token = authent.create_access_token(data=data, expires_delta=expires_delta)
    return access_token

@pytest.fixture
def auth_headers_test(access_token_test):
    return {'accept': 'application/json', "Authorization": f"Bearer {access_token_test}"}

@pytest.fixture
def auth_headers_admax(access_token_admax):
    return {'accept': 'application/json', "Authorization": f"Bearer {access_token_admax}"}

@pytest.fixture
def auth_headers_external_client(access_token_external_client):
    return {'accept': 'application/json', "Authorization": f"Bearer {access_token_external_client}"}

# Create a fixture for root user credentials
@pytest.fixture
def root_user_credentials():
    return {
        "username": "admax",
        "password": "XXXXX"
    }

# Create a fixture for test user credentials
@pytest.fixture
def test_user_credentials():
    return {
        "username": "test",
        "password": "XXXXX"
    }

# Create a fixture user to add
@pytest.fixture
def user_add():
    return {
        'user_id': 'test_user',
        'pwd_hash': 'test_password',
        'firstname': 'test_firstname',
        'lastname': 'test_lastname',
        'user_email': 'test_email',
        'position': 'test_position',
        'active': 1
    }

# Create a fixture user to edit
@pytest.fixture
def user_edit():
    return {
        'user_id': 'test_user',
        'pwd_hash': 'test_password_edit',
        'firstname': 'test_firstname_edit',
        'lastname': 'test_lastname_edit',
        'user_email': 'test_email_edit',
        'position': 'test_position_edit',
        'active': 1
    }

# Create a fixture user to edit_false
@pytest.fixture
def user_edit_false():
    return  {
        'user_id': 'test_user_false',
        'pwd_hash': 'test_password_edit',
        'firstname': 'test_firstname_edit',
        'lastname': 'test_lastname_edit',
        'user_email': 'test_email_edit',
        'position': 'test_position_edit',
        'active': 1
    }

# Create a fixture user admax to edit
@pytest.fixture
def user_edit_admax():
    return  {
        'user_id': 'admax',
        'pwd_hash': 'test_password_edit',
        'firstname': 'test_firstname_edit',
        'lastname': 'test_lastname_edit',
        'user_email': 'test_email_edit',
        'position': 'test_position_edit',
        'active': 1
    }


@pytest.fixture
def user_id_test():
    return  {
        'user_id': 'test_user'
    }

@pytest.fixture
def user_id_admax():
    return {
        'user_id': 'admax'
    }

@pytest.fixture
def user_permission():
    return  {
        'user_id': 'test',
        'permission_id' : 'get_data'
    }

@pytest.fixture
def user_permission_admax():
    return {
        'user_id': 'admax',
        'permission_id' : 'forecast'
    }

@pytest.fixture
def user_permission_false_permission():
    return  {
        'user_id': 'test',
        'permission_id' : 'false'
    }

@pytest.fixture
def user_permission_false_user():
    return {
        'user_id': 'false',
        'permission_id' : 'forecast'
    }

@pytest.fixture(params=["Arsac", "Ludon-Medoc", "Lamarque, FR", "Macau, FR","Castelnau-de-Medoc", "Soussan", "Margaux"])
def city_name(request):
    return request.param

##########################


def test_read_root(api_client):
    response = api_client.get("/")
    assert response.status_code == 200
    assert response.text == '"Welcome to the Joffrey LEMERY, Nicolas CARAYON and Jacques DROUVROY weather API (for places around Margaux-Cantenac)"'


# Use the fixture in the test function
def test_login(api_client: TestClient, root_user_credentials):
    test_user = root_user_credentials['username']
    test_password = root_user_credentials['password']
    response = api_client.post("/token", data={"username": test_user, "password": test_password})
    assert response.status_code == HttpCodes.success
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_read_users_me(api_client, root_user_credentials):
    # Not authenticated
    response = api_client.get("/users/me/")
    assert response.status_code == HttpCodes.not_authenticated
    # Authenticated
    expires_delta = timedelta(minutes=15)
    data = {"sub" : root_user_credentials["username"]}
    access_token = authent.create_access_token(data=data, expires_delta=expires_delta)
    headers = {'accept': 'application/json', "Authorization": f"Bearer {access_token}"}
    response =api_client.get("/users/me/", headers=headers)
    assert response.status_code == HttpCodes.success
    assert "user_id" in response.json()
    assert response.json()['user_id'] == 'admax'


def test_add_user(api_client, user_add, auth_headers_test, auth_headers_admax):
    # Not authenticated
    response = api_client.post("/add_user", params=user_add)
    assert response.status_code == HttpCodes.not_authenticated

    # Authenticated without permission
    response = api_client.post("/add_user", params=user_add, headers=auth_headers_test)
    assert response.status_code == HttpCodes.access_refused

    # Authenticated with permission
    response = api_client.post("/add_user", params=user_add, headers=auth_headers_admax)
    assert response.status_code == HttpCodes.success

    # Authenticated with permission trying to add an already existing user_id
    response = api_client.post("/add_user", params=user_add, headers=auth_headers_admax)
    assert response.status_code == HttpCodes.bad_request



def test_edit_user(api_client, user_edit, user_edit_false, user_edit_admax, auth_headers_test, auth_headers_admax):

    # Not authentificated
    response = api_client.post("/edit_user", params=user_edit)
    assert response.status_code == HttpCodes.not_authenticated

    # Authenticated without permission
    response = api_client.post("/edit_user", params=user_edit, headers=auth_headers_test)
    assert response.status_code == HttpCodes.access_refused

    # Authenticated with permission trying to edit non editable user "admax"
    response = api_client.post("/edit_user", params=user_edit_admax, headers=auth_headers_admax)
    assert response.status_code == HttpCodes.access_refused

    # Authenticated with permission trying to edit non existing user
    response = api_client.post("/edit_user", params=user_edit_false, headers=auth_headers_admax)
    assert response.status_code == HttpCodes.bad_request

    # Authenticated with permission editing existing user
    response = api_client.post("/edit_user", params=user_edit, headers=auth_headers_admax)
    assert response.status_code == HttpCodes.success


def test_delete_user(api_client, user_id_test, user_id_admax, auth_headers_test, auth_headers_admax):
    # Not authenticated
    response = api_client.post("/delete_user", params=user_id_test)
    assert response.status_code == HttpCodes.not_authenticated

    # Authenticated without permission
    response = api_client.post("/delete_user", params=user_id_test, headers=auth_headers_test)
    assert response.status_code == HttpCodes.access_refused

    # Authenticated with permission trying to delete non editable user "admax"
    response = api_client.post("/delete_user", params=user_id_admax, headers=auth_headers_admax)
    assert response.status_code == HttpCodes.access_refused

    # Authenticated with permission deleting existing user
    response = api_client.post("/delete_user", params=user_id_test, headers=auth_headers_admax)
    assert response.status_code == HttpCodes.success

    # Authenticated with permission trying to delete non existing user    
    response = api_client.post("/delete_user", params=user_id_test, headers=auth_headers_admax)
    assert response.status_code == HttpCodes.bad_request


def test_add_user_permission(api_client, user_permission, user_permission_admax, user_permission_false_user, user_permission_false_permission , auth_headers_test, auth_headers_admax):

    # Not authenticated
    response = api_client.post("/add_user_permission", params=user_permission)
    assert response.status_code == HttpCodes.not_authenticated

    # Authenticated without permission    
    response = api_client.post("/add_user_permission", params=user_permission, headers=auth_headers_test)
    assert response.status_code == HttpCodes.access_refused

    # Authenticated with permission trying to add permission to non editable user "admax"
    response = api_client.post("/add_user_permission", params=user_permission_admax, headers=auth_headers_admax)
    assert response.status_code == HttpCodes.access_refused

    # Authenticated with permission trying to add permission to a non existing user_id    
    response = api_client.post("/add_user_permission", params=user_permission_false_user, headers=auth_headers_admax)
    assert response.status_code == HttpCodes.bad_request

    # Authenticated with permission trying to add a non existing permission_id    
    response = api_client.post("/add_user_permission", params=user_permission_false_permission, headers=auth_headers_admax)
    assert response.status_code == HttpCodes.bad_request

    # Authenticated with permission    
    response = api_client.post("/add_user_permission", params=user_permission, headers=auth_headers_admax)
    assert response.status_code == HttpCodes.success


def test_delete_user(api_client, user_id_test, user_id_admax, auth_headers_test, auth_headers_admax):

    # Not authenticated
    response = api_client.post("/delete_user", params=user_id_test)
    assert response.status_code == HttpCodes.not_authenticated

    # Authenticated without permission
    response = api_client.post("/delete_user", params=user_id_test, headers=auth_headers_test)
    assert response.status_code == HttpCodes.access_refused

    # Authenticated with permission trying to delete non editable user "admax"
    response = api_client.post("/delete_user", params=user_id_admax, headers=auth_headers_admax)
    assert response.status_code == HttpCodes.access_refused

    # Authenticated with permission deleting existing user   
    response = api_client.post("/delete_user", params=user_id_test, headers=auth_headers_admax)
    assert response.status_code == HttpCodes.success

    # Authenticated with permission trying to delete non existing user
    response = api_client.post("/delete_user", params=user_id_test, headers=auth_headers_admax)
    assert response.status_code == HttpCodes.bad_request


def test_delete_user_permission(api_client, user_permission, user_permission_admax, user_permission_false_user, user_permission_false_permission , auth_headers_test, auth_headers_admax):

    # Not authenticated
    response = api_client.post("/delete_user_permission", params = user_permission)
    assert response.status_code == HttpCodes.not_authenticated

    # Authenticated without permission
    response = api_client.post("/delete_user_permission", params =  user_permission, headers=auth_headers_test)
    assert response.status_code == HttpCodes.access_refused

    # Authenticated with permission trying to delete permission to non editable user_id "admax"
    response = api_client.post("/delete_user_permission", params = user_permission_admax, headers=auth_headers_admax)
    assert response.status_code == HttpCodes.access_refused

    # Authenticated with permission trying to delete permission to a non existing user_id    
    response = api_client.post("/delete_user_permission", params = user_permission_false_user, headers=auth_headers_admax)
    assert response.status_code == HttpCodes.bad_request

    # Authenticated with permission trying to delete non existing permission_id to user_id
    response = api_client.post("/delete_user_permission", params = user_permission_false_permission, headers=auth_headers_admax)
    assert response.status_code == HttpCodes.bad_request

    # Authenticated with permission delete existing permission_id to existing user_id   
    response = api_client.post("/delete_user_permission", params = user_permission, headers=auth_headers_admax)
    assert response.status_code == HttpCodes.success


def test_get_logs(api_client, auth_headers_test, auth_headers_admax):

    # Not authenticated
    response = api_client.post("/get_logs")
    assert response.status_code == HttpCodes.not_authenticated

    # Authenticated without permission
    response = api_client.post("/get_logs", headers=auth_headers_test)
    assert response.status_code == HttpCodes.access_refused

    # Authenticated with permission
    response = api_client.post("/get_logs", headers=auth_headers_admax)
    assert response.status_code == HttpCodes.success


def test_populate_weather_table(api_client, auth_headers_test, auth_headers_admax):

    # Not authenticated
    response = api_client.post("/populate_weather_table")
    assert response.status_code == HttpCodes.not_authenticated

    # Authenticated without permission
    response = api_client.post("/populate_weather_table", headers=auth_headers_test)
    assert response.status_code == HttpCodes.access_refused

    # Authenticated with permission
    response = api_client.post("/populate_weather_table", headers=auth_headers_admax)
    assert response.status_code == HttpCodes.success


def test_update_weather_data(api_client, auth_headers_test, auth_headers_admax):

    # Not authenticated
    response = api_client.post("/update_weather_data")
    assert response.status_code == HttpCodes.not_authenticated

    # Authenticated without permission
    response = api_client.post("/update_weather_data", headers=auth_headers_test)
    assert response.status_code == HttpCodes.access_refused

    # Authenticated with permission
    response = api_client.post("/update_weather_data", headers=auth_headers_admax)
    assert response.status_code == HttpCodes.success


def test_forecast_city(api_client, city_name, auth_headers_test, auth_headers_admax):
    
    # Not authenticated
    response = api_client.post("/forecast_city/{city}?name_city="+str(city_name))
    assert response.status_code == HttpCodes.not_authenticated

    # Authenticated without permission
    response = api_client.post("/forecast_city/{city}?name_city="+str(city_name), headers=auth_headers_test)
    assert response.status_code == HttpCodes.access_refused

    # Authenticated with permission
    response = api_client.post('/forecast_city/{city}?name_city='+str(city_name), headers=auth_headers_admax)
    print(response)
    assert response.status_code == HttpCodes.success

def test_forecast_data(api_client, city_name, auth_headers_test, auth_headers_external_client):
   
    # Not authenticated
    response = api_client.get("/forecast_data/?name_city="+str(city_name))
    assert response.status_code == HttpCodes.not_authenticated

    # Authenticated without permission
    response = api_client.get("/forecast_data/?name_city="+str(city_name), headers=auth_headers_test)
    assert response.status_code == HttpCodes.success

    # Authenticated with permission
    response = api_client.get("/forecast_data/?name_city="+str(city_name), headers=auth_headers_external_client)
    assert response.status_code == HttpCodes.success


def test_delete_weather_data(api_client, auth_headers_test, auth_headers_admax):

    # Not authenticated
    response = api_client.post("/delete_weather_data")
    assert response.status_code == HttpCodes.not_authenticated

    # Authenticated without permission
    response = api_client.post("/delete_weather_data", headers=auth_headers_test)
    assert response.status_code == HttpCodes.access_refused

    # Authenticated with permission
    response = api_client.post("/delete_weather_data", headers=auth_headers_admax)
    assert response.status_code == HttpCodes.success

def test_delete_forecast_data(api_client, auth_headers_test, auth_headers_admax):

    # Not authenticated
    response = api_client.post("/delete_forecast_data")
    assert response.status_code == HttpCodes.not_authenticated

    # Authenticated without permission
    response = api_client.post("/delete_forecast_data", headers=auth_headers_test)
    assert response.status_code == HttpCodes.access_refused

    # Authenticated with permission
    response = api_client.post("/delete_forecast_data", headers=auth_headers_admax)
    assert response.status_code == HttpCodes.success