import aiofiles
import environ
import logging

@environ.config
class BotConfig:
    token = environ.var(
        None,
        help = (
            'The log-in token for the Discord bot account '
            '(mutually exclusive with DFB_BOT_TOKEN_FILE)'
        )
    )

    token_file = environ.var(
        None,
        help = (
            'The path to a file containing the log-in token '
            '(mutually exclusive with DFB_BOT_TOKEN)'
        )
    )

    @token.validator
    def _token_valid(self,  attribute, value):
        if self.token is None and self.token_file is None:
            raise ValueError(
                'One of DFB_BOT_TOKEN or DFB_BOT_TOKEN_FILE is required'
            )

        if self.token is not None and self.token_file is not None:
            raise ValueError(
                'Only one of DFB_BOT_TOKEN or DFB_BOT_TOKEN_FILE may be set'
            )

    async def read_token(self):
        """Read the token from the config, possibly from the filesystem."""
        if self.token_file is not None:
            async with aiofiles.open(self.token_file, 'r') as token_file:
                return (await token_file.read()).strip()

        return self.token

@environ.config
class DatabaseConfig:
    url = environ.var(help = "URL for the database connection")

@environ.config
class LogConfig:
    level = environ.var(None, help = 'The minimum log level')

    def apply_global():
        if self.level is not None:
            logging.basicConfig(level = self.level)


@environ.config(prefix = 'DFB')
class Config:
    bot = environ.group(BotConfig)
    database = environ.group(DatabaseConfig)
    log = environ.group(LogConfig)


@environ.config(prefix = 'DFB_MIGRATION')
class MigrationConfig:
    database = environ.group(DatabaseConfig)

