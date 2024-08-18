from utils.manager import AIManager
from utils.manager import Tools as managerTool
import discord
import asyncio
import json
import re

class SetupChat:
    def __init__(self, bot, interaction, chat_model, channel_id, first_msg,
                  monika_thread_id, sayori_thread_id, natsuki_thread_id,
                  yuri_thread_id):
        self.bot = bot
        self.interaction: discord.Interaction = interaction
        self.chat_model = chat_model
        self.channel_id = channel_id
        self.first_msg = first_msg
        self.monika_thread_id = monika_thread_id
        self.sayori_thread_id = sayori_thread_id
        self.natsuki_thread_id = natsuki_thread_id
        self.yuri_thread_id = yuri_thread_id
        self.tools = Tools(self.bot)
        self.chars = {"Monika": self.monika_thread_id, "Sayori": self.sayori_thread_id,
                     "Natsuki": self.natsuki_thread_id, "Yuri": self.yuri_thread_id}
        with open(f'{self.bot.PATH}/config.json') as f:
            self.config = json.load(f)
        with open(f"{self.bot.PATH}/assets/prompts/prompt_template.json") as f:
            self.prompt_template = json.load(f)



    async def setup(self):
        default_chathistory = self.bot.PATH + f"/data/{self.channel_id}.json"
        chathistory = await self.tools.checkFile(default_chathistory)

        userInput = "{RST}" if self.first_msg else "continue"

        self.bot.active_chat.append(self.channel_id)
        return await self.chatText(userInput=userInput, chathistory=chathistory)




    async def chatText(self, userInput, chathistory, msg_id_for_reply=None, user_name=""):

        if self.channel_id not in self.bot.active_chat:
            return

        channel_obj = self.bot.get_channel(self.channel_id)

        reply, character = await AIManager(
            bot=self.bot,
            channel_id=self.channel_id,
            chat_model=self.chat_model,
            chathistory=chathistory
            ).AIResponse(userInput)
        print(reply, character)

        reply = re.sub("<@(.*?)>", f'{user_name}', reply)
        reply = reply.replace("@", "")
        
        if character in self.chars:
            # Using custom made bots instead of a webhook
            for doki in self.chars:
                if character == doki:
                    cs_obj = self.bot.get_channel(self.chars[doki])

            msg_id_for_reply = "" if msg_id_for_reply == None else f" <||{msg_id_for_reply}||>" 
            channel_id_for_msg = f" <||{self.channel_id}||>"
            # Sends message in private thread for the other bot to capture with their on_message event
            await cs_obj.send(reply + msg_id_for_reply + channel_id_for_msg)


            # Wait for user to send msg
            try:
                raw_msg: discord.Message = await self.bot.wait_for("message",
                check=lambda m: m.channel.id == channel_obj.id and not m.author.bot, 
                timeout = 180)

                header =   f"[NAME] <@{raw_msg.author.id}> [CONTENT] " 
                user_content =  ''.join(char for char in raw_msg.content.strip())
                user_content = await managerTool(self.bot).filterWords(user_content)


                userInput = header + user_content
                userInput = userInput[:256] # Number of characters allowed (not words)
                print('Message was captured')

                msg_id_for_reply = raw_msg.id
                hasProfanity = await managerTool(self.bot).hasProfanity(raw_msg.author.display_name)
                user_name = raw_msg.author.display_name if hasProfanity == False else "Anon"

            except asyncio.exceptions.TimeoutError:
                print('\n\nNo one responded so timeout for chatText was reached')
                userInput = 'continue'
                msg_id_for_reply = None
                #user_name = ""

        else:
            if reply and (reply!="ERROR"): 
                await channel_obj.send(content=reply)
            else:
                # A False value was returned
                error = character
                if error:
                    return await channel_obj.send(error)

        return await self.chatText(userInput=userInput, chathistory=chathistory, msg_id_for_reply=msg_id_for_reply, user_name=user_name)







class Tools:
    def __init__(self, bot):
        self.bot = bot


    async def checkFile(self, chathistory_path):
        try:
            with open(chathistory_path, 'r') as f:
                chathistory = json.load(f)
                return chathistory
        except FileNotFoundError:
            chathistory = []
            with open(chathistory_path, 'w') as f:
                json.dump(chathistory, f, indent=2)
        return chathistory

