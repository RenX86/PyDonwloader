# logger.py
import logging

# Configure the logger for the application
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("myapp")

# Use this logger instance in all modules by importing:
# from logger import logger