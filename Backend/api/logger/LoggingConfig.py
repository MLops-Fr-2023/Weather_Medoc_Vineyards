import logging
from datetime import datetime 

date_string = datetime.now().strftime('%Y%m%d')

def setup_logging():
    logging.basicConfig(
        filename=f"app_{date_string}.log",
        filemode='a',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
