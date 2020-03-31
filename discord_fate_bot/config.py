import aiofiles
import environ

@environ.config
class BotGroup:
    token = environ.var(
        None,
        help = 'The log-in token for the Discord bot account ' \
        '(mutually exclusive with DFB_BOT_TOKEN_FILE)'
    )
    token_file = environ.var(
        None,
        help = 'The path to a file containing the log-in token ' \
        '(mutually exclusive with DFB_BOT_TOKEN)'
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
        return await _read_file_or_immediate_value(self.token_file, self.token)

@environ.config
class LogGroup:
    config_file = environ.var(None, help = 'The path to a configuration file for Python logging')

@environ.config
class MongoGroup:
    connection_url = environ.var(help = "URL for the MongoDB connection")
    password = environ.var(
        None,
        help = 'MongoDB password ' \
        '(mutually exclusive with DFB_MONGO_PASSWORD_FILE)'
    )
    password_file = environ.var(
        None,
        help = 'Path to a file containing the MongoDB password ' \
        '(mutually exclusive with DFB_MONGO_PASSWORD)'
    )

    @password.validator
    def _password_valid(self,  attribute, value):
        if self.password is not None and self.password_file is not None:
            raise ValueError(
                'Only one of DFB_MONGO_PASSWORD or DFB_MONGO_PASSWORD_FILE may be set'
            )

    async def read_password(self):
        """Read the password from the config, possibly from the filesystem."""
        return await _read_file_or_immediate_value(self.password_file, self.password)


@environ.config(prefix = 'DFB')
class Config:
    bot = environ.group(BotGroup)
    log = environ.group(LogGroup)
    mongo = environ.group(MongoGroup)


async def _read_file_or_immediate_value(path, immediate_value):
    if path is not None:
        async with aiofiles.open(path, 'r') as file:
            return (await file.read()).strip()

    return immediate_value

