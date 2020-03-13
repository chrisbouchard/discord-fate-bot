import random

from dataclasses import dataclass, field, replace
from functools import total_ordering
from typing import Sequence

from .util import join_as_columns

FATE_DIE_POOL_SIZE = 4


@dataclass
@total_ordering
class Value:
    raw_value: int
    hide_plus: bool = False
    show_space: bool = False

    def no_plus(self):
        return replace(self, hide_plus=True)

    def with_space(self):
        return replace(self, show_space=True)

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
        output = ''

        if self.raw_value >= 0:
            if not self.hide_plus:
                output += '+'
                if self.show_space:
                    output += ' '
        else:
            output += '−'
            if self.show_space:
                output += ' '

        output += str(abs(self.raw_value))
        return output

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
    width: int = 3

    def __str__(self):
        side = '─' * max(self.width, len(self.label))
        return '\n'.join((
            f'╭{side}╮ ',
            f'│{self.label:^{self.width}}│ ',
            f'╰{side}╯ '
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

    def description(self):
        shifts = self.result()

        if self.context.opposition is None:
            return f'You generated **{shifts}** shifts.'

        if shifts >= 3:
            return f'You **succeeded with style** with **{shifts}** shifts!'
        elif shifts > 0:
            return f'You **succeeded** with **{shifts}** shifts.'
        elif shifts < 0:
            return f'You **failed** with **{shifts}** shifts.'
        else:
            return "You **tied**."

    def dice_display(self):
        return join_as_columns(self.faces)

    def explanation(self):
        explanation_str = f'You rolled  ⟦{self.dice_total().no_plus()}⟧'

        if self.context.modifiers:
            explanation_str += ''.join(f' {modifier.with_space()}' for modifier in self.context.modifiers)

        explanation_str += f'  =  **{self.total().no_plus()}**'

        if self.context.opposition is not None:
            explanation_str += f'   vs   {self.context.opposition.no_plus()}'

        explanation_str += '.'

        return explanation_str

@dataclass
class DiePool:
    dice: Sequence[Die]

    def roll(self, context: RollContext) -> Roll:
        return Roll(tuple(die.roll() for die in self.dice), context)


class FateDie(Die):
    def __init__(self):
        super().__init__(
            faces = (
                DieFace(label = '╺━╸', value = Value(-1)),
                DieFace(label = ' ', value = Value(0)),
                DieFace(label = '╺╋╸', value = Value(1)),
            )
        )

class FateDiePool(DiePool):
    def __init__(self, size: int = FATE_DIE_POOL_SIZE):
        super().__init__(tuple(FateDie() for _ in range(size)))

