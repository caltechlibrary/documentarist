from loguru import logger
import sys
from os import environ

logger.trace('a trace msg won\'t be printed by default')
os.environ('LOGURU_FORMAT', "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
