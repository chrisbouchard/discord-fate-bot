from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from discord.ext.commands import BadArgument, Converter

BOOL_TRUE_VALUES = { 'yes', 'y', 'true', 't', '1', 'enable', 'on' }
BOOL_FALSE_VALUES = { 'no', 'n', 'false', 'f', '0', 'disable', 'off' }


class Tag:
    def __init_subclass__(cls, *, tag_name = None, **kwargs):
        cls.tag_name = tag_name


@dataclass
class BoolTag(Tag):
    """Tag to set a boolean value"""

    value: bool

    @classmethod
    async def convert(cls, ctx, argument):
        key, separator, value = argument.partition('=')

        if key != cls.tag_name:
            raise BadArgument(f'Unexpected tag {key}')

        if not separator:
            return cls(value=True)

        if not value:
            raise BadArgument(f'Expected {cls.tag_name}[=BOOL]')

        lowered = value.lowered()

        if lowered in BOOL_TRUE_VALUES:
            return cls(value=True)
        elif lowered in BOOL_FALSE_VALUES:
            return cls(value=False)
        raise BadArgument(f'{value} is not a recognised boolean option')


@dataclass
class CountTag(Tag):
    """Tag to set or modify the a count value"""

    class Action(metaclass=ABCMeta):
        @abstractmethod
        def apply(self, current, value):
            ...

    value: int
    action: Action

    def apply(self, current):
        return self.action.apply(current, self.value)

    @classmethod
    async def convert(cls, ctx, argument):
        key, separator, value = argument.partition('=')

        action = cls._SetAction()
        negate = False

        if key.endswith('+'):
            key = key[:-1]
            action = cls._ModifyAction()
        elif key.endswith('-'):
            key = key[:-1]
            action = cls._ModifyAction()
            negate = True

        if key != cls.tag_name:
            raise BadArgument(f'Unexpected tag {key}')

        if not value:
            raise BadArgument(f'Expected {cls.tag_name}[OP]=VALUE')

        try:
            int_value = int(value)
        except ValueError:
            raise BadArgument(f'{value} is not a recognized number format')

        return cls(value=int_value, action=action)

    class _SetAction(Action):
        def apply(self, current, value):
            return value

    class _ModifyAction(Action):
        def apply(self, current, value):
            return current + value


class Separator(Converter):
    """Converter that looks for a literal value and ignores it. This is useful as a
    separator to force a Greedy list to end.
    """

    literal: str

    def __init__(self, literal: str = '--'):
        self.literal = literal

    async def convert(self, ctx, argument):
        if argument != self.literal:
            raise BadArgument(f'Expected "{self.literal}"')
        return None

