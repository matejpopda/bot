import dotenv
import pathlib
import logging


log = logging.getLogger("console")

def validate(): 
    config = dotenv.dotenv_values("config_files/.env")


    if not pathlib.Path("config_files/.env").exists():
        log.critical("Missing .env file, this expected on the first run. Use the .env.example in the directory where you mounted /app/config_files.")
        exit()
    else: 
        if not "TOKEN" in config:
            log.critical("Missing discord bot token in .env file. The file is wherever you mounted /app/config_files")
            exit()

        if not "GENIUS_TOKEN" in config:
            log.error("Missing genius token in .env file. The file is wherever you mounted /app/config_files. Song module will be broken. ")
