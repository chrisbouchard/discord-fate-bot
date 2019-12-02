import discord
import environ
import logging
import os

from discord_fate_bot import config

bot_config = environ.to_config(config.BotConfig, os.environ)

if bot_config.log_level is not None:
    logging.basicConfig(level=bot_config.log_level)

logger = logging.getLogger('discord_fate_bot')

client = discord.Client()

@client.event
async def on_ready():
    logger.debug('READY: Logged in as %s', client.user)

@client.event
async def on_message(message):
    logger.debug('MESSAGE: Received message: %s', message)

    # Don't get into a feedback loop!
    if message.author == client.user:
        return

    # Otherwise respond politely.
    if message.content.startswith('!hello'):
        await message.channel.send('Hello!')

# TODO: Get a real token. (From the environment?)
client.run(bot_config.token)

