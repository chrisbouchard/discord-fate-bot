import alembic.config
import importlib.resources
import sys

def main():
    with importlib.resources.path('discord_fate_bot.migrations', 'alembic.ini') as path:
        alembic_args = ['-c', str(path), *sys.argv[1:]]
        alembic.config.main(argv=alembic_args)

