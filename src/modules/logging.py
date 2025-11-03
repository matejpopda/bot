
import logging
import logging.handlers

from pathlib import Path



def get_rotating_file_handler(file_path):
    handler = logging.handlers.RotatingFileHandler(file_path, mode='w', maxBytes=1_000_000, backupCount=3)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s")
    handler.setFormatter(formatter)
    return handler

def get_console_handler():
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    return handler

def setup_database_logging():
    logfilepath = Path('logs/sql.log')

    logfilepath.parent.mkdir(exist_ok=True)

    logger = logging.getLogger('sqlalchemy')
    logger.propagate = False
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_rotating_file_handler(logfilepath))
    

def setup_discord_logging():
    logfilepath = Path('logs/discord.log')

    logfilepath.parent.mkdir(exist_ok=True)

    logger = logging.getLogger('discord')
    logger.propagate = False
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_rotating_file_handler(logfilepath))

def setup_root_logging():
    logfilepath = Path('logs/bot.log')

    logfilepath.parent.mkdir(exist_ok=True)

    logger = logging.getLogger()
    logger.propagate = False
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_rotating_file_handler(logfilepath))
    logger.addHandler(get_console_handler())
    


def setup_all_logging():
    setup_database_logging()
    setup_discord_logging()
    setup_root_logging()