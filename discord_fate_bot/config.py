from dotenv import load_dotenv

import environ as environ_
import os

ENV_VAR_PREFIX = 'DFB'

@environ_.config
class BotConfig:
    token = environ_.var(help = 'The log-in token for the Discord bot account')

@environ_.config
class LogConfig:
    level = environ_.var('INFO', help = 'The minimum log level')

@environ_.config(prefix = ENV_VAR_PREFIX)
class Config:
    bot = environ_.group(BotConfig)
    log = environ_.group(LogConfig)


def read(environ = os.environ):
    load_dotenv()
    return environ_.to_config(Config, environ)

