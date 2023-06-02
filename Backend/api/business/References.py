from pydantic import BaseModel
from typing import Annotated, Optional, Union, List
from datetime import datetime, timedelta, time, date

cities = ['Margaux', 'Soussan', 'Macau, FR', 'Castelnau-de-Medoc','Lamarque, FR', 'Ludon-Medoc', 'Arsac', 'Brach, FR', 'Saint-Laurent Medoc' ]

columns_mandatory = ['observation_time','temperature','weather_code','wind_speed',
                     'wind_degree','wind_dir','pressure','precip','humidity',
                     'cloudcover','feelslike','uv_index','visibility','time','city']

list_permissions = ['forecast', 'get_data', 'training', 'user_mngt']
