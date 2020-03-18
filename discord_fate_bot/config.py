import environ as _environ  # Renaming to avoid shadowing in read(environ)
import os

@_environ.config
class BotConfig:
    token = _environ.var(
        None,
        help = 'The log-in token for the Discord bot account'
    )

    token_file = _environ.var(
        None,
        help = 'The path to a file containing the log-in token (takes precedence)'
    )

    def read_token(self):
        """Read the token from the config, possibly from the filesystem."""
        if self.token_file is not None:
            with open(self.token_file, 'r') as token_file:
                return token_file.read().strip()

        return self.token

@_environ.config
class LogConfig:
    level = _environ.var('INFO', help = 'The minimum log level')

@_environ.config(prefix = 'DFB')
class Config:
    bot = _environ.group(BotConfig)
    log = _environ.group(LogConfig)

    @bot.validator
    def _bot_token_valid(self,  attribute, value):
        if value.token is None and value.token_file is None:
            raise ValueError(
                'One of DFB_BOT_TOKEN or DFB_BOT_TOKEN_FILE is required'
            )

        if value.token is not None and value.token_file is not None:
            raise ValueError(
                'Only one of DFB_BOT_TOKEN or DFB_BOT_TOKEN_FILE may be set'
            )

