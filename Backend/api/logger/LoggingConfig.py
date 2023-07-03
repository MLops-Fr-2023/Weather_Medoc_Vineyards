import logging
from datetime import datetime 
import os

date_string = datetime.now().strftime('%Y%m%d')

def setup_logging():
    os.makedirs('logs', exist_ok=True)
    logging.basicConfig(
        filename=f"logs/app_{date_string}.log",
        filemode='a',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
