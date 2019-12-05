import environ
import logging

def log_level_numeric(log_level):
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')
    return numeric_level

@environ.config(prefix='DISCORD_FATE_BOT')
class Config:
    log_level = environ.var('INFO', converter=log_level_numeric)
    token = environ.var()

