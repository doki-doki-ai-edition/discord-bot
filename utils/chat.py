from utils.manager import AIManager
from utils.manager import Tools as tools
from utils.data import Info
import discord, asyncio, json, re, random

class ChatManager:
    def __init__(self, bot, interaction, chat_model, channel_id, first_msg, characters, chosen_prompt):
        self.bot = bot
        self.interaction: discord.Interaction = interaction
        self.chat_model = chat_model
        self.channel_id = channel_id
        self.first_msg = first_msg
        self.tools = Tools(self.bot)
        self.chars = characters
        self.chat_still_active = False
        with open(f'{self.bot.PATH}/config.json') as f:
            self.config = json.load(f)
        self.system_prompt = chosen_prompt



    async def setup(self):
        default_chathistory = self.bot.PATH + f"/data/{self.channel_id}.json"
        chathistory = await self.tools.checkFile(default_chathistory)
        userInput = "{RST}" if self.first_msg else "continue"

        self.bot.active_chat_channels.append(self.channel_id)
        self.chat_still_active = True
        return await self.chat(userInput=userInput, chathistory=chathistory)



    async def chat(self, userInput, chathistory, msg_id_for_reply=None, user_name=""):
        if self.channel_id not in self.bot.active_chat_channels:
            return

        channel_obj = self.bot.get_channel(self.channel_id)

        reply, character = await AIManager(
            bot=self.bot,
            channel_id=self.channel_id,
            chat_model=self.chat_model,
            chathistory=chathistory
            ).AIResponse(userInput, self.system_prompt)
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
                    check=lambda m: m.channel.id == channel_obj.id and 
                    not m.author.bot and self.chat_still_active and
                    m.author.id not in tools(self.bot).blacklist, 
                    timeout = 180
                )

                user_content = ''.join(char for char in raw_msg.content.strip())
                user_content = await tools(self.bot).filterWords(user_content)

                userInput = f"[NAME] <@{raw_msg.author.id}> [CONTENT] {user_content}" 
                userInput = userInput[:256] # Number of characters allowed (not words)
                
                print('Message was captured')

                msg_id_for_reply = raw_msg.id
                user_name = raw_msg.author.display_name

            except asyncio.exceptions.TimeoutError:
                print('\n\nNo one responded so timeout for chatText was reached')
                userInput = 'continue'
                msg_id_for_reply = None

        else:
            if reply and (reply!="ERROR"): 
                await channel_obj.send(content=reply)
            else:
                # A False value was returned
                error = character
                if error:
                    return await channel_obj.send(error)
        progressChance = random.randrange(0,3)
        if progressChance==0:
            print("Progressing convo...")
            userInput += r" {progress the conversation, or change subjects if necessary}"
        return await self.chat(userInput=userInput, chathistory=chathistory, msg_id_for_reply=msg_id_for_reply, user_name=user_name)







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

