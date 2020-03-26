import alembic.config
import importlib.resources
import sys

from .. import migrations

def main():
    with importlib.resources.path(migrations, 'alembic.ini') as path:
        alembic_args = ['-c', str(path), *sys.argv[1:]]
        alembic.config.main(argv=alembic_args)

