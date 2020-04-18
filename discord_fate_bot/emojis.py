import random

from discord import Message

SCENE_EMOJI = '\N{Clapper Board}'
ROLL_EMOJI = '\N{Game Die}'

ERROR_EMOJIS = [
    '\N{Confounded Face}',
    '\N{Face Screaming in Fear}',
    '\N{Face with Head-Bandage}',
    '\N{Face with Open Mouth and Cold Sweat}',
    '\N{Face with Thermometer}',
    '\N{Freezing Face}',
    '\N{Grimacing Face}',
    '\N{Loudly Crying Face}',
    '\N{Overheated Face}',
    '\N{Weary Face}',
]

SUCCESS_EMOJIS = [
    '\N{Ballot Box with Check}',
    '\N{OK Hand Sign}',
    '\N{Squared OK}',
    '\N{Thumbs Up Sign}',
    '\N{White Heavy Check Mark}',
]


def random_error_emoji():
    return random.choice(ERROR_EMOJIS)

def random_success_emoji():
    return random.choice(SUCCESS_EMOJIS)


async def react_error(message):
    await message.add_reaction(random_error_emoji())

async def react_success(message):
    await message.add_reaction(random_success_emoji())

