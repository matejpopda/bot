
import logging
import logging.handlers

from pathlib import Path



def get_rotating_file_handler(file_path):
    handler = logging.handlers.RotatingFileHandler(file_path, mode='w', maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    handler.setLevel(logging.DEBUG)
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
    handler = get_rotating_file_handler(logfilepath)

    logger = logging.getLogger('sqlalchemy')
    logger.setLevel(logging.INFO)

    logger.propagate = False

    logger.addHandler(handler)

    logger = logging.getLogger("aiosqlite")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.addHandler(handler)
    

def setup_discord_logging():
    logfilepath = Path('logs/discord.log')

    logfilepath.parent.mkdir(exist_ok=True)

    logger = logging.getLogger('discord')
    logger.propagate = False
    logger.setLevel(logging.INFO)

    handler = get_rotating_file_handler(logfilepath)
    logger.addHandler(handler)
    
def setup_root_logging():
    logfilepath = Path('logs/root.log')

    logfilepath.parent.mkdir(exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    handler = get_rotating_file_handler(logfilepath)
    logger.addHandler(handler)
    

def setup_announcer_logging():
    logfilepath = Path('logs/console.log')

    logfilepath.parent.mkdir(exist_ok=True)

    logger = logging.getLogger("console")
    logger.setLevel(logging.DEBUG)

    handler = get_rotating_file_handler(logfilepath)
    logger.addHandler(handler)
    
    logger.addHandler(get_console_handler())

def setup_dailies_logging():
    logfilepath = Path('logs/dailies.log')

    logfilepath.parent.mkdir(exist_ok=True)

    logger = logging.getLogger("dailies")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    handler = get_rotating_file_handler(logfilepath)
    logger.addHandler(handler)
    


def setup_ignoring_of_loggers():
    logging.getLogger("matplotlib.font_manager").propagate = False
    logging.getLogger("PIL.PngImagePlugin").propagate = False
    



def setup_all_logging():
    setup_database_logging()
    setup_discord_logging()
    setup_root_logging()
    setup_announcer_logging()
    
    setup_dailies_logging()
    setup_ignoring_of_loggers()

