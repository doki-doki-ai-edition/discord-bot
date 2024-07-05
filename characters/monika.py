from discord.ext import commands
import discord
import json
import os
import re

PATH = os.path.dirname(os.path.realpath(__file__))

with open(f'{PATH}/config.json') as f:
    config = json.load(f)

TOKEN = config["MONIKA_TOKEN"]
INTENTS = discord.Intents.default()
INTENTS.members = True
INTENTS.message_content = True
COMMAND_PREFIX = "mm!"


THREAD_ID = 1258250947797454858


class Bot(commands.Bot):

    async def on_ready(self):
        print(f"Running on version: {discord.__version__} ")


    async def on_message(self, message: discord.Message):
        if message.channel.id == bot.monika_thread_id:
            print("caught msg")
            if message.author.bot:
                print('detected bot')

                try: raw_msg_id = message.content.split()[-2]
                except IndexError: raw_msg_id = ""

                raw_channel_id = message.content.split()[-1]

                pattern = r"<\|\|(.*?)\|\|>"
                found_msg_id = re.search(pattern, raw_msg_id)
                found_channel_id = re.search(pattern, raw_channel_id)

                actual_msg = re.sub(pattern, '', message.content)

                if found_msg_id:
                    print(f"msg id: {found_msg_id.group(1)}")
                    channel_obj = bot.get_channel(int(found_channel_id.group(1)))
                    
                    reply_obj = await channel_obj.fetch_message(int(found_msg_id.group(1).strip()))
                    await reply_obj.reply(actual_msg)
                else:
                    channel_obj = bot.get_channel(int(found_channel_id.group(1)))
                    await channel_obj.send(actual_msg)


        await bot.process_commands(message)






bot = Bot(command_prefix=COMMAND_PREFIX,
          intents=INTENTS,
          case_insensitive=True,
          allowed_mentions=discord.AllowedMentions(roles=False, everyone=False),
          owner_ids=[1063386002955190312,285172553440296962]
        )

bot.monika_thread_id = THREAD_ID  # (Thread For storing messages)



@bot.command()
@commands.is_owner()
async def ping(ctx):
    await ctx.send("pong")


@bot.command()
@commands.is_owner()
async def set_thread(ctx, thread_id):
    bot.monika_thread_id =  int(thread_id)
    await ctx.send("set new thread id")


if __name__ == "__main__":
    bot.run(TOKEN)
