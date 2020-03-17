from dotenv import load_dotenv

import environ as _environ
import os

ENV_VAR_PREFIX = 'DFB'

@_environ.config
class BotConfig:
    token = _environ.var(help = 'The log-in token for the Discord bot account')

@_environ.config
class LogConfig:
    level = _environ.var('INFO', help = 'The minimum log level')

@_environ.config(prefix = ENV_VAR_PREFIX)
class Config:
    bot = _environ.group(BotConfig)
    log = _environ.group(LogConfig)


def read(environ = os.environ):
    load_dotenv()
    return _environ.to_config(Config, environ)

