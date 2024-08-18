from discord.ext import commands
import discord
import json
import os

PATH = os.path.dirname(os.path.realpath(__file__))

with open(f'{PATH}/config.json') as f:
    config = json.load(f)

TOKEN = config["BOT_TOKEN"]
INTENTS = discord.Intents.default()
INTENTS.members = True
INTENTS.message_content = True
COMMAND_PREFIX = "dd!"

#TODO:
# - Mods can use some commands, not owner specific


class Bot(commands.Bot):

    async def setup_hook(self):
        """This will be called before any events are dispatched"""
        for filename in os.listdir(f'{PATH}/cogs'):
            if filename.endswith('.py'):
                await bot.load_extension(f'cogs.{filename[:-3]}')

    async def on_ready(self):
        print(f"Running on version: {discord.__version__} ")




bot = Bot(command_prefix=COMMAND_PREFIX,
          intents=INTENTS,
          allowed_mentions=discord.AllowedMentions(roles=False, everyone=False),
          owner_ids=[1063386002955190312,285172553440296962] # Replace or add your own UID from Discord
        )
bot.remove_command('help')
bot.PATH = PATH



bot.active_chat = []

bot.ddae_version = "0.2.0"


@bot.command()
@commands.is_owner()
async def sync(ctx):
    """Used to update all slash commands when a change is made to them"""
    await ctx.send("Attemping to sync...")
    try:
        synced = await bot.tree.sync()
    except discord.errors.HTTPException as e:
        print(f"Error during sync: {e}")
    return await ctx.send(f"{len(synced)} commands were synced.")


if __name__ == "__main__":
    bot.run(TOKEN)
