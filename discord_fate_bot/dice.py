import random

from dataclasses import dataclass
from typing import Sequence

FATE_DIE_POOL_SIZE = 4

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

    def total(self):
        return sum(face.value for face in self.faces)

    def __str__(self):
        return '\n'.join(
            ''.join(line) for line in zip(*(
                f'{face}'.splitlines() for face in self.faces
            ))
        )

@dataclass
class DiePool:
    dice: Sequence[Die]

    def roll(self) -> Roll:
        return Roll(tuple(die.roll() for die in self.dice))


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

