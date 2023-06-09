CREATE DATABASE WCM_DB;

USE DATABASE WCM_DB;

CREATE TABLE CITIES (
    ID NUMBER IDENTITY,
    CITY STRING
);

CREATE TABLE USERS (
    USER_ID STRING PRIMARY KEY,
    PWD_HASH STRING,
    FIRSTNAME STRING,
    LASTNAME STRING,
    USER_EMAIL STRING,
    POSITION STRING,
    CREATE_DATE DATE,
    LAST_UPD_DATE DATE,
    ACTIVE NUMBER(1, 0)
);

CREATE TABLE PERMISSIONS (
    PERMISSION_ID STRING PRIMARY KEY,     
    DESCRIPTION STRING
);

CREATE TABLE USER_PERMISSION (
    USER_ID STRING,
    PERMISSION_ID STRING,
    FOREIGN KEY(USER_ID) REFERENCES USERS(USER_ID),
    FOREIGN KEY(PERMISSION_ID) REFERENCES PERMISSIONS(PERMISSION_ID)
);

CREATE TABLE WEATHER_DATA (
    ID INTEGER,
    OBSERVATION_TIME TIMESTAMP_NTZ,
    TEMPERATURE FLOAT,
    WEATHER_CODE INTEGER,
    WIND_SPEED FLOAT,
    WIND_DEGREE INTEGER,
    WIND_DIR STRING,
    PRESSURE FLOAT,
    PRECIP FLOAT,
    HUMIDITY INTEGER,
    CLOUDCOVER INTEGER,
    FEELSLIKE FLOAT,
    UV_INDEX INTEGER,
    VISIBILITY INTEGER,
    TIME STRING,
    CITY STRING
);

INSERT INTO USERS (USER_ID, PWD_HASH, CREATE_DATE, LAST_UPD_DATE, ACTIVE)
VALUES
('external_client', '$2b$12$4mDimtgnr1BfIPFuU.hGK.sZGCzibTzRlgWEliug6IeGoPuZhXnry', current_date, current_date, 1),
('admax', '$2b$12$4mDimtgnr1BfIPFuU.hGK.sZGCzibTzRlgWEliug6IeGoPuZhXnry', current_date, current_date, 1),
('backend', '$2b$12$4mDimtgnr1BfIPFuU.hGK.sZGCzibTzRlgWEliug6IeGoPuZhXnry', current_date, current_date, 1)
('test', '$2b$12$4mDimtgnr1BfIPFuU.hGK.sZGCzibTzRlgWEliug6IeGoPuZhXnry', current_date, current_date, 1);


INSERT INTO PERMISSIONS (PERMISSION_ID, DESCRIPTION)
VALUES 
('training', 'launch model training'),
('user_management', 'user management'),
('get_data', 'get data from weather api'),
('forecast', 'get 7 days forecast');

INSERT INTO USER_PERMISSION (USER_ID, PERMISSION_ID)
VALUES
('external_client', 'forecast'),
('admax', 'forecast'),
('admax', 'get_data'),
('admax', 'user_management'),
('admax', 'training'),
('backend', 'training'),
('backend', 'get_data'),
('test', 'forecast');