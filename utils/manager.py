from utils.data import Info, Configs
from utils.ai_tools import TextModel
import json, random


class AIManager():

    def __init__(self, bot, channel_id, chat_model, chathistory):
        self.bot = bot
        self.channel_id = channel_id
        self.chat_model = chat_model
        self.chathistory = chathistory
        self.tools = Tools(self.bot)



    @property
    def count_tokens(self):
        current_letters = 0
        for content in self.chathistory:
            letter_amnt = len(content['content'])
            current_letters += letter_amnt
        current_tokens = current_letters // 4
        return current_tokens


    async def removeKeywords(self, reply):
        """Get rid of keywords and return a clean string"""

        def getContent(start, end, reply=reply):
            try:
                content = reply.split(start)[1].split(end)[0].strip()
                return content
            except IndexError:
                return None
            except AttributeError:
                return None

        character = getContent('[CHAR]', '[CONTENT]')
        reply = reply.split('[END]')[0].strip()


        if "[CONTENT]" in reply:
            reply = reply.split("[CONTENT]")[1].strip()
        else:
            # Typically this means that the model didnt return a proper content field
            reply = "ERROR"

        return reply, character




    async def checkForContextLimit(self, system_prompt_offset=1300, contains_system_prompt=False):
        """Estimates the amount of tokens in the chathistory.
        If the max context window for an LLM is set to (for eg.) 1024 then if the tokens
        exceed that amount, the start of the chathistory will be deleted.
        
        Both the user message and the assistant message.

        Args:
            system_prompt_offset -- estimated tokens in the system prompt, the history deleter
                            will take this value into consideration when deleting up to 
                            the max tokens. eg. if the max context window is 1024, and
                            your system_prompt_offset is 40, once your current_tokens passes 984,
                            it will begin to delete messages.
            
            contains_system_prompt -- Determines if the first index should be deleted or skipped
                                    (which would typically be the system prompt)
        """

        delete_pos = 1 if contains_system_prompt else 0
        current_tokens = self.count_tokens
        model_set = None
        if self.chat_model in Configs().getChatModelInfo["openai"]:
            model_set = "openai"
        if self.chat_model in Configs().getChatModelInfo["groq"]:
            model_set = "groq"
        if self.chat_model in Configs().getChatModelInfo["ollama"]:
            model_set = "ollama"
        max_tokens = int(Configs().getChatModelInfo[model_set][str(self.chat_model)]["context_win"])

        print(f"max_tokens: {max_tokens}\ndel_pos: {delete_pos}\ncurrent_tokens: {current_tokens} ")
        # Continues to delete the chat from the top if
        # The current_tokens is still greater than max_tokens
        while (current_tokens) >= max_tokens - system_prompt_offset:
            self.chathistory.pop(0 + delete_pos)
            self.chathistory.pop(1 + delete_pos)
            with open(f"{self.bot.PATH}/data/{self.channel_id}.json", 'w') as f:
                json.dump(self.chathistory, f, indent=2)
            print("***POPPED 2 MESSAGES***")
            current_tokens = self.count_tokens




    async def checkForError(self, reply):
        """If An error happened with the API, return the Error"""
        try:
            if reply[0] == False:
                false_return = reply[0]
                error_message = reply[1]
                return false_return, error_message
        except TypeError:
            return False



    async def modelChoices(self, prompt):
        groq = Configs().getChatModelInfo["groq"]
        openai = Configs().getChatModelInfo["openai"]
        ollama = Configs().getChatModelInfo["ollama"]

        if self.chat_model in groq:
            return await TextModel().getGroq(prompt=prompt, modelName=self.chat_model)
        elif self.chat_model in openai:
            return await TextModel().getGPT(prompt=prompt, modelName=self.chat_model)
        elif self.chat_model in ollama:
            return await TextModel().getLLM(prompt=prompt, modelName=self.chat_model)




    async def AIResponse(self, userInput):
        """Gets ai generated text based off given prompt"""
        # Log user input
        with open(f"{self.bot.PATH}/data/{self.channel_id}.json", 'r') as f:
            self.chathistory = json.load(f)
        self.chathistory.append({"role": "user", "content": userInput })

        # Make sure the user's msg doesn't go over the context window
        await self.checkForContextLimit()
        examples = Info().getExamplePrompts[f"gpt4"]
        contextAndUserMsg = examples + self.chathistory

        response = await self.modelChoices(contextAndUserMsg)

        # If An error happened with the API, return the Error
        check_error = await self.checkForError(response)
        if check_error:
            return check_error[0], check_error[1]

        reply, character = await self.removeKeywords(response)

        if reply == "ERROR":
            self.chathistory.pop(-1)
            print(f"> ERROR: Model didn't return a proper response, generated response: {response}")

        elif reply != "ERROR":
            # Log AI input
            self.chathistory.append({"role": "assistant", "content": response})

        with open(f"{self.bot.PATH}/data/{self.channel_id}.json", 'w') as f:
            json.dump(self.chathistory, f, indent=2)
        return reply, character






class Tools:

    def __init__(self, bot):
        self.bot = bot
        

    async def resetChatHistory(self, channel_id):
        """Reset the chat history"""
        try:
            with open(f"{self.bot.PATH}/data/{channel_id}.json", 'w') as f:
                json.dump([], f, indent=2)
            return True
        except:
            return False


    async def whitelistSetup(self, whitelist, value):
        """Add channel ID to a whitelist"""
        whitelist["channels"].append(value)
        with open(self.bot.PATH + "/data/whitelist.json", "w") as f:
            json.dump(whitelist, f, indent=2)


    async def whitelistRemove(self, whitelist, value):
        """Remove channel ID from a whitelist"""
        try:
            whitelist["channels"].remove(value)
            with open(self.bot.PATH + "/data/whitelist.json", "w") as f:
                json.dump(whitelist, f, indent=2)
        except ValueError:
            return False
        return True


    async def hasProfanity(self, text):
        """Returns true if inappropriate text is detected"""
        ai_result = await TextModel().hasProfanity(text)
        return ai_result


    async def filterWords(self, text):
        """Remove special characters"""
        not_allowed = ["/", "`", "\\", "$", ";", "{", "}", "#", "@", "%", "&", "^", "|", "["]
        for i in not_allowed:
            text = text.replace(i, '')
        return text