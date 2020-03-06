import random

from dataclasses import dataclass, field
from functools import total_ordering
from typing import Sequence

from .util import join_as_columns

FATE_DIE_POOL_SIZE = 4

@dataclass
@total_ordering
class Value:
    raw_value: int

    def __add__(self, other):
        if isinstance(other, Value):
            return Value(self.raw_value + other.raw_value)
        elif isinstance(other, int):
            return Value(self.raw_value + other)
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, Value):
            return Value(other.raw_value + self.raw_value)
        elif isinstance(other, int):
            return Value(other + self.raw_value)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Value):
            return Value(self.raw_value - other.raw_value)
        elif isinstance(other, int):
            return Value(self.raw_value - other)
        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, Value):
            return Value(other.raw_value - self.raw_value)
        elif isinstance(other, int):
            return Value(other - self.raw_value)
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Value):
            return self.raw_value < other.raw_value
        elif isinstance(other, int):
            return self.raw_value < other
        return NotImplemented

    def __str__(self):
        sign = '+' if self.raw_value >= 0 else '−'
        return f'{sign}{abs(self.raw_value)}'


@dataclass
class RollContext:
    modifiers: Sequence[Value] = ()
    opposition: Value = Value(0)

    def total_modifier(self):
        return sum(self.modifiers)

    def total_opposition(self):
        return self.opposition or Value(0)

@dataclass
class DieFace:
    label: str
    value: Value

    def __str__(self):
        side = '─' * len(self.label)
        return '\n'.join((
            f'╭─{side}─╮',
            f'│ {self.label} │',
            f'╰─{side}─╯'
        ))

@dataclass
class Die:
    faces: Sequence[DieFace]

    def roll(self) -> DieFace:
        return random.choice(self.faces)

@dataclass
class Roll:
    faces: Sequence[DieFace]
    context: RollContext

    def dice_total(self):
        return sum(face.value for face in self.faces)

    def total(self):
        return sum(face.value for face in self.faces) + self.context.total_modifier()

    def result(self):
        return self.total() - self.context.total_opposition()

    def __str__(self):
        columns = (*self.faces, self._str_tag())
        return join_as_columns(columns)

    def _str_tag(self):
        tag = f'\n ({self.dice_total()})'

        if self.context.modifiers:
            tag += ''.join(f' {modifier}' for modifier in self.context.modifiers)

        tag += f'  =  {self.total()}'

        if self.context.opposition is not None:
            tag += f'   vs   {self.context.opposition}'

        return tag

@dataclass
class DiePool:
    dice: Sequence[Die]

    def roll(self, context: RollContext) -> Roll:
        return Roll(tuple(die.roll() for die in self.dice), context)


class FateDie(Die):
    def __init__(self):
        super().__init__(
            faces = (
                DieFace(label = '−', value = Value(-1)),
                DieFace(label = ' ', value = Value(0)),
                DieFace(label = '+', value = Value(1)),
            )
        )

class FateDiePool(DiePool):
    def __init__(self, size: int = FATE_DIE_POOL_SIZE):
        super().__init__(tuple(FateDie() for _ in range(size)))

