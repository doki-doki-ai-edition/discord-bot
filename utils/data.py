import os
import json

THIS_PATH = os.path.dirname(os.path.realpath(__file__))
PATH = os.path.dirname(THIS_PATH)

class Data:
    def __init__(self):
        pass




class Configs:
    @property
    def config(self):
        with open(f'{PATH}/config.json', 'r') as f:
            config = json.load(f)
        return config


    @property
    def getChatModelInfo(self):
        with open(f'{PATH}/assets/configs/chat_model_info.json', 'r') as f:
            chat_model_info = json.load(f)
        return chat_model_info


    def setChatModelInfo(self, chat_model_info):
        with open(f'{PATH}/assets/configs/chat_model_info.json', 'w') as f:
            json.dump(chat_model_info, f, indent=4)


    def setChatModelTemperature(self, model_family, chat_model, temperature):
        chat_model_info = self.getChatModelInfo
        chat_model_info[model_family][chat_model]["temperature"] = temperature
        self.setChatModelInfo(chat_model_info=chat_model_info)


    def getModelFamilyFromModel(self, chat_model):
        for model_family in ["openai", "groq", "ollama"]:
            models = Configs().getChatModelInfo[model_family]
            if chat_model in models:
                return model_family
        return False




class Info:
    @property
    def getDokis(self):
        with open(PATH + "/assets/info/dokis.json", "r") as f:
            dokis = json.load(f)
        return dokis
    
    @property
    async def getHelpInfo(self):
        with open(PATH +'/assets/info/cmds.json', 'r') as f:
            desc = json.load(f)
        return desc
    
    @property
    def getExamplePrompts(self):
        with open(PATH + "/assets/prompts/prompt_template.json", "r") as f:
            example = json.load(f)
        return example
    
    @property
    def getReminder(self):
        with open(PATH + "/assets/info/reminder.json", "r") as f:
            reminder = json.load(f)
        return reminder
    
    @property
    async def getWhitelist(self):
        try:
            with open(PATH + "/data/whitelist.json", "r") as f:
                whitelist = json.load(f)
        except FileNotFoundError:
            default_whitelist = {
                "channels": []
            }

            with open(PATH + f"/data/whitelist.json", "w") as f:
                json.dump(default_whitelist, f, indent=2)
            with open(PATH + f"/data/whitelist.json", "r") as f:
                whitelist = json.load(f)
        return whitelist
    



class Misc:
    @property
    async def getDummyText(self):
        with open(f'{PATH}/assets/misc/dummy_msgs.json') as f:
            misc = json.load(f)
        return misc