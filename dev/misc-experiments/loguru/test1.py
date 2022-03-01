from loguru import logger
import sys
from os import environ

logger.info('this is a default info msg')

logger.remove()
logger.add(sys.stderr, format = '<g>{thread.name}</g> {module}:{line} <u>{function}()</u> <w>{message}</w>')

logger.info('this is after changing the default format')
