/* DROP and CREATE DATABASE are deactivated on free MySql server use for dev environment */

CREATE TABLE CITIES (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    CITY VARCHAR(255)
);

CREATE TABLE USERS (
    USER_ID VARCHAR(255) PRIMARY KEY,
    PWD_HASH VARCHAR(255),
    FIRSTNAME VARCHAR(255),
    LASTNAME VARCHAR(255),
    USER_EMAIL VARCHAR(255),
    POSITION VARCHAR(255),
    CREATE_DATE DATE,
    LAST_UPD_DATE DATE,
    ACTIVE TINYINT(1)
);

CREATE TABLE PERMISSIONS (
    PERMISSION_ID VARCHAR(255) PRIMARY KEY,     
    DESCRIPTION VARCHAR(255)
);

CREATE TABLE USER_PERMISSION (
    USER_ID VARCHAR(255),
    PERMISSION_ID VARCHAR(255),
    FOREIGN KEY(USER_ID) REFERENCES USERS(USER_ID),
    FOREIGN KEY(PERMISSION_ID) REFERENCES PERMISSIONS(PERMISSION_ID)
);

CREATE TABLE WEATHER_DATA (
    ID INT,
    OBSERVATION_TIME DATETIME,
    TEMPERATURE FLOAT,
    WEATHER_CODE INT,
    WIND_SPEED FLOAT,
    WIND_DEGREE INT,
    WIND_DIR VARCHAR(255),
    PRESSURE FLOAT,
    PRECIP FLOAT,
    HUMIDITY INT,
    CLOUDCOVER INT,
    FEELSLIKE FLOAT,
    UV_INDEX INT,
    VISIBILITY INT,
    TIME VARCHAR(255),
    CITY VARCHAR(255)
);

INSERT INTO USERS (USER_ID, PWD_HASH, CREATE_DATE, LAST_UPD_DATE, ACTIVE)
VALUES
('external_client', '$2b$12$4mDimtgnr1BfIPFuU.hGK.sZGCzibTzRlgWEliug6IeGoPuZhXnry', CURDATE(), CURDATE(), 1),
('admax', '$2b$12$4mDimtgnr1BfIPFuU.hGK.sZGCzibTzRlgWEliug6IeGoPuZhXnry', CURDATE(), CURDATE(), 1),
('backend', '$2b$12$4mDimtgnr1BfIPFuU.hGK.sZGCzibTzRlgWEliug6IeGoPuZhXnry', CURDATE(), CURDATE(), 1),
('test', '$2b$12$4mDimtgnr1BfIPFuU.hGK.sZGCzibTzRlgWEliug6IeGoPuZhXnry', CURDATE(), CURDATE(), 1);

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
