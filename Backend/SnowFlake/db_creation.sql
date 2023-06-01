DROP DATABASE Wheather_Chateau_Margaux; 

CREATE DATABASE Wheather_Chateau_Margaux;

USE DATABASE Wheather_Chateau_Margaux;

CREATE TABLE cities (
    id NUMBER IDENTITY,
    city STRING
);

CREATE TABLE users (
    user_id STRING PRIMARY KEY,
    pwd_hash STRING,
    firstname STRING,
    lastname STRING,
    user_email STRING,
    position STRING,
    create_date DATE,
    last_upd_date DATE,
    active BOOLEAN
);

CREATE TABLE permissions (
    permission_id STRING PRIMARY KEY,     
    description STRING
);

CREATE TABLE user_permission (
    user_id STRING,
    permission_id STRING,
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(permission_id) REFERENCES permissions(permission_id)
);

CREATE TABLE weather_data (
    id INTEGER,
    observation_time TIMESTAMP_NTZ,
    temperature FLOAT,
    weather_code INTEGER,
    wind_speed FLOAT,
    wind_degree INTEGER,
    wind_dir STRING,
    pressure FLOAT,
    precip FLOAT,
    humidity INTEGER,
    cloudcover INTEGER,
    feelslike FLOAT,
    uv_index INTEGER,
    visibility INTEGER,
    time STRING,
    city STRING
);

INSERT INTO users (user_id, pwd_hash, create_date, last_upd_date, active)
VALUES
('airflow_train', '$2b$12$4mDimtgnr1BfIPFuU.hGK.sZGCzibTzRlgWEliug6IeGoPuZhXnry', current_date, current_date, 'True'),
('admax', '$2b$12$4mDimtgnr1BfIPFuU.hGK.sZGCzibTzRlgWEliug6IeGoPuZhXnry', current_date, current_date, 'True'),
('nico', '$2b$12$4mDimtgnr1BfIPFuU.hGK.sZGCzibTzRlgWEliug6IeGoPuZhXnry', current_date, current_date, 'True'),
('jacques', '$2b$12$4mDimtgnr1BfIPFuU.hGK.sZGCzibTzRlgWEliug6IeGoPuZhXnry', current_date, current_date, 'True'),
('joffrey', '$2b$12$4mDimtgnr1BfIPFuU.hGK.sZGCzibTzRlgWEliug6IeGoPuZhXnry', current_date, current_date, 'True');


INSERT INTO permissions (permission_id, description)
VALUES 
('get_pred', 'get wheater prediction'),
('training', 'launch model training'),
('usr_create', 'user creation'),
('usr_edit', 'user edition'),
('usr_deactivate', 'user deactivation'),
('forecast', 'get 7 days forecast'),
('get_data', 'get data from weather api'),
('forecast', 'get 7 days forecast');

INSERT INTO user_permission (user_id, permission_id)
VALUES
('airflow_train', 'forecast'),
('airflow_train', 'get_data'),
('airflow_train', 'training'),
('admax', 'forecast'),
('admax', 'get_data'),
('admax', 'training'),
('nico', 'forecast'),
('nico', 'get_data'),
('nico', 'training'),
('jacques', 'forecast'),
('jacques', 'get_data'),
('jacques', 'training'),
('joffrey', 'forecast'),
('joffrey', 'get_data'),
('joffrey', 'training');