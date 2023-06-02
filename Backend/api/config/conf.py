from dotenv import dotenv_values

config = {**dotenv_values(".env_API")}

SECRET_KEY = config['SECRET_KEY']
ALGORITHM = config['ALGORITHM']
ACCESS_TOKEN_EXPIRE_MINUTES = config['ACCESS_TOKEN_EXPIRE_MINUTES']
WEATHER_API_KEY = config['WEATHER_API_KEY']