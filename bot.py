import asyncio
import logging
import sys

from discord.ext import commands

logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.INFO,
    datefmt="[%m/%d/%y] %H:%M:%S",
    stream=sys.stderr,
)
LOGGER = logging.getLogger(__name__)
logging.getLogger("chardet.charsetprober").disabled = True

bot = commands.Bot(command_prefix='h!')

@bot.event
async def on_ready():
    LOGGER.info(f'{bot.user.name} connected to Discord.')
    for guild in bot.guilds:
        LOGGER.info(f'Connected to {guild}')


#############################################################
#                                                           #
#                        Search                             #
#                                                           #
#############################################################
@bot.command(name='create')
async def create_heart(ctx, *, message):
    LOGGER.info(f'Got create request from {ctx.author}: {message}')

    if (blacklist.intersection(message.split(' '))):
        await ctx.send(embed=get_error_embed('Blacklisted Tags', 'One or more requested tags are blacklisted.'))
        return

    try:
        e6_resp = await get_e621_json(message, DEFAULT_LIMIT, get_order(), get_rating(), str(get_score_threshold()))
    except (E6ApiError, E6ResponseError):
        await ctx.send(embed=get_error_embed('e621 API Error', 'Error searching e621.'))
        return

    if (len(e6_resp) <= 0):
        embed = get_error_embed('Tags Not Found', f'Unable to find any posts matching the tags {message}')
        await ctx.send(embed=embed)
        return

    acceptable_post = get_random_nonblacklisted_post(e6_resp, blacklist)

    if (acceptable_post is None):
        embed = get_error_embed('Blacklisted Tags', f'Unable to find an post with tags {message} '
                                                    f'not also including blacklisted tags')
        await ctx.send(embed=embed)
        return

    await ctx.send(embed=get_discord_embed(acceptable_post))


#############################################################
#                                                           #
#                       Settings                            #
#                                                           #
#############################################################
@bot.group()
async def settings(ctx):
    if ctx.invoked_subcommand is None:
        embed = get_error_embed('No Subcommand Passed',
                                'The `setting` command has subcommands. See `e!help bl` for details.')
        await ctx.send(embed=embed)


@settings.command()
async def update(ctx, *, message):
    try:
        success_message = update_app_settings(message)
        await ctx.send(success_message)
    except Exception as err:
        await ctx.send(str(err))


@settings.command()
async def get(ctx, *, message):
    try:
        success_message = get_app_setting(message)
        await ctx.send(success_message)
    except Exception as err:
        await ctx.send(str(err))


#############################################################
#                                                           #
#                       Blacklist                           #
#                                                           #
#############################################################
@bot.group()
async def bl(ctx):
    if ctx.invoked_subcommand is None:
        embed = get_error_embed('No Subcommand Passed', 'The `bl` command has subcommands. See `e!help bl` for details.')
        await ctx.send(embed=embed)


@bl.command()
async def check(ctx):
    blacklist = blacklist_dao.get_blacklist_for_server(ctx.guild.id)
    if len(blacklist) == 0 or not blacklist_dao.server_in_database(ctx.guild.id):
        await ctx.send(f'This server is not currently blacklisting any tags.')
    else:
        await ctx.send(f'This server is currently blacklisting the tags: {" ".join(blacklist)}')


@bl.command()
async def add(ctx, *, message):
    if not blacklist_dao.server_in_database(ctx.guild.id):
        blacklist_dao.add_server_to_database(ctx.guild.id, ctx.guild.name)
    tags = ''
    ignore = ''
    for tag in message.split(' '):
        if blacklist_dao.add_tag_to_blacklist(tag, ctx.guild.id):
            tags += f'`{tag}` '
        else:
            ignore += f'`{tag}` '
    response = ''
    if len(tags) > 0:
        response += f"Added {tags} to the server's blacklist."
    if len(ignore) > 0:
        response += f"{'' if len(tags) == 0 else ' '}" \
                    f"Ignoring {ignore} as {'it is' if len(ignore.split(' ')) == 2 else 'they are'} " \
                    f"already blacklisted."
    await ctx.send(response)


@bl.command(name='rm')
async def remove(ctx, *, message):
    blacklist = blacklist_dao.get_blacklist_for_server(ctx.guild.id)
    if len(blacklist) == 0 or not blacklist_dao.server_in_database(ctx.guild.id):
        embed = get_error_embed('No Blacklist', 'This server is not currently blacklisting any tags.')
        await ctx.send(embed=embed)
        return
    tags = ''
    ignore = ''
    for tag in message.split(' '):
        if blacklist_dao.rm_tag_from_blacklist(tag, ctx.guild.id):
            tags += f'`{tag}` '
        else:
            ignore += f'`{tag}` '
    response = ''
    if len(tags) > 0:
        response += f"Removed {tags} from the server's blacklist."
    if len(ignore) > 0:
        response += f"{'' if len(tags) == 0 else ' '}" \
                    f"Ignoring {ignore} as {'it is' if len(ignore.split(' ')) == 2 else 'they are'} " \
                    f"not blacklisted."
    await ctx.send(response)


if __name__ == '__main__':
    bot.run(DISCORD_TOKEN)

    for task in asyncio.Task.all_tasks():
        task.cancel()
