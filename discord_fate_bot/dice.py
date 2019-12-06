import random

from dataclasses import dataclass, field
from typing import Sequence

from .util import join_as_columns

FATE_DIE_POOL_SIZE = 4

@dataclass
class RollContext:
    modifiers: Sequence[int] = ()
    opposition: int = None

    def is_opposed(self):
        return self.opposition is not None

    def total_modifier(self):
        return sum(self.modifiers)

    def total_opposition(self):
        return self.opposition or 0

@dataclass
class DieFace:
    label: str
    value: int

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

    def total(self):
        return sum(face.value for face in self.faces) + self.context.total_modifier()

    def result(self):
        return self.total() - self.context.total_opposition()

    def __str__(self):
        columns = (*self.faces, self._str_tag())
        return join_as_columns(columns)

    def _str_tag(self):
        tag = '\n'

        if self.context.modifiers:
            tag += ''.join(f' {modifier:+}' for modifier in self.context.modifiers)

        tag += f'  =  {self.total()}'

        if self.context.opposition is not None:
            tag += f'   vs  {self.context.opposition}'

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
                DieFace(label = '−', value = -1),
                DieFace(label = ' ', value = 0),
                DieFace(label = '+', value = 1),
            )
        )

class FateDiePool(DiePool):
    def __init__(self, size: int = FATE_DIE_POOL_SIZE):
        super().__init__(tuple(FateDie() for _ in range(size)))

