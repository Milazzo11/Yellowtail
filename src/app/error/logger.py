import logging
import os

# Configure basic logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename=os.path.join('data', 'err.log'),
                    filemode='a') # 'a' for append, 'w' for write



def log(message: str) -> None:
    """
    """

    logging.error(message)