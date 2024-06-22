from utils.data import Info, Configs
from utils.ai_tools import TextModel
import json


class AIManager():

    def __init__(self, bot, channel_id, chat_model, chathistory):
        self.bot = bot
        self.channel_id = channel_id
        self.chat_model = chat_model
        self.chathistory = chathistory
        self.tools = Tools(self.bot)



    @property
    def count_tokens(self):
        current_tokens = 0
        for content in self.chathistory:
            words_amnt = len(content['content'].split())
            current_tokens += words_amnt
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
        reply = reply.split('[END]')[0]


        if "[CONTENT]" in reply:
            reply = reply.split("[CONTENT]")[1].strip()
        else:
            # Typically this means that the model didnt return a proper content field
            reply = "ERROR"

        return reply, character




    async def checkForContextLimit(self, range=40, contains_system_prompt=False):
        """Estimates the amount of tokens in the chathistory.
        If the max context window for an LLM is set to (for eg.) 1024 then if the tokens
        exceed that amount, the start of the chathistory will be deleted.
        
        Both the user message and the assistant message.

        Args:
            range -- the amount of words it will take before clearing up the chat. eg.
                    if the max context window is 1024, with a range of 40 and the current
                    context of the chathistory is >= 984 then it will delete the chat (first 2 msgs or more)
                    once the current tokens reach 984 or higher.
            
            contains_system_prompt -- Determines if the first index should be deleted or skipped
                                    (which would typically be the system prompt)
        """
        parent_model = "openai"
        checkForLLM = True
        for model in Configs().getChatModelInfo["openai"]:
            if self.chat_model == model:
                parent_model = "openai"
                checkForLLM = False
                break
        for model in Configs().getChatModelInfo["groq"]:
            if self.chat_model == model:
                parent_model = "groq"
                checkForLLM = False
                break
        max_tokens = Configs().getChatModelInfo["num_ctx"] if checkForLLM else int(Configs().getChatModelInfo[parent_model][str(self.chat_model)]["context_win"])
        delete_pos = 0 if contains_system_prompt == False else 1
        current_tokens = self.count_tokens

        # Continues to delete the chat from the top if
        # The current_tokens is still greater than max_tokens
        while (current_tokens) >= max_tokens - range:
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

        if self.chat_model in groq:
            return await TextModel().getGroq(prompt=prompt)
        elif self.chat_model in openai:
            return await TextModel().getGPT(prompt=prompt)
        else:
            return await TextModel().getLLM(prompt=prompt)




    async def AIResponse(self, userInput):
        """Gets ai generated text based off given prompt"""
        # Log user input
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

        # Log AI input
        self.chathistory.append({"role": "assistant", "content": response})

        with open(f"{self.bot.PATH}/data/{self.channel_id}.json", 'w') as f:
            json.dump(self.chathistory, f, indent=2)
        return reply, character






class Tools:

    def __init__(self, bot):
        self.bot = bot
        

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
        not_allowed = ["/", "`", "\\", "$", ";", "\"", "'", "{", "}", "#", "@", "%", "&", "*", "^", "|"]
        for i in not_allowed:
            text = text.replace(i, '')
        return text