import asyncio
import logging
import os
import sys
import discord

from discord.ext import commands

from heart import create_heart

logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.INFO,
    datefmt="[%m/%d/%y] %H:%M:%S",
    stream=sys.stderr,
)
LOGGER = logging.getLogger(__name__)
logging.getLogger("chardet.charsetprober").disabled = True

LEGAL_HEX_VALUES = ('a', 'b', 'c', 'd', 'e', 'f', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9')

bot = commands.Bot(command_prefix='h!')

@bot.event
async def on_ready():
    LOGGER.info(f'{bot.user.name} connected to Discord.')
    for guild in bot.guilds:
        LOGGER.info(f'Connected to {guild}')

class InputReadingError(Exception):
    pass

#############################################################
#                                                           #
#                        Create                             #
#                                                           #
#############################################################
@bot.command(name='create')
async def handle_create_heart(ctx, *, message):
    LOGGER.info(f'Got create request from {ctx.author}: {message}')

    try:
        inside_hex, outside_hex = get_hex_input(message)
    except InputReadingError as err:
        LOGGER.error(f'Encountered input error: {str(err)}')
        await ctx.send(embed=get_error_embed('Input Error', str(err)))
        return

    print(f"Calling create_heart with inside_hex={inside_hex}, outside_hex={outside_hex}")

    saved_filename = create_heart(inside_hex, outside_hex)

    await ctx.send(file=discord.File(saved_filename))

    os.remove(saved_filename)


def get_hex_input(message):

    print(f'message: {message}')

    if (message is None):
        raise InputReadingError("No input found")

    if (len(message) != 15):
        raise InputReadingError("Input must be in the form of '#aaaaaa #bbbbbb'")

    if (message.find(" ") == -1):
        raise InputReadingError("No split character (' ') found.")

    values = message.split(' ')

    print(f'values: {values}')

    if (len(values) != 2):
        raise InputReadingError("More than two values found")

    for value in values:
        if (len(value) != 7):
            raise InputReadingError("Incorrectly formatted value found. Size incorrect. Must be of the form '#aaaaaa'. "
                                    "Value: ", value)

        if (value[0] != '#'):
            raise InputReadingError("Incorrectly formatted value found. Must begin with #. Value: ", value)

        for value_character in value[1:]:
            if (value_character.lower() not in LEGAL_HEX_VALUES):
                raise InputReadingError(f"Incorrectly formatted value found. Must only include hex values. Value: "
                                        f"{value_character.lower()}")

    return values[0], values[1]


def get_error_embed(title, desc):
    embed = discord.Embed(title=title,
                          description=desc,
                          color=0xe12020)
    return embed


if __name__ == '__main__':
    with open('discord_token.txt') as file:
        discord_token = file.read()
        bot.run(discord_token)

        for task in asyncio.Task.all_tasks():
            task.cancel()